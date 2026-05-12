import requests
import os

def get_component_data(mpn: str):
    """
    Queries Octopart/Nexar API to get real-time part data.
    """
    api_key = os.getenv("OCTOPART_API_KEY")
    url = f"https://octopart.com/api/v4/rest/parts/match?queries=[{{'mpn':'{mpn}'}}]&apikey={api_key}"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # Extract stock and technical attributes
        part = data['results'][0]['items'][0]
        return {
            "mpn": part['mpn'],
            "stock": sum(s['inventory_level'] for s in part['offers']),
            "datasheet_url": part['specs'].get('datasheet_url'),
            "is_eol": part.get('lifecycle_status') == 'obsolete'
        }
    return {"error": "Part not found"}
  
