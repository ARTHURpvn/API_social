from flask import Flask, Blueprint, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import os
import uuid

app = Flask(__name__)
CORS(app)

# Configuração de uploads
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Funções de arquivo
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

# Rotas de upload
@app.route("/upload", methods=["POST"])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "Arquivo sem nome"}), 400

    filename = save_uploaded_file(file)
    file_url = f"https://127.0.0.1:5000/uploads/{filename}"

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
# Importe as funções necessárias aqui
try:
    from linkedin.get_token import linkedin, linkedinCallback
    
    @app.route('/linkedin')
    def linkedinEndpoint():
        return linkedin()

    @app.route('/callback/linkedin')
    def linkedinCallbackEndpoint():
        return linkedinCallback()
except ImportError:
    # Se não conseguir importar, crie endpoints temporários para debug
    @app.route('/linkedin')
    def linkedinEndpoint():
        return jsonify({"error": "Módulo LinkedIn não encontrado"}), 500
        
    @app.route('/callback/linkedin')
    def linkedinCallbackEndpoint():
        return jsonify({"error": "Módulo LinkedIn não encontrado"}), 500

# INSTAGRAM
# Importe as funções necessárias aqui
try:
    from instagram.get_id import instagram, instagramCallback
    from instagram.create_post import create_instagram_post, create_media_container
    
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
except ImportError:
    # Se não conseguir importar, crie endpoints temporários para debug
    @app.route('/instagram')
    def instagramEndpoint():
        return jsonify({"error": "Módulo Instagram não encontrado"}), 500
        
    @app.route('/callback/instagram')
    def instagramCallbackEndpoint():
        return jsonify({"error": "Módulo Instagram não encontrado"}), 500
        
    @app.route('/instagram/post', methods=['POST'])
    def create_instagram_post_endpoint():
        return jsonify({"error": "Módulo Instagram não encontrado"}), 500
        
    @app.route('/instagram/container', methods=['POST'])
    def create_media_container_endpoint():
        return jsonify({"error": "Módulo Instagram não encontrado"}), 500

# Rota principal para verificar se a aplicação está online
@app.route('/')
def home():
    return jsonify({"status": "online", "message": "API is running"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)