
import requests
import json

def get_insights(access_token, urn):
    """Retrieve post insights from LinkedIn API"""
    url = f"https://api.linkedin.com/v2/organizationalEntityShareStatistics?q=organizationalEntity&organizationalEntity={urn}"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "LinkedIn-Version": "202401"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching LinkedIn insights: {response.status_code}")
        print(response.text)
        return None

def share_analytics(access_token, share_urn):
    """Get analytics for a specific LinkedIn share"""
    encoded_urn = share_urn.replace(":", "%3A")
    url = f"https://api.linkedin.com/v2/socialActions/{encoded_urn}"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "LinkedIn-Version": "202401"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching share analytics: {response.status_code}")
        print(response.text)
        return None
