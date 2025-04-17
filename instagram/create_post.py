from flask import jsonify
import requests
from flask import  request, jsonify
import time

from flask import Flask, jsonify, request
import requests

def create_media_container():
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    
    data = request.get_json()
    ACCESS_TOKEN = data.get('instagramToken')
    MEDIA = data.get('media')
    
    # Auto-detect media type based on file extension
    file_extension = MEDIA.split('.')[-1].lower() if '.' in MEDIA else ''
    TYPE = 'REELS' if file_extension in ['mp4', 'mov', 'mpeg', 'avi'] else 'IMAGE'
    
    # Override with explicit type if provided
    if 'type' in data:
        TYPE = data.get('type')
    
    print(f"Media URL received: {MEDIA}")
    print(f"Media type detected: {TYPE}")
    
    # Verify media URL is accessible
    try:
        head_response = requests.head(MEDIA)
        print(f"Media URL head response: Status {head_response.status_code}")
        print(f"Content-Type: {head_response.headers.get('Content-Type')}")
        
        if head_response.status_code != 200:
            return jsonify({"error": f"Media URL returned status {head_response.status_code}"}), 400
            
        content_type = head_response.headers.get('Content-Type', '')
        if not content_type.startswith(('image/', 'video/')):
            print(f"Warning: Media URL does not appear to have an image/video Content-Type: {content_type}")
    except Exception as e:
        print(f"Warning: Failed to access media URL: {str(e)}")
    
    try:
        url = f"https://graph.facebook.com/v22.0/17841472937904147/media"
        params = {
            "access_token": ACCESS_TOKEN
        }
        
        # Add the correct parameter based on media type
        if TYPE == 'REELS' or TYPE == 'VIDEO':
            params["video_url"] = MEDIA
            print("Using video_url parameter")
        else:  # TYPE == 'IMAGE'
            params["image_url"] = MEDIA
            print("Using image_url parameter")
            
        # Make the request and capture the full response
        print(f"Making request to {url} with params: {params}")
        response = requests.post(url, params=params, timeout=60)
        
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
