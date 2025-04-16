import requests
from flask import Flask, request, jsonify, redirect

APP_ID = "9526502094075634"
APP_SECRET = "f0d6474c10466f47d5a40146c682e7b7"
REDIRECT_URI = "https://api-social-sd6m.onrender.com/callback/instagram" 
SCOPE = "instagram_basic,pages_show_list"


# URL para login do Instagram (com OAuth)
AUTH_URL = f"https://www.facebook.com/v22.0/dialog/oauth?client_id={APP_ID}&redirect_uri={REDIRECT_URI}&scope={SCOPE}&response_type=code"

# Armazenamento temporário do token (em produção, use Redis ou banco de dados)
user_tokens = {}

def instagram():
    # Retorna a URL para o frontend em vez de abrir o navegador
    return jsonify({"auth_url": AUTH_URL})

def instagramCallback():
    # Captura o código de autorização
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "Código de autorização não fornecido"}), 400
    
    # Troca o código por um token de acesso
    access_token = get_access_token(code)
    if not access_token:
        return jsonify({"error": "Falha ao obter token de acesso"}), 400
    
    # Obtém o ID do usuário
    user_id, user_name = get_user_id(access_token)
    if not user_id:
        return jsonify({"error": "Falha ao obter ID do usuário"}), 400
    
    
    # Redireciona para o frontend com o ID do usuário como parâmetro
    return redirect(f"http://localhost:8080/auth-success?media=instagram&user_id={user_id}&username={user_name}&token={access_token}")


# def userExists():
#     # Endpoint para o frontend verificar se o usuário está autenticado
#     user_id = request.args.get("user_id")
#     if user_id in user_tokens:
#         return jsonify({"user_id": user_id})
#     return jsonify({"error": "Usuário não autenticado"}), 401

def get_access_token(code):
    url = "https://graph.facebook.com/v22.0/oauth/access_token"

    params = {
        "client_id": APP_ID,
        "client_secret": APP_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": code,
    }

    response = requests.get(url, params=params)
    data = response.json()
    
    if "error" in data:
        print(f"Erro ao obter o access token: {data['error']['message']}")
        return None

    return data.get("access_token")

def get_user_id(access_token):
    url = "https://graph.facebook.com/v22.0/me"
    params = {
        "fields": "id,name", 
        "access_token": access_token
    }

    response = requests.get(url, params=params)
    user_data = response.json()

    if "error" in user_data:
        print(f"Erro ao obter ID do usuário: {user_data['error']['message']}")
        return None

    return user_data.get("id"), user_data.get("name")
