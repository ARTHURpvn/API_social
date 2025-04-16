from flask import request, jsonify, send_from_directory, current_app
import os
import uuid

# Tipos de arquivos permitidos
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/x-matroska"}

def upload_image():
    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    file = request.files["file"]
    content_type = file.content_type

    if content_type in ALLOWED_IMAGE_TYPES:
        file_type = "image"
    elif content_type in ALLOWED_VIDEO_TYPES:
        file_type = "video"
    else:
        return jsonify({"error": "Tipo de arquivo não suportado"}), 400

    # Pasta onde os arquivos serão salvos
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)

    file_url = request.host_url + "uploads/" + filename

    return jsonify({
        "url": file_url,
        "type": file_type,
    })

def serve_image(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
