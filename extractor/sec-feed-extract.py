import csv
import feedparser
import time
import configparser
from pathlib import Path
import os
from groq import Groq
import logging
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv(Path(__file__).parent / '.env')

# Set up logging directory and file
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)

# Create log files with timestamps
feed_log_file = log_dir / f'sec_feed_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
feed_data_file = log_dir / f'feed_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(feed_log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Define the Notion API configuration
NOTION_API_TOKEN = os.getenv('NOTION_API_TOKEN')
SOURCE_DATABASE_ID = "2027677d888a807ba4c4c2496f90a340"
HEADERS = {
    "Authorization": f"Bearer {NOTION_API_TOKEN}",
    "Notion-Version": "2022-02-22",
    "Content-Type": "application/json"
}

# Configuration
FileConfig = configparser.ConfigParser()
ConfigurationFilePath = 'Config.txt'
feed_csv_path = Path('Feed.csv')
options = type('', (), {})()
options.Debug = False

# Statistics tracking
stats = {
    'processed_items': 0,
    'successful_items': 0,
    'failed_items': 0,
    'source_count': {},
    'source_link_count': {},
    'errors': []
}

# Define the system prompt for Groq
prompt = """You are a social media content creator specialized in LinkedIn posts for IT professionals.\n\nYour task is to:\n1. Write a LinkedIn post of up to 1000 characters based on the article below, focusing on Linux, DevOps, CI/CD, Unix, AIX, Solaris, and related technologies.\n2. The post should be clear, concise, and highlight the main insights, tips, or news from the article.\n3. Always include a practical and real-world example related to the topic. If the topic is about Linux, DevOps, or similar, prefer to use a relevant command-line example (e.g., a shell command, script, or config snippet). If the article is just news, provide a contextual example or scenario.\n4. End the post with a thought-provoking question to engage the audience.\n5. Use a professional yet approachable tone, and make the post engaging for IT and tech audiences.\n6. Optimize the post for SEO and LinkedIn engagement.\n7. At the end of the post, add 3-5 relevant hashtags (in English) that match the article's topic (e.g., #Linux, #DevOps, #Cloud, #SysAdmin, #Automation, #CI/CD, #Unix, #AIX, #Solaris, etc).\n\nIMPORTANT: Do not explain your reasoning. Do not include any thoughts, explanations, or step-by-step. Only output the LinkedIn post and hashtags in the format below. Do not include <think> or any other commentary.\n\nFormat your response exactly like this:\nPOST:\n[Your LinkedIn post here]\n\nHASHTAGS:\n[#hashtag1, #hashtag2, #hashtag3, ...]\n"""

# Função para sanitizar o conteúdo para LinkedIn e redes sociais
def sanitize_for_linkedin(content):
    # Remove blocos de código markdown
    content = re.sub(r"```[a-zA-Z]*\\n([\s\S]*?)```", lambda m: '💻 `' + m.group(1).replace('\n', ' ') + '`', content)
    content = re.sub(r"```([\s\S]*?)```", lambda m: '💻 `' + m.group(1).replace('\n', ' ') + '`', content)
    # Comandos inline
    content = re.sub(r"`+([^`]+)`+", r"💻 `\1`", content)
    # Listas não numeradas
    content = re.sub(r"^\s*[-*]\s+", "• ", content, flags=re.MULTILINE)
    # Listas numeradas (1. 2. ...)
    def num_marker(m):
        num = m.group(1)
        emoji_nums = {'1':'1️⃣','2':'2️⃣','3':'3️⃣','4':'4️⃣','5':'5️⃣','6':'6️⃣','7':'7️⃣','8':'8️⃣','9':'9️⃣','0':'0️⃣'}
        return emoji_nums.get(num, num) + ' '
    content = re.sub(r"^\s*([0-9])\.\s+", num_marker, content, flags=re.MULTILINE)
    # Emojis no início de parágrafo
    content = re.sub(r"(^|\n)([A-Za-z])", r"\1👉 \2", content)
    # Remove espaços extras no início/fim de linhas
    content = '\n'.join([line.strip() for line in content.splitlines()])
    # Remove múltiplas quebras de linha seguidas
    content = re.sub(r"(\n\s*){2,}", "\n", content)
    # Adiciona separador visual entre parágrafos longos
    content = re.sub(r"(\n)([^\n]{80,})(\n)", r"\1\2\n—\n", content)
    # Remove espaços extras
    content = re.sub(r" +", " ", content)
    return content.strip()

