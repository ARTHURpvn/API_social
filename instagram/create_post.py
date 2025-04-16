from flask import jsonify
import requests
from flask import  request, jsonify
import time

def create_media_container():
    data = request.get_json()
    TYPE = data.get('type')
    ACCOUNT_ID = data.get('account_id')
    ACCESS_TOKEN = data.get('instagramToken')
    MEDIA = data.get('media')

    if TYPE == 'VIDEO':
        try:
            url = f"https://graph.facebook.com/v22.0/{ACCOUNT_ID}/media"
            params = {
                "media_type": TYPE,
                "video_url": MEDIA,
                "access_token": ACCESS_TOKEN,
            }
            response = requests.post(url, params=params)
            response.raise_for_status()
            
            data = response.json()

            if "id" in data:
                return data["id"]
            else:
                raise Exception(f"Erro ao criar container de mídia: {data}")
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro na requisição: {str(e)}")

    if TYPE == 'IMAGE':
        try:
            url = f"https://graph.facebook.com/v22.0/{ACCOUNT_ID}/media"
            params = {
                "media_type": TYPE,
                "image_url": MEDIA,
                "access_token": ACCESS_TOKEN,
            }
            response = requests.post(url, params=params)
            response.raise_for_status()
            
            data = response.json()

            if "id" in data:
                return data["id"]
            else:
                raise Exception(f"Erro ao criar container de mídia: {data}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro na requisição: {str(e)}")


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
