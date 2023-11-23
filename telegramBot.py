import re
import get_info_of_url as info

API_ID = 26720965
API_HASH = 'c0bb692038911a6cc6f977d0d55224c3'

from telethon.sync import TelegramClient, events
from urllib.parse import urlparse

def listen_to_messages(event):

    chat_from = event.chat if event.chat else (event.get_chat()) # telegram MAY not send the chat enity
    chat_title = chat_from.title

    sender_username = event.sender.username
    chat_id = event.chat_id
    text = event.text
    date = event.date

    print(f"New message in group {chat_title} from {sender_username} in time - {date} : {text}")

    urls = []
    israeli_urls = []
    if ".il" in text:
        regex = "http[s]*\S+"  # Pattern to match a valid URL
        urls = re.findall(regex, text)
        for url in urls:
            if ".il" in url:
                israeli_urls.append(url)
        # Write message details to a text file
        with open('messages.txt', 'a', encoding='utf-8') as file:
            file.write(f"Group {chat_title} | Sender: {sender_username} | URLs: {israeli_urls} | Message: {text}\n")
        for url in israeli_urls:
            clean_url = re.sub(r'https?://([^/]+).*', r'\1', url)
            whois_info = info.get_whois_info(clean_url)
            new_text = info.get_text_between_phrases(whois_info, "person:", "registrar info:")
            ip_of_server = info.get_ip_address(clean_url)
            dictionary = info.create_dictionary(new_text, url, None, None, None, ip_of_server)
            with open("urls_to_check.txt", 'a', encoding='utf-8') as file:
                file.write(f"{dictionary} \n")

SESSION_NAME = 'your_session_name'

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

@client.on(events.NewMessage)
async def new_message_handler(event):
    listen_to_messages(event)

if __name__ == "__main__":
    client.start()
    client.run_until_disconnected()