def log_feed_stats():
    """Log feed processing statistics"""
    logger.info(f"\n{'='*50}")
    logger.info("Feed Processing Statistics:")
    logger.info(f"Total processed items: {stats['processed_items']}")
    logger.info(f"Successful items: {stats['successful_items']}")
    logger.info(f"Failed items: {stats['failed_items']}")
    
    logger.info("\nSource counts:")
    for source, count in sorted(stats['source_count'].items()):
        logger.info(f"- {source}: {count} entries found, {stats['source_link_count'].get(source, 0)} processed")
    
    if stats['errors']:
        logger.info("\nErrors encountered:")
        for error in stats['errors']:
            logger.error(error)
    logger.info(f"{'='*50}\n")

def create_notion_page(short_title, summary, keywords, date, source, link):
    """Create a page in Notion with error handling and logging"""
    try:
        url = "https://api.notion.com/v1/pages"
        # Extrair apenas o texto entre POST: e HASHTAGS:
        post = ""
        hashtags = []
        if "POST:" in summary and "HASHTAGS:" in summary:
            post_part = summary.split("POST:",1)[1]
            post = post_part.split("HASHTAGS:",1)[0].strip()
            hashtags_str = post_part.split("HASHTAGS:",1)[1].strip()
            hashtags = [tag.strip().replace("#","").replace(",","") for tag in hashtags_str.replace("["," ").replace("]"," ").split() if tag.strip()]
        else:
            post = summary.strip()
        # Remover qualquer bloco <think> do início do post e prefixos indesejados
        def clean_post_start(text):
            # Remove prefixos como POST:, POST, <think>, THINK:, etc. do início
            text = text.strip()
            # Regex para remover múltiplos prefixos indesejados no início
            pattern = r'^(POST:?|<think>|THINK:?|\*\*POST:?\*\*|\*POST:?\*|\*\*POST\*\*|POST |POST:|POST-|POST_|POST—|POST–|POST—|POST–|POST:)+' \
                      r'\s*'
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
            # Se ainda começar com <think>, remove novamente
            while text.lower().startswith('<think>'):
                text = text[7:].strip()
            return text.strip()
        post = clean_post_start(post)
        # SANITIZAR O POST PARA LINKEDIN
        post = sanitize_for_linkedin(post)
        # Melhorar extração de hashtags
        def extract_hashtags(post, hashtags_str):
            hashtags = []
            # 1. Tentar extrair do bloco HASHTAGS
            if hashtags_str:
                hashtags = [tag.strip().replace("#","").replace(",","") for tag in hashtags_str.replace("["," ").replace("]"," ").split() if tag.strip() and tag.startswith("#") or tag.isalnum()]
            # 2. Se não encontrar, procurar hashtags no post inteiro
            if not hashtags:
                hashtags = re.findall(r'#(\w+)', post)
            # 3. Se ainda não encontrar, extrair palavras-chave do post
            if not hashtags:
                stopwords = set(['the','a','an','and','or','for','to','of','in','on','with','is','are','at','by','as','from','that','this','it','be','has','have','was','were','but','if','so','do','can','will','just','your','you','we','i','my','our','their','they','he','she','his','her','its','not','more','all','any','new','how','why','what','when','where','which','who','about','into','out','up','down','over','under','after','before','then','than','too','very','also','only','each','other','such','these','those','may','should','could','would','must','been','being','did','does','had','having','make','made','get','got','use','used','using','like','see','even','many','much','most','some','no','yes','one','two','three','first','last','next','now','today','tomorrow','yesterday'])
                words = re.findall(r'\b\w{4,}\b', post.lower())
                keywords = [w.capitalize() for w in words if w not in stopwords]
                hashtags = list(dict.fromkeys(keywords))[:3]
            # 4. Se ainda não houver, usar tags genéricas
            if not hashtags:
                hashtags = ['Tech','IT','DevOps']
            return hashtags
        hashtags = extract_hashtags(post, hashtags_str if 'hashtags_str' in locals() else '')
        # Preencher keywords com as hashtags
        keywords_str = ", ".join([f"#{tag}" for tag in hashtags])
        data = {
            "parent": {"database_id": SOURCE_DATABASE_ID},
            "properties": {
                "Edition": {
                    "title": [{"text": {"content": short_title}}]
                },
                "Created time": {"date": {"start": date}},
                "Source": {"select": {"name": source}},
                "Content": {
                    "rich_text": [
                        {"text": {"content": post}, "annotations": {"bold": True}},
                        {"text": {"content": f"\nRead more: {link}"}}
                    ]
                },
                "Tags": {"multi_select": [{"name": tag} for tag in hashtags if tag]},
                "Keywords": {"rich_text": [{"text": {"content": keywords_str}}]},
                "flow_status": {"multi_select": [{"name": "NOT STARTED"}]}
            }
        }
        logger.debug(f"Sending request to Notion API for page creation:\n{json.dumps(data, indent=2)}")
        response = requests.post(url, headers=HEADERS, json=data)
        if response.status_code == 200:
            logger.info(f"Successfully created Notion page: {short_title}")
            logger.debug(f"Notion API Response: {response.json()}")
            stats['successful_items'] += 1
        else:
            error_msg = f"Failed to create Notion page: {response.status_code} - {response.text}"
            logger.error(error_msg)
            logger.debug(f"Failed request data: {json.dumps(data, indent=2)}")
            stats['errors'].append(error_msg)
            stats['failed_items'] += 1
    except Exception as e:
        error_msg = f"Error creating Notion page: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"Exception details:", exc_info=True)
        stats['errors'].append(error_msg)
        stats['failed_items'] += 1

def save_raw_feed_content(RssItem, NewsFeed, feed_dir='raw_feeds'):
    """Save the raw feed content to a text file for inspection"""
    try:
        # Create directory for raw feeds if it doesn't exist
        feed_dir = Path(feed_dir)
        feed_dir.mkdir(exist_ok=True)
        
        # Create a filename based on the feed name and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = feed_dir / f"{RssItem[1].lower().replace(' ', '_')}_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Feed: {RssItem[1]}\n")
            f.write(f"URL: {RssItem[0]}\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Number of entries: {len(NewsFeed.entries)}\n")
            f.write("="*50 + "\n\n")
            
            for i, entry in enumerate(NewsFeed.entries, 1):
                f.write(f"Entry {i}:\n")
                f.write(f"Title: {entry.get('title', 'No title')}\n")
                f.write(f"Link: {entry.get('link', 'No link')}\n")
                f.write(f"Published: {entry.get('published', 'No date')}\n")
                f.write(f"Summary: {entry.get('summary', 'No summary')}\n")
                f.write("-"*50 + "\n\n")
        
        logger.info(f"Raw feed content saved to {filename}")
        return filename
    except Exception as e:
        logger.error(f"Error saving raw feed content for {RssItem[1]}: {e}")
        return None

def GetRssFromUrl(RssItem):
    try:
        # Skip commented out feeds
        if RssItem[0].startswith('#'):
            logger.info(f"Skipping commented feed: {RssItem[1]}")
            return

        logger.info(f"\n{'='*50}")
        logger.info(f"Processing feed: {RssItem[1]} ({RssItem[0]})")
        
        NewsFeed = feedparser.parse(RssItem[0])
        logger.info(f"Found {len(NewsFeed.entries)} entries in feed")
        
        # Save raw feed content
        raw_feed_file = save_raw_feed_content(RssItem, NewsFeed)
        if raw_feed_file:
            logger.info(f"Raw feed content saved to: {raw_feed_file}")
        
        # Handle bozo errors more gracefully
        if NewsFeed.bozo and NewsFeed.bozo_exception:
            if "XML or text declaration not at start of entity" in str(NewsFeed.bozo_exception):
                logger.warning(f"Feed {RssItem[1]} has XML declaration issue but is still parseable")
            elif "is not an XML media type" in str(NewsFeed.bozo_exception):
                logger.warning(f"Feed {RssItem[1]} has content type issue but is still valid XML")
            elif "document declared as us-ascii" in str(NewsFeed.bozo_exception):
                logger.warning(f"Feed {RssItem[1]} has encoding mismatch but content is still valid")
            else:
                logger.error(f"Feed parsing error for {RssItem[1]}: {NewsFeed.bozo_exception}")
                stats['errors'].append(f"Feed parsing error for {RssItem[1]}: {NewsFeed.bozo_exception}")
                return

        # Count total entries for this source
        stats['source_count'][RssItem[1]] = len(NewsFeed.entries)
        logger.info(f"Processing {len(NewsFeed.entries)} entries for {RssItem[1]}")

        # Calcular o corte de 14 dias atrás
        seven_days_ago = datetime.utcnow() - timedelta(days=14)

        for RssObject in reversed(NewsFeed.entries):
            try:
                # Try multiple date fields
                date_fields = ['published_parsed', 'updated_parsed', 'created_parsed']
                date_parsed = None
                for field in date_fields:
                    if hasattr(RssObject, field) and getattr(RssObject, field):
                        date_parsed = getattr(RssObject, field)
                        logger.debug(f"Found date in {field} field")
                        break
                if date_parsed:
                    DateActivity = time.strftime('%Y-%m-%dT%H:%M:%S', date_parsed)
                    dt_obj = datetime(*date_parsed[:6])
                else:
                    # If no parsed date available, try string fields
                    string_fields = ['published', 'updated', 'created']
                    for field in string_fields:
                        if hasattr(RssObject, field) and getattr(RssObject, field):
                            DateActivity = getattr(RssObject, field)
                            try:
                                dt_obj = datetime.strptime(DateActivity[:19], '%Y-%m-%dT%H:%M:%S')
                            except Exception:
                                dt_obj = datetime.utcnow()
                            logger.debug(f"Using string date from {field} field")
                            break
                    else:
                        # If no date found, use current time
                        DateActivity = time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime())
                        dt_obj = datetime.utcnow()
                        logger.warning(f"No date found for entry, using current time")

                # FILTRO: só processar notícias dos últimos 14 dias
                if dt_obj < seven_days_ago:
                    logger.info(f"Skipping entry older than 14 days: {DateActivity}")
                    continue

            except (AttributeError, TypeError) as e:
                logger.warning(f"Unable to parse date for RSS entry in feed {RssItem[1]}: {e}")
                continue

            try:
                TmpObject = FileConfig.get('Rss', RssItem[1])
            except configparser.NoOptionError:
                FileConfig.set('Rss', RssItem[1], "?")
                TmpObject = "?"
                logger.info(f"Created new feed entry for {RssItem[1]}")

            if TmpObject.endswith("?") or TmpObject < DateActivity:
                FileConfig.set('Rss', RssItem[1], DateActivity)
                stats['processed_items'] += 1
                if RssItem[1] not in stats['source_link_count']:
                    stats['source_link_count'][RssItem[1]] = 0
                stats['source_link_count'][RssItem[1]] += 1
                try:
                    title = RssObject.title if hasattr(RssObject, 'title') else 'No title'
                    link = RssObject.link if hasattr(RssObject, 'link') else ''
                    description = RssObject.summary if hasattr(RssObject, 'summary') else ''
                    logger.info(f"\nProcessing article: {title}")
                    logger.debug(f"Original description: {description[:200]}...")
                    # Call Groq API for content enhancement
                    client = Groq(api_key=os.getenv('GROQ_API_KEY'))
                    retry_count = 0
                    while True:
                        try:
                            chat_completion = client.chat.completions.create(
                                messages=[
                                    {"role": "system", "content": prompt},
                                    {"role": "user", "content": f"Title: {title}\nDescription: {description}"}
                                ],
                                model="deepseek-r1-distill-llama-70b",
                                temperature=0.5,
                                max_tokens=500,
                                top_p=0.9
                            )
                            break
                        except Exception as e:
                            if hasattr(e, 'status_code') and e.status_code == 429:
                                wait_time = 20
                                logger.warning(f"429 Too Many Requests. Waiting {wait_time} seconds before retry...")
                                time.sleep(wait_time)
                                retry_count += 1
                                if retry_count > 5:
                                    logger.error("Max retries reached for 429 error. Skipping entry.")
                                    raise
                            else:
                                raise
                    enhanced_description = chat_completion.choices[0].message.content
                    logger.info(f"Groq API Response:\n{enhanced_description}\n")
                    # Create Notion page if we have a token
                    if NOTION_API_TOKEN:
                        logger.info(f"Creating Notion page for: {title}")
                        create_notion_page(title, enhanced_description, '', DateActivity, RssItem[1], link)
                    else:
                        logger.warning("Skipping Notion page creation - no API token")
                    time.sleep(2)  # Delay entre requisições
                except Exception as e:
                    logger.error(f"Failed to process RSS feed entry {RssItem[1]}: {e}")
                    stats['failed_items'] += 1
                    stats['errors'].append(f"Failed to process RSS feed entry {RssItem[1]}: {e}")
            else:
                logger.debug(f"Skipping entry - already processed: {title if 'title' in locals() else 'Unknown title'}")
    except Exception as e:
        logger.error(f"Error processing feed {RssItem[1]}: {str(e)}")
        stats['errors'].append(f"Error processing feed {RssItem[1]}: {str(e)}")
        stats['failed_items'] += 1
    # Update Config.txt after processing each feed
    update_config_file()
    logger.info(f"Completed processing feed: {RssItem[1]}\n{'='*50}\n")

