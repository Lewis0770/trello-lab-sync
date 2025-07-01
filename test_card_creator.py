import os
import requests
from datetime import datetime

# Trello credentials (must be passed via environment variables)
API_KEY = os.getenv("TRELLO_API_KEY")
TOKEN = os.getenv("TRELLO_TOKEN")
BOARD_ID = os.getenv("TRELLO_BOARD_ID")

# Check if all required environment variables are set
if not all([API_KEY, TOKEN, BOARD_ID]):
    print("Error: Missing required environment variables")
    print(f"API_KEY: {'✓' if API_KEY else '✗'}")
    print(f"TOKEN: {'✓' if TOKEN else '✗'}")
    print(f"BOARD_ID: {'✓' if BOARD_ID else '✗'}")
    exit(1)

# Auto-generated names and description
timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
LIST_NAME = f"AutoList {timestamp}"
CARD_NAME = f"AutoCard {timestamp}"
CARD_DESC = f"This card was created by GitHub Actions at {timestamp}."

def get_lists(board_id):
    url = f"https://api.trello.com/1/boards/{board_id}/lists"
    params = {"key": API_KEY, "token": TOKEN}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def create_list(board_id, list_name):
    url = "https://api.trello.com/1/lists"
    params = {
        "key": API_KEY,
        "token": TOKEN,
        "idBoard": board_id,
        "name": list_name,
        "pos": "bottom"
    }
    response = requests.post(url, params=params)
    response.raise_for_status()
    return response.json()["id"]

def create_card(list_id, name, desc):
    url = "https://api.trello.com/1/cards"
    params = {
        "key": API_KEY,
        "token": TOKEN,
        "idList": list_id,
        "name": name,
        "desc": desc
    }
    response = requests.post(url, params=params)
    response.raise_for_status()
    return response.json()

def main():
    try:
        print("Fetching existing lists...")
        trello_lists = get_lists(BOARD_ID)
        
        # Always create a new list (as per request)
        print(f"Creating new list: {LIST_NAME}")
        list_id = create_list(BOARD_ID, LIST_NAME)
        
        print(f"Creating card in list '{LIST_NAME}'...")
        card = create_card(list_id, CARD_NAME, CARD_DESC)
        
        print(f"✅ Created card: {card.get('url', '[No URL]')}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        exit(1)

if __name__ == "__main__":  # Fixed: double underscores, not asterisks
    main()