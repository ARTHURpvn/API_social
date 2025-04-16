from flask import Blueprint, request, jsonify, send_from_directory
import os
import uuid

routes = Blueprint("routes", __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')

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


@routes.route("/upload", methods=["POST"])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "Arquivo sem nome"}), 400

    filename = save_uploaded_file(file)
    file_url = f"https://127.0.0.1:5000/uploads/{filename}"

    return jsonify({"url": file_url}), 200


@routes.route("/uploads/<filename>")
def serve_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@routes.route("/remove/<filename>")
def remove_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return jsonify({"message": "Arquivo removido com sucesso"}), 200
