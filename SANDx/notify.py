import requests

def send_notification(url, topic, message):
    """
    Send a notification message to a specified topic using ntfy.
    """
    re = requests.post(f"{url}/{topic}", data=message.encode(encoding='utf-8'))

    return re.status_code