# Update Config.txt after processing each feed
def update_config_file():
    """Update the Config.txt file with new timestamps"""
    try:
        logger.info("Updating Config.txt with new timestamps")
        with open(ConfigurationFilePath, 'w') as FileHandle:
            FileConfig.write(FileHandle)
        logger.info("Successfully updated Config.txt")
    except Exception as e:
        logger.error(f"Error updating Config.txt: {str(e)}")

def print_notion_pages(database_id):
    """Print the list of pages in the Notion database"""
    try:
        url = f"https://api.notion.com/v1/databases/{database_id}/query"
        response = requests.post(url, headers=HEADERS)
        if response.status_code == 200:
            pages = response.json().get('results', [])
            logger.info(f"\nFound {len(pages)} pages in Notion database")
            for page in pages[:5]:  # Show only the first 5 pages
                title = page['properties'].get('Edition', {}).get('title', [{}])[0].get('text', {}).get('content', 'No title')
                logger.info(f"- {title}")
        else:
            logger.error(f"Failed to query Notion database: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Error querying Notion database: {str(e)}")

def main():
    logger.info("Starting security feed extraction")
    try:
        feeds = {}
        # Check if Feed.csv exists and print its contents
        if feed_csv_path.exists():
            logger.info(f"Feed.csv found at {feed_csv_path}")
            with open(feed_csv_path, 'r') as csvfile:
                reader = csv.reader(csvfile)
                print("Contents of Feed.csv:")
                for row in reader:
                    print(row)
                    if len(row) == 2:  # Include all rows for display
                        feeds[row[1].strip()] = {'url': row[0].strip(), 'last_update': '1900-01-01T00:00:00'}
                        stats['source_link_count'][row[1].strip()] = 0
        else:
            logger.error(f"Feed.csv file not found at {feed_csv_path}")
            return
        # Check if Config.txt exists and print its contents
        if Path(ConfigurationFilePath).exists():
            logger.info(f"Config.txt found at {ConfigurationFilePath}")
            FileConfig.read(ConfigurationFilePath)
            print("\nContents of Config.txt:")
            for section in FileConfig.sections():
                print(f"[{section}]")
                for key, value in FileConfig.items(section):
                    print(f"{key} = {value}")
        else:
            logger.info("Config.txt not found, creating new file")
            FileConfig.add_section('Rss')
        # Garantir que todos os feeds do Feed.csv estejam no Config.txt
        rss_section = 'rss' in (section.lower() for section in FileConfig.sections())
        if not rss_section:
            FileConfig.add_section('Rss')
        for name in feeds:
            if not FileConfig.has_option('Rss', name):
                FileConfig.set('Rss', name, '?')
        for line in FileConfig.options('Rss'):
            name = line.strip()
            if name not in feeds:
                logger.warning(f"Feed '{name}' from Config.txt not found in Feed.csv")
        # Process each feed
        consolidated_list = [(info['url'], name) for name, info in feeds.items()]
        for rss_item in consolidated_list:
            if not rss_item[0].startswith('#'):
                GetRssFromUrl(rss_item)
                update_config_file()
        update_config_file()
        log_feed_stats()
    except Exception as e:
        logger.error(f"Critical error in main execution: {str(e)}", exc_info=True)
    logger.info("Security feed extraction completed")

if __name__ == "__main__":
    main()
