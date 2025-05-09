from flask import jsonify
import requests

def making_request(url, params):
    try:
        response = requests.post(url, params=params, timeout=60)
        print(f"📡 Resposta da criação do container: {response.text}")
    except Exception as e:
        return jsonify({"error": f"Erro ao fazer requisição: {str(e)}"}), 501

    response_data = response.json()
    if "error" in response_data:
        return jsonify({"error": f"Erro da API: {response_data['error']}"}), 400

    if "id" in response_data:
        return response_data["id"]

    else:
        return jsonify({"error": f"Resposta inesperada: {response_data}"}), 400