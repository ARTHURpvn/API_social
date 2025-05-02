from flask import Flask, request, jsonify
from instagram.get_id import instagram, instagramCallback
from instagram.create_post import create_media_container, publish_instagram_post
from linkedin.get_token import linkedin, linkedinCallback
from flask_cors import CORS
import os
import uuid
import cloudinary
import cloudinary.uploader

# Config Cloudinary
cloudinary.config( 
    cloud_name = "djaqxziua", 
    api_key = "934931552134249", 
    api_secret = "VFpYXwUZbcUFvjuZksDLkU6-ZZE", 
)

# Criação da aplicação Flask
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:8080", "https://api-social-sd6m.onrender.com", "https://preview--socialwhiz-creator.lovable.app"]}})

# Configuração da pasta de uploads
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Rotas de upload e gerenciamento de arquivos
@app.route("/upload", methods=["POST"])
def upload():
    print("Requisição recebida no /upload")  # LOG

    if 'file' not in request.files:
        print("Nenhum arquivo na requisição.")  # LOG
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    file = request.files['file']
    if file.filename == '':
        print("Arquivo com nome vazio.")  # LOG
        return jsonify({"error": "Arquivo sem nome"}), 400

    ext = os.path.splitext(file.filename)[1]
    temp_filename = f"{uuid.uuid4().hex}{ext}"
    temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)

    # Garante que a pasta de uploads existe
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    try:
        print(f"Salvando arquivo em {temp_filepath}")  # LOG
        file.save(temp_filepath)

        # Faz upload para a Cloudinary
        print("Iniciando upload para Cloudinary...")  # LOG
        upload_result = cloudinary.uploader.upload(temp_filepath)

        file_url = upload_result.get("secure_url")
        print(f"Upload concluído: {file_url}")  # LOG

        os.remove(temp_filepath)

        return jsonify({"url": file_url}), 200

    except Exception as e:
        print("Erro no upload:", str(e))  # LOG DE ERRO
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
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

@app.route('/callback/instagram')
def instagramCallbackEndpoint():
    return instagramCallback()

@app.route('/instagram/post', methods=['POST'])
def create_instagram_post_endpoint():
    return publish_instagram_post()

@app.route('/instagram/container', methods=['POST'])
def create_media_container_endpoint():
    return create_media_container()

# Execução da aplicação
if __name__ == '__main__':
    app.run(debug=True, port=5000)