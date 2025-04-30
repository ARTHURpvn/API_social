from flask import  request, jsonify
import time, requests

def create_media_container():
    data = request.get_json()
    ACCESS_TOKEN = data.get('instagramToken')
    MEDIA = data.get('media')
    TYPE = data.get('type')
    CAPTION = data.get('caption')
    
    if not ACCESS_TOKEN or not MEDIA:
        return jsonify({"error": "instagramToken and media are required."}), 400
    
    print(f"Media URL received: {MEDIA}")
    
    url = f"https://graph.facebook.com/v22.0/17841472937904147/media&caption={CAPTION}"
    params = {
        "access_token": ACCESS_TOKEN
    }

    # Define o parâmetro correto de acordo com o tipo detectado
    if TYPE in ['REELS']:
        params["video_url"] = MEDIA
        print("Using video_url parameter")
    elif TYPE == 'IMAGE':
        params["image_url"] = MEDIA
        print("Using image_url parameter")
    else:
        return jsonify({"error": f"Unsupported media type: {TYPE}"}), 400

    # Faz a requisição ao endpoint do Graph API
    try:
        response = requests.post(url, params=params, timeout=60)
        
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
def publish_instagram_post():
    try:
        data = request.get_json()

        access_token = data.get("access_token")
        media_id = data.get("media_id")

        if not all([ access_token, media_id]):
            return jsonify({"error": "instagram_account_id, access_token e media_id são obrigatórios"}), 400

        publish_url = (
            f"https://graph.facebook.com/v22.0/17841472937904147/media_publish"
            f"?creation_id={media_id}&access_token={access_token}"
        )
        header = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }

        response = requests.post(publish_url, headers=header)
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
        return jsonify({"error": "Erro interno no servidor", "details": str(e)}), 500