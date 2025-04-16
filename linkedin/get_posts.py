import requests

def get_user_posts(access_token,urn):
    url = f"https://api.linkedin.com/v2/shares?q=owners&owners={urn}&sortBy=LAST_MODIFIED&sharesPerOwner=100"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0"
    }

    response = requests.post(url, headers=headers)
    return response.json()