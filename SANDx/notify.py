import requests

def send_notification(url, topic, message):
    """
    Send a notification message to a specified topic using ntfy.
    """
    re = requests.post(f"{url}/{topic}", data=message.encode(encoding='utf-8'))
    print(f"Notifying: {re.text}")

    return re.status_code

