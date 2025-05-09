from flask import  request, jsonify
import requests
from flask import Blueprint
from instagram.utils.api_request import making_request

instagram_post_routes = Blueprint('instagram', __name__)

# Função para criar o media container
def create_media_container(ACCESS_TOKEN, MEDIA, CAPTION, CAROUSEL):    
    medias_ids = []

    if not ACCESS_TOKEN and not MEDIA and not CAPTION and not CAROUSEL:
        return jsonify({"error": "instagramToken e media são obrigatórios."}), 400
    
    for i in MEDIA:
        EXTENSION = MEDIA[i].split('.')[-1].lower()

        print(f"📥 Media URL recebida: {MEDIA[i]}")

        url = f"https://graph.facebook.com/v22.0/17841472937904147/media"
        params = {
            "access_token": ACCESS_TOKEN,
        }

        if(CAROUSEL == True):
            params["is_carousel_item"] = True
        else:
            params["is_carousel_item"] = False
            params["caption"] = CAPTION


        if EXTENSION == 'mp4':
            params["video_url"] = MEDIA[i]
            params["media_type"] = "REELS"
            print(f"🎥 Vídeo detectado")

        elif EXTENSION in ('jpg', 'jpeg'):
            params["image_url"] = MEDIA[i]
            print(f"🖼️ Imagem detectada")
        else:
            return jsonify({"error": f"Extensão de mídia não suportada: {EXTENSION}"}), 400

        medias_ids.append(making_request(url, params))

    if (CAROUSEL == True):
        url = f"https://graph.facebook.com/v22.0/17841472937904147/media"
        params = {
            "caption": CAPTION,
            "media_type": "CAROUSEL",
            "children": ",".join(medias_ids),
            "access_token": ACCESS_TOKEN
        }

        return making_request(url, params)
    else:
        return medias_ids[0]

def create_instagram_media():
    data = request.get_json()
    access_token = data.get("access_token")
    media = data.get("media")
    caption = data.get("caption")
    carousel = False

    if not all([access_token, media, caption]):
        return jsonify({"error": "access_token, media e caption são obrigatórios."}), 400
    
    if len(media) > 1:
        carousel = True

    media_id = create_media_container(access_token, media, caption, carousel)

    if isinstance(media_id, tuple):  # erro
        return media_id

    return jsonify({
        "media_id": media_id
    }), 202

def check_instagram_media_status():
    media_id = request.args.get("media_id")
    access_token = request.args.get("access_token")

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