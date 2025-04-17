from flask import  request, jsonify
import time, requests

def create_media_container():
    data = request.get_json()
    ACCESS_TOKEN = data.get('instagramToken')
    MEDIA = data.get('media')
    
    if not ACCESS_TOKEN or not MEDIA:
        return jsonify({"error": "instagramToken and media are required."}), 400

    # Verifica se o tipo foi enviado explicitamente
    explicit_type = data.get('type')
    
    print(f"Media URL received: {MEDIA}")
    
    # Verifica se a URL está acessível e pega o Content-Type
    try:
        head_response = requests.head(MEDIA, allow_redirects=True, timeout=10)
        print(f"Media URL head response: Status {head_response.status_code}")
        
        if head_response.status_code != 200:
            return jsonify({"error": f"Media URL returned status {head_response.status_code}"}), 400

        content_type = head_response.headers.get('Content-Type', '').lower()
        print(f"Detected Content-Type: {content_type}")
    except Exception as e:
        print(f"Exception during HEAD request: {str(e)}")
        return jsonify({"error": "Failed to access media URL."}), 400

    # Define o tipo com base no Content-Type
    if explicit_type:
        TYPE = explicit_type.upper()
        print(f"Using explicit type: {TYPE}")
    elif content_type.startswith("video/"):
        TYPE = "REELS"
        print("Detected type based on Content-Type: REELS")
    elif content_type.startswith("image/"):
        TYPE = "IMAGE"
        print("Detected type based on Content-Type: IMAGE")
    else:
        return jsonify({"error": f"Unsupported media Content-Type: {content_type}"}), 400

    url = f"https://graph.facebook.com/v22.0/17841472937904147/media"
    params = {
        "access_token": ACCESS_TOKEN
    }

    # Define o parâmetro correto de acordo com o tipo detectado
    if TYPE in ['REELS', 'VIDEO']:
        params["video_url"] = MEDIA
        print("Using video_url parameter")
    elif TYPE == 'IMAGE':
        params["image_url"] = MEDIA
        print("Using image_url parameter")
    else:
        return jsonify({"error": f"Unsupported media type: {TYPE}"}), 400

    # Faz a requisição ao endpoint do Graph API
    try:
        print(f"Sending POST request to {url} with params: {params}")
        response = requests.post(url, params=params, timeout=60)
        print(f"Status code: {response.status_code}")
        print(f"Response content: {response.text}")
    except Exception as e:
        return jsonify({"error": f"Request failed: {str(e)}"}), 500

    response_data = response.json()

    # Trata erros de API
    if "error" in response_data:
        error_message = response_data["error"].get("message", "Unknown error")
        error_code = response_data["error"].get("code", "")
        return jsonify({"error": f"API Error ({error_code}): {error_message}"}), 400

    # Retorna o ID do container criado
    if "id" in response_data:
        return jsonify({"success": True, "container_id": response_data["id"]}), 200
    else:
        return jsonify({"error": f"Unexpected response: {response_data}"}), 400
      
    
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
def publish_media(media_id, INSTAGRAM_ACCOUNT_ID, ACCESS_TOKEN):
    try:
        url = f"https://graph.facebook.com/v22.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"
        params = {
            "creation_id": media_id,
            "access_token": ACCESS_TOKEN,
        }
        response = requests.post(url, params=params)
        response.raise_for_status()
        
        data = response.json()

        if "id" in data:
            print("✅ Post publicado com sucesso! ID:", data["id"])
            return {"success": True, "post_id": data["id"]}
        else:
            raise Exception(f"Erro ao publicar post: {data}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Erro ao publicar mídia: {str(e)}")

def create_instagram_post():
    print("Received request to create_media_container")
    print(f"Request method: {request.method}")
    print(f"Request headers: {request.headers}")
    print(f"Request data: {request.get_data()}")

    try:
        data = request.json()

        # Cria o container de mídia
        media_id = create_media_container(
            data['instagram_account_id'],
            data['access_token'],
            data['media_url'],
            data['caption']
        )

        if not media_id:
            return jsonify({'error': 'Falha ao criar container de mídia'}), 500

        # Aguarda a mídia estar pronta
        if not wait_for_media_ready(media_id, data['access_token']):
            return jsonify({'error': 'Tempo esgotado ao aguardar processamento da mídia'}), 500

        # Publica a mídia
        publish_result = publish_media(
            media_id,
            data['instagram_account_id'],
            data['access_token']
        )

        return jsonify({
            'message': 'Post criado com sucesso',
            'media_id': media_id,
            'publish_result': publish_result
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
