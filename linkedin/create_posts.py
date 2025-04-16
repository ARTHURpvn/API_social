import requests
import json

def insert_image(upload_url, image_path, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/octet-stream"
    }
    with open(image_path, 'rb') as image_file:
        response = requests.post(upload_url, headers=headers, data=image_file)
    return response

def upload_archives(urn, access_token, image_path):
    url = "https://api.linkedin.com/v2/assets?action=registerUpload"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }

    data = {
        "registerUploadRequest": {
            "recipes": [
                "urn:li:digitalmediaRecipe:feedshare-image"
            ],
            "owner": f"urn:li:person:{urn}",
            "serviceRelationships": [
                {
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent"
                }
            ]
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    response_json = response.json()

    asset = response_json["value"]["asset"]
    upload_url = response_json["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]

    uploaded = insert_image(upload_url, image_path, access_token)
    if not uploaded.ok:
        return f"Error uploading image: {uploaded.text}"

    return asset

def create_post_image(urn, access_token, image_path):
    media = []
    for image in image_path:
        asset = upload_archives(urn, access_token, image)
        if asset:
            mediaLoop = {
                "status": "READY",
                "description": {
                    "text": "Center stage!"
                },
                "media": asset,
                "title": {
                    "text": "LinkedIn Talent Connect 2021"
                }
            }
            media.append(mediaLoop)

    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }

    data = {
        "author": f"urn:li:person:{urn}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": "Feeling inspired after meeting so many talented individuals at this year's conference. #talentconnect"
                },
                "shareMediaCategory": "IMAGE",
                "media": media
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.content

def create_post(urn, access_token):
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }

    data = {
        "author": f"urn:li:person:{urn}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": "Hello World! This is my first Share on LinkedIn!"},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.content
