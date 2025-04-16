from flask import jsonify
import requests
from flask import  request, jsonify
import time

def create_media_container():
    data = request.get_json()
    TYPE = data.get('type', 'IMAGE')  # Default to IMAGE if not specified
    ACCESS_TOKEN = data.get('instagramToken')
    MEDIA = data.get('media')

    try:
        url = f"https://graph.facebook.com/v22.0/17841472937904147/media"
        params = {
            "access_token": ACCESS_TOKEN
        }
        
        # Add the correct parameter based on media type
        if TYPE == 'REELS' or TYPE == 'VIDEO':
            params["video_url"] = MEDIA
        else:  # TYPE == 'IMAGE'
            params["image_url"] = MEDIA
            
        # Make the request and capture the full response
        response = requests.post(url, params=params)
        
        # Print debug information
        print(f"Status code: {response.status_code}")
        print(f"Response content: {response.text}")
        
        # Parse the response as JSON
        response_data = response.json()
        
        # Check if there's an error in the API response
        if "error" in response_data:
            error_message = response_data.get("error", {}).get("message", "Unknown error")
            error_code = response_data.get("error", {}).get("code", "")
            return jsonify({"error": f"API Error ({error_code}) {error_message}"}), 400
            
        # Check if there's an ID in the response
        if "id" in response_data:
            return jsonify({"success": True, "container_id": response_data["id"]}), 200
        else:
            return jsonify({"error": f"Response without ID: {response_data}"}), 400
            
    except requests.exceptions.RequestException as e:
        print(f"Request error: {str(e)}")
        return jsonify({"error": f"Request error: {str(e)}"}), 500
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
    
    
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
    try:
        data = request.json
        required_fields = ['instagram_account_id', 'access_token', 'media_url', 'caption']
        
        # Verifica se todos os campos necessários estão presentes
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400

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
