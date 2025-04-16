import webbrowser
import requests
import os
from create_posts import create_post_image, create_post
from get_posts import get_user_posts
import time
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()  # Carrega as variáveis do arquivo .env

client_id = os.getenv("LINKEDIN_CLIENT_ID")
client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")
state = os.getenv("STATE")

app = Flask(__name__)

@app.route('/callback')
def callback():
    """Captura o código de autorização e exibe o título da página."""
    code = request.args.get("code")
    state_received = request.args.get("state")

    if not code or state_received != state:
        return "Erro na autenticação!", 400

    access_token = get_access_token(code)

    if not access_token:
        return "Erro ao obter o access token!", 400
    
    urn = get_profile(access_token)

    if not urn:
        return "Erro ao obter o urn!", 400

    images = ["image1.jpeg"]

    # creating_post = create_post_image(urn, access_token, images)
    # get_post = get_user_posts(access_token,urn)
    # return f"<h1>{get_post}</h1>"
    



if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: app.run(port=5000, debug=False, use_reloader=False)).start()
