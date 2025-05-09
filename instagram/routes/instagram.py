from flask import Blueprint, request, jsonify
from create_post import (
    create_instagram_media,
    check_instagram_media_status,
    publish_instagram
)
from get_id import instagram

instagram_bp = Blueprint('instagram_bp', __name__, url_prefix='/instagram')

@instagram_bp.route('/')
def instagramEndpoint():
    return instagram()

@instagram_bp.route('/media', methods=['POST'])
def create_instagram_media_endpoint():
    return create_instagram_media()

@instagram_bp.route('/status', methods=['GET'])
def create_media_container_endpoint():
    return check_instagram_media_status()

@instagram_bp.route('/post', methods=['POST'])
def create_instagram_post_endpoint():
    return publish_instagram()