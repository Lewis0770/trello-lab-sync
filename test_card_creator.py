import os
import requests

# Trello credentials (passed via environment variables)
API_KEY = os.getenv("TRELLO_API_KEY")
TOKEN = os.getenv("TRELLO_TOKEN")
BOARD_ID = os.getenv("TRELLO_BOARD_ID")

LIST_NAME = "Integration Test"
CARD_NAME = "GitHub Actions Test Card"
CARD_DESC = "This is a dry-run test card created automatically."

def get_lists(board_id):
    url = f"https://api.trello.com/1/boards/{board_id}/lists"
    params = {"key": API_KEY, "token": TOKEN}
    response = requests.get(url, params=params)
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
    return response.json()

def main():
    trello_lists = get_lists(BOARD_ID)
    target_list = next((l for l in trello_lists if l["name"].lower() == LIST_NAME.lower()), None)

    if target_list:
        list_id = target_list["id"]
    else:
        list_id = create_list(BOARD_ID, LIST_NAME)

    card = create_card(list_id, CARD_NAME, CARD_DESC)
    print(f"Created card: {card.get('url', '[No URL]')}")

if __name__ == "__main__":
    main()
