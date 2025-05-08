from flask import Flask, request, jsonify
from instagram.get_id import instagram
from instagram.create_post import check_instagram_media_status, create_instagram_media, publish_instagram
from linkedin.get_token import linkedin, linkedinCallback
from flask_cors import CORS
from instagram.create_post import instagram_post_routes
import os
import uuid
import cloudinary
import cloudinary.uploader

# Criação da aplicação Flask
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:8080", "https://api-social-sd6m.onrender.com", "https://preview--socialwhiz-creator.lovable.app"]}})

app.register_blueprint(instagram_post_routes)

# Config Cloudinary
cloudinary.config( 
    cloud_name = "djaqxziua", 
    api_key = "934931552134249", 
    api_secret = "VFpYXwUZbcUFvjuZksDLkU6-ZZE", 
)


# Configuração da pasta de uploads
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Rotas de upload e gerenciamento de arquivos
@app.route("/upload", methods=["POST"])
def upload():
    file = request.files['file']
    ext = os.path.splitext(file.filename)[1]
    temp_filename = f"{uuid.uuid4().hex}{ext}"
    temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)

    mimetype = file.mimetype

    if mimetype.startswith("image/"):
        type = "image"
    elif mimetype.startswith("video/"):
        type = "video"

    # Garante que a pasta de uploads existe
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    try:
        print(f"Salvando arquivo em {temp_filepath}")  # LOG
        file.save(temp_filepath)

        # Faz upload para a Cloudinary
        print("Iniciando upload para Cloudinary...")  # LOG
        if type == "image":
            upload_result = cloudinary.uploader.upload(temp_filepath, resource_type="image")
        else:
            upload_result = cloudinary.uploader.upload_large(temp_filepath, resource_type="video", chunk_size=6000000)


        file_url = upload_result.get("secure_url")
        print(f"Upload concluído: {file_url}")  # LOG

        os.remove(temp_filepath)

        return jsonify({"url": file_url}), 200

    except Exception as e:
        print("Erro no upload:", str(e))  # LOG DE ERRO
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
        return jsonify({"error": str(e)}), 500


@app.route("/remove/<filename>", methods=["DELETE"])
def remove(filename):
    try:
        cloudinary.uploader.destroy(filename)
        return jsonify({"message": "Arquivo removido com sucesso"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
# ENDPOINTS DO LINKEDIN
@app.route('/linkedin')
def linkedinEndpoint():
    return linkedin()

@app.route('/callback/linkedin')
def linkedinCallbackEndpoint():
    return linkedinCallback()



# ENDPOINTS DO INSTAGRAM
@app.route('/instagram')
def instagramEndpoint():
    return instagram()

@app.route('/instagram/media', methods=['POST'])
def create_instagram_post_endpoint():
    return create_instagram_media()

@app.route('/instagram/status', methods=['POST'])
def create_media_container_endpoint():
    return check_instagram_media_status()

@app.route('/instagram/post', methods=['POST'])
def create_instagram_post_endpoint():
    return publish_instagram()

# Execução da aplicação
if __name__ == '__main__':
    app.run(debug=True, port=5000)