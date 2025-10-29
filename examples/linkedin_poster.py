#!/usr/bin/env python3
"""
LinkedIn Poster - Exemplo de código para postar no LinkedIn
"""

import requests
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class LinkedInPoster:
    """Classe para postar no LinkedIn"""
    
    def __init__(self):
        self.client_id = os.getenv('LINKEDIN_CLIENT_ID')
        self.client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
        self.redirect_uri = os.getenv('LINKEDIN_REDIRECT_URI')
        self.access_token = None
        self.profile_id = None
        
    def get_authorization_url(self):
        """Gerar URL de autorização"""
        import secrets
        state = secrets.token_urlsafe(32)
        
        auth_url = (
            f"https://www.linkedin.com/oauth/v2/authorization?"
            f"response_type=code&"
            f"client_id={self.client_id}&"
            f"redirect_uri={self.redirect_uri}&"
            f"state={state}&"
            f"scope=r_liteprofile%20w_member_social"
        )
        
        return auth_url, state
    
    def get_access_token(self, code):
        """Trocar código por Access Token"""
        url = "https://www.linkedin.com/oauth/v2/accessToken"
        
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data["access_token"]
            
            # Salvar token
            self.save_token(token_data)
            
            return self.access_token
        else:
            raise Exception(f"Erro ao obter token: {response.text}")
    
    def save_token(self, token_data):
        """Salvar token com expiração"""
        tokens = {
            "access_token": token_data["access_token"],
            "expires_at": (datetime.now() + timedelta(seconds=token_data["expires_in"])).isoformat(),
            "created_at": datetime.now().isoformat()
        }
        
        with open("linkedin_tokens.json", "w") as f:
            json.dump(tokens, f, indent=2)
    
    def load_token(self):
        """Carregar token salvo"""
        try:
            with open("linkedin_tokens.json", "r") as f:
                tokens = json.load(f)
            
            expires_at = datetime.fromisoformat(tokens["expires_at"])
            
            if datetime.now() < expires_at:
                self.access_token = tokens["access_token"]
                return True
            else:
                print("⚠️ Token expirado")
                return False
        except FileNotFoundError:
            return False
    
    def get_profile_id(self):
        """Obter ID do perfil"""
        if not self.access_token:
            raise Exception("Precisa autenticar primeiro")
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        response = requests.get(
            "https://api.linkedin.com/v2/me",
            headers=headers
        )
        
        if response.status_code == 200:
            profile = response.json()
            self.profile_id = profile["id"]
            return self.profile_id
        else:
            raise Exception(f"Erro ao obter perfil: {response.text}")
    
    def post_content(self, content, link=None):
        """Postar conteúdo no LinkedIn"""
        if not self.access_token or not self.profile_id:
            raise Exception("Precisa autenticar primeiro")
        
        url = "https://api.linkedin.com/v2/ugcPosts"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        # Adicionar link se fornecido
        if link:
            content_with_link = f"{content}\n\n🔗 Read more: {link}"
        else:
            content_with_link = content
        
        post_data = {
            "author": f"urn:li:person:{self.profile_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content_with_link
                    },
                    "shareMediaCategory": "NONE" if not link else "ARTICLE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        response = requests.post(url, headers=headers, json=post_data)
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Post publicado com sucesso!")
            return result
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"📝 Resposta: {response.text}")
            raise Exception(f"Erro na API: {response.text}")


def main():
    """Função principal"""
    print("🚀 LinkedIn Poster")
    print("=" * 50)
    
    # Criar instância
    poster = LinkedInPoster()
    
    # Tentar carregar token salvo
    if poster.load_token():
        print("✅ Token carregado")
    else:
        print("⚠️ Token não encontrado ou expirado")
        print("\n📝 Para autenticar:")
        
        auth_url, state = poster.get_authorization_url()
        print(f"\n1. Acesse: {auth_url}")
        print(f"2. Autorize o acesso")
        print(f"3. Cole o código aqui:")
        code = input("\nCódigo: ")
        
        poster.get_access_token(code)
        print("✅ Autenticado!")
    
    # Obter profile ID
    profile_id = poster.get_profile_id()
    print(f"👤 Profile ID: {profile_id}")
    
    # Exemplo de conteúdo
    content = """
🚨 Breaking: Nova vulnerabilidade crítica descoberta!

✅ Patch disponível imediatamente
📊 Ataques em escala global detectados
🔒 Mitigação urgente necessária

#Cybersecurity #InfoSec #IT
"""
    
    # Postar (descomente para postar de verdade)
    # try:
    #     result = poster.post_content(content)
    #     print(f"📊 Post ID: {result.get('id')}")
    # except Exception as e:
    #     print(f"❌ Erro: {e}")
    
    print("\n✅ Exemplo concluído!")


if __name__ == "__main__":
    main()

