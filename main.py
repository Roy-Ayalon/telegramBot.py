from flask import Flask, request
from telethon.sync import TelegramClient, events
import re
import get_info_of_url as info

from flask import Flask
from telethon.sync import TelegramClient, events
import threading
import asyncio
import sqlitepool

API_ID = 26720965
API_HASH = 'c0bb692038911a6cc6f977d0d55224c3'
SESSION_NAME = 'your_session_name'

app = Flask(__name__)

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


async def new_message_handler(event):
    listen_to_messages(event)

async def polling_thread(connection_pool):
    # Get a connection from the pool
    connection = connection_pool.connect()

    # Create a new event loop for the thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Run the polling loop in the separate thread
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH, loop=loop, connection=connection)
    client.add_event_handler(new_message_handler, events.NewMessage)

    try:
        await client.start()
        await client.run_until_disconnected()
    finally:
        # Release the connection back to the pool when done
        connection_pool.release(connection)

@app.route('/')
def index():
    return 'Telegram Bot is running!'

if __name__ == "__main__":
    # Create a SQLite connection pool
    connection_pool = sqlitepool.SimpleSQLitePool('session.db', check_same_thread=False)

    # Start the polling thread
    polling_thread = threading.Thread(target=asyncio.run, args=(polling_thread(connection_pool),))
    polling_thread.start()

    # Start the Flask app in the main thread
    app.run(debug=True)
