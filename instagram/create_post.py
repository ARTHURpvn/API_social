from flask import  request, jsonify
import time, requests
from flask import Blueprint

instagram_post_routes = Blueprint('instagram', __name__)

# Função para criar o media container
def create_media_container(ACCESS_TOKEN, MEDIA, CAPTION):    
    if not ACCESS_TOKEN or not MEDIA:
        return jsonify({"error": "instagramToken e media são obrigatórios."}), 400

    EXTENSION = MEDIA.split('.')[-1].lower()

    print(f"📥 Media URL recebida: {MEDIA}")

    url = f"https://graph.facebook.com/v22.0/17841472937904147/media"
    params = {
        "access_token": ACCESS_TOKEN,
        "caption": CAPTION,
        "is_carousel_item": False
    }

    if EXTENSION == 'mp4':
        params["video_url"] = MEDIA
        params["media_type"] = "REELS"
        print(f"🎥 Vídeo detectado")

    elif EXTENSION in ('jpg', 'jpeg'):
        params["image_url"] = MEDIA
        print(f"🖼️ Imagem detectada")
    else:
        return jsonify({"error": f"Extensão de mídia não suportada: {EXTENSION}"}), 400

    try:
        response = requests.post(url, params=params, timeout=60)
        print(f"📡 Resposta da criação do container: {response.text}")
    except Exception as e:
        return jsonify({"error": f"Erro ao fazer requisição: {str(e)}"}), 501

    response_data = response.json()

    if "error" in response_data:
        return jsonify({"error": f"Erro da API: {response_data['error']}"}), 400

    if "id" in response_data:
        return response_data["id"]
    else:
        return jsonify({"error": f"Resposta inesperada: {response_data}"}), 400


# Passo 3: Publicar a mídia no Instagram
    
def create_instagram_media():
    data = request.get_json()
    access_token = data.get("access_token")
    media = data.get("media")
    caption = data.get("caption")

    if not all([access_token, media, caption]):
        return jsonify({"error": "access_token, media e caption são obrigatórios."}), 400

    media_id = create_media_container(access_token, media, caption)

    if isinstance(media_id, tuple):  # erro
        return media_id

    return jsonify({
        "media_id": media_id
    }), 202

def check_instagram_media_status():
    data = request.get_json()
    media_id = data.get("media_id")
    access_token = data.get("access_token")

    if not all([media_id, access_token]):
        return jsonify({"error": "media_id e access_token são obrigatórios."}), 400

    url = f"https://graph.facebook.com/v22.0/{media_id}?fields=status_code&access_token={access_token}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return jsonify({"status": data.get("status_code")})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

def publish_instagram():
    data = request.get_json()
    access_token = data.get("access_token")
    media_id = data.get("media_id")

    if not all([access_token, media_id]):
        return jsonify({"error": "access_token e media_id são obrigatórios."}), 400

    url = f"https://graph.facebook.com/v22.0/17841472937904147/media_publish"
    params = {
        "creation_id": media_id,
        "access_token": access_token
    }

    try:
        response = requests.post(url, params=params)
        response.raise_for_status()
        data = response.json()
        return jsonify({"status": "success", "post_id": data.get("id")})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500