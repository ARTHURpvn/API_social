from flask import Flask
from flask_cors import CORS
from app import routes

from linkedin.get_token import linkedin, linkedinCallback
from instagram.get_id import instagram, instagramCallback
from instagram.create_post import create_instagram_post, create_media_container


app = Flask(__name__)
CORS(app)


app.config['UPLOAD_FOLDER'] = 'uploads'
app.register_blueprint(routes)

# ENDPOINTS DO LINKEDIN

@app.route('/linkedin')
def linkedinEndpoint():
    return linkedin()

@app.route('/callback/linkedin')
def linkedinCallbackEndpoint():
    return linkedinCallback()

# INSTAGRAM
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


if __name__ == '__main__':
    app.run(debug=True, port=5000, ssl_context='adhoc')
