from flask import  request, jsonify
import time, requests

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
      
    
def wait_for_media_ready(media_id, ACCESS_TOKEN, retries=10, delay=30):
    try:
        url = f"https://graph.facebook.com/v22.0/{media_id}?fields=status_code&access_token={ACCESS_TOKEN}"

        for _ in range(retries):
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            status = data.get("status_code")
            print(f"⏳ Status da mídia: {status}")

            if status == "FINISHED":  
                print("✅ Mídia pronta para publicação!")
                return True
            time.sleep(delay)

        print("❌ Tempo esgotado! A mídia ainda não está pronta.")
        return False
    except requests.exceptions.RequestException as e:
        raise Exception(f"Erro ao verificar status da mídia: {str(e)}")


# Passo 3: Publicar a mídia no Instagram
def publish_instagram_post():
    try:
        data = request.get_json()

        access_token = data.get("access_token")
        media = data.get("media")
        caption = data.get("caption")

        if not all([access_token, media, caption]):
            return jsonify({"error": "access_token, media e caption são obrigatórios."}), 400

        media_id = create_media_container(access_token, media, caption)
        
        # Verifica se houve erro na criação
        if isinstance(media_id, tuple):  # é um (jsonify, status_code)
            return media_id

        if not wait_for_media_ready(media_id, access_token):
            return jsonify({"error": "Tempo esgotado! A mídia ainda não está pronta."}), 400

        publish_url = f"https://graph.facebook.com/v22.0/17841472937904147/media_publish"
        params = {
            "creation_id": media_id,
            "access_token": access_token
        }
        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(publish_url, headers=headers, params=params)
        response_data = response.json()

        if response.status_code != 200:
            return jsonify({
                "error": "Erro ao publicar mídia",
                "facebook_response": response_data
            }), response.status_code

        return jsonify({
            "status": "success",
            "post_id": response_data.get("id")
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Erro interno no servidor", "details": str(e)}), 500