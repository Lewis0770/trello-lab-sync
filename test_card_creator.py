import os
import requests
from datetime import datetime

# Trello credentials (must be passed via environment variables)
API_KEY = os.getenv("TRELLO_API_KEY")
TOKEN = os.getenv("TRELLO_TOKEN")
BOARD_ID = os.getenv("TRELLO_BOARD_ID")

# Slack webhook URL
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# Check if all required environment variables are set
if not all([API_KEY, TOKEN, BOARD_ID, SLACK_WEBHOOK_URL]):
    print("Error: Missing required environment variables")
    print(f"API_KEY: {'✓' if API_KEY else '✗'}")
    print(f"TOKEN: {'✓' if TOKEN else '✗'}")
    print(f"BOARD_ID: {'✓' if BOARD_ID else '✗'}")
    print(f"SLACK_WEBHOOK_URL: {'✓' if SLACK_WEBHOOK_URL else '✗'}")
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
    data = {
        "key": API_KEY,
        "token": TOKEN,
        "idBoard": board_id,
        "name": list_name,
        "pos": "bottom"
    }
    print(f"Attempting to create list with board ID: {board_id}")
    response = requests.post(url, data=data)
    print(f"Response status: {response.status_code}")
    if response.status_code != 200:
        print(f"Response text: {response.text}")
    response.raise_for_status()
    return response.json()["id"]

def create_card(list_id, name, desc):
    url = "https://api.trello.com/1/cards"
    data = {
        "key": API_KEY,
        "token": TOKEN,
        "idList": list_id,
        "name": name,
        "desc": desc
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()

def send_slack_notification(card_info, list_name, success=True):
    """Send notification to Slack about card creation"""
    if success:
        message = {
            "text": "✅ Trello Card Created Successfully!",
            "attachments": [
                {
                    "color": "good",
                    "fields": [
                        {"title": "Card Name", "value": card_info.get('name', 'N/A'), "short": True},
                        {"title": "List", "value": list_name, "short": True},
                        {"title": "Card URL", "value": card_info.get('url', 'N/A'), "short": False},
                        {"title": "Created At", "value": timestamp, "short": True}
                    ],
                    "footer": "Trello Automation Bot",
                    "ts": int(datetime.utcnow().timestamp())
                }
            ]
        }
    else:
        message = {
            "text": "❌ Trello Card Creation Failed!",
            "attachments": [
                {
                    "color": "danger",
                    "fields": [
                        {"title": "Error", "value": "Failed to create card", "short": False},
                        {"title": "Attempted At", "value": timestamp, "short": True}
                    ],
                    "footer": "Trello Automation Bot",
                    "ts": int(datetime.utcnow().timestamp())
                }
            ]
        }
    
    response = requests.post(SLACK_WEBHOOK_URL, json=message)
    response.raise_for_status()
    return response.status_code == 200

def main():
    try:
        print(f"Using Board ID: {BOARD_ID}")
        print("Fetching existing lists...")
        trello_lists = get_lists(BOARD_ID)
        print(f"Found {len(trello_lists)} existing lists")
        
        # Always create a new list (as per request)
        print(f"Creating new list: {LIST_NAME}")
        list_id = create_list(BOARD_ID, LIST_NAME)
        
        print(f"Creating card in list '{LIST_NAME}'...")
        card = create_card(list_id, CARD_NAME, CARD_DESC)
        
        print(f"✅ Created card: {card.get('url', '[No URL]')}")
        
        # Send success notification to Slack
        print("📤 Sending success notification to Slack...")
        if send_slack_notification(card, LIST_NAME, success=True):
            print("✅ Slack notification sent successfully!")
        else:
            print("⚠️ Slack notification failed, but card was created successfully")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {e}")
        
        # Send failure notification to Slack
        try:
            print("📤 Sending failure notification to Slack...")
            send_slack_notification({}, LIST_NAME, success=False)
            print("✅ Slack failure notification sent")
        except Exception as slack_error:
            print(f"❌ Failed to send Slack notification: {slack_error}")
        
        exit(1)
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        
        # Send failure notification to Slack
        try:
            print("📤 Sending failure notification to Slack...")
            send_slack_notification({}, LIST_NAME, success=False)
            print("✅ Slack failure notification sent")
        except Exception as slack_error:
            print(f"❌ Failed to send Slack notification: {slack_error}")
        
        exit(1)

if __name__ == "__main__":
    main()
