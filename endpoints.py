from flask import Flask, Blueprint, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import uuid

# Criação da aplicação Flask
app = Flask(__name__)
CORS(app)

# Configuração da pasta de uploads
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Funções auxiliares para gerenciamento de arquivos
def ensure_upload_folder_exists():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

def save_uploaded_file(file):
    ensure_upload_folder_exists()
    ext = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, unique_name)
    file.save(filepath)
    return unique_name

# Funções para LinkedIn (você precisará implementar essas funções)
def linkedin():
    # Implementação da autenticação do LinkedIn
    return "LinkedIn authentication"

def linkedinCallback():
    # Implementação do callback do LinkedIn
    return "LinkedIn callback"

# Funções para Instagram (você precisará implementar essas funções)
def instagram():
    # Implementação da autenticação do Instagram
    return "Instagram authentication"

def instagramCallback():
    # Implementação do callback do Instagram
    return "Instagram callback"

def create_instagram_post():
    # Implementação para criar post no Instagram
    return "Create Instagram post"

def create_media_container():
    # Implementação para criar um container de mídia no Instagram
    return "Create media container"

# Rotas de upload e gerenciamento de arquivos
@app.route("/upload", methods=["POST"])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "Arquivo sem nome"}), 400

    filename = save_uploaded_file(file)
    file_url = f"https://api-social-sd6m.onrender.com/uploads/{filename}"

    return jsonify({"url": file_url}), 200

@app.route("/uploads/<filename>")
def serve_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route("/remove/<filename>")
def remove_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return jsonify({"message": "Arquivo removido com sucesso"}), 200

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
    return create_instagram_post()

@app.route('/instagram/container', methods=['POST'])
def create_media_container_endpoint():
    return create_media_container()

# Execução da aplicação
if __name__ == '__main__':
    app.run(debug=True, port=5000)