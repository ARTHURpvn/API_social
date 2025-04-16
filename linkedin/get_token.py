from flask import request, jsonify, redirect
from dotenv import load_dotenv
import os
import requests

load_dotenv()  

client_id = os.getenv("LINKEDIN_CLIENT_ID")
client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")
state = os.getenv("STATE")


def get_user_code():
    """Abre a página de login do LinkedIn e aguarda o redirecionamento."""
    return f"https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope=openid,profile,w_member_social&state={state}"

def get_access_token(code):
    url = "https://www.linkedin.com/oauth/v2/accessToken"
    data = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "code": code,
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"Erro ao obter access token: {response.status_code}, {response.text}")
        return None


def get_profile(access_token):
    url = "https://api.linkedin.com/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    user_id = response.json().get("sub")
    user_name = response.json().get("name")
    return user_id, user_name

def linkedin():
    AUTH_URL = get_user_code()

    return jsonify({"auth_url": AUTH_URL})


def linkedinCallback():
    code = request.args.get("code")

    if not code:
        return "Erro na autenticação!", 400

    access_token = get_access_token(code)

    if not access_token:
        return "Erro ao obter o access token!", 400
    
    urn, username = get_profile(access_token)

    if not urn:
        return "Erro ao obter o urn!", 400
    
    return redirect(f"http://localhost:8080/auth-success?media=linkedin&user_id={urn}&token={access_token}&username={username}")