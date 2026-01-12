import requests
from huggingface_hub import HfApi
import os

USER = os.environ["HF_USERNAME"]
TOKEN = os.environ.get("HF_TOKEN")

def get_direct_url(space_id):
    subdomain = space_id.lower().replace("/", "-").replace("_", "-").replace(".", "-")
    return f"https://{subdomain}.hf.space"

def wake_up_spaces():
    api = HfApi(
        token=TOKEN
    )
    
    print(f"Fetching spaces for: {USER}...")
    my_spaces = api.list_spaces(author=USER)
    
    for space in my_spaces:
        direct_url = get_direct_url(space.id)
        
        print(f"Waking up: {space.id}")
        print(f"   URL: {direct_url}")
        
        try:
            response = requests.get(direct_url, timeout=10)
            print(f"   Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"   Signal sent! (Request timed out waiting for boot: {e})")
        print("-" * 30)

if __name__ == "__main__":
    wake_up_spaces()