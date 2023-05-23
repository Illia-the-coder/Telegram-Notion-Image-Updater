import os
import asyncio
import logging
from telethon import TelegramClient, events
import pandas as pd
from dotenv import load_dotenv
from ProcessNotion import *
from LoadImagesTelegram import *
import time 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')




class TelegramNotionIntegration:
    def __init__(self, api_id, api_hash, group_username, allowed_usernames, notion_token, database_id):
        logging.info("Initializing TelegramNotionIntegration...")
        self.client = TelegramClient('session_name', api_id, api_hash)
        self.group_username = group_username
        self.allowed_usernames = allowed_usernames
        self.notion_token = notion_token
        self.database_id = database_id


    async def process_new_photos(self, event):
        sender = await event.get_sender()
        logging.info(f"Processing new photos...")
        logging.info(f"Sender: {sender.username}")
        if bool(event.photo) and sender.username in self.allowed_usernames:
            time.sleep(100)
            logging.info("New photo message detected from the specific user!")
            filtered_df = pd.read_csv('local_database.csv')
            filtered_df['Date'] = pd.to_datetime(filtered_df['Date'])
            if event.date.date() in filtered_df['Date'].dt.date.values:
                await self.main()

    async def download_database(self, notion_token, database_id):
        logging.info("Downloading database...")
        DW = NotionDatabaseDW(notion_token, database_id)
        results = DW.query_database()
        df = DW.extract_data_and_export_to_csv(results)
        df = DW.preprocess_df(df)
        df.to_csv('local_database.csv', index=False)

    async def main(self, AccessAllDates=True, embed=False):
        logging.info("Running main function...")
        DW = NotionDatabaseDW(self.notion_token, self.database_id)
        results = DW.query_database()
        df = DW.extract_data_and_export_to_csv(results)
        df = DW.preprocess_df(df)
        df.to_csv('local_database.csv', index=False)
        filtered_df = DW.filter_df(df, AccessAllDates)
        start_dates = list(filtered_df['Date'])
        logging.info("Filtered DataFrame created.")
        print(start_dates)
        downloader = TelegramImageDownloader(api_id, api_hash, group_username, allowed_usernames)
        logging.info("Downloading images from Telegram...")
        tlDfUrl = await downloader.main(start_dates, embed=embed)

        logging.info("Adding image URLs to DataFrame...")
        filtered_df['urls'] = filtered_df['Date'].apply(
            lambda x: tlDfUrl[x.date()] if x.date() in tlDfUrl.keys() else [])
        print(filtered_df)
        logging.info("Adding images to Notion pages and ticking checkboxes...")
        for i in filtered_df.iterrows():
            for url in i[1]['urls']:
                DW.add_image_to_page(page_id=i[1]['id'], image_url=url, embed=embed)
            if len(i[1]['urls']):
                DW.tick_lesson_checkbox(page_id=i[1]['id'])
                logging.info(f'Submitted {i[1]["id"]}')

    def start(self):
        logging.info("Starting application...")
        loop = asyncio.get_event_loop()
        if not os.path.exists('local_database.csv'):
            loop.run_until_complete(self.download_database(self.notion_token, self.database_id))

        self.client.start()
        self.client.add_event_handler(self.process_new_photos, events.NewMessage(chats=self.group_username))
        logging.info("Telegram client started, waiting for new messages...")
        self.client.run_until_disconnected()

if __name__ == "__main__":
    load_dotenv()
    logging.info("Loaded environment variables.")
    notion_token = os.getenv('NOTION_TOKEN')
    database_id = os.getenv('DATABASE_ID')
    api_id = int(os.getenv('API_ID'))  # Converting string to int as API_ID should be int
    api_hash = os.getenv('API_HASH')
    group_username = os.getenv('GROUP_USERNAME')
    allowed_usernames = allowed_usernames = ['aberez68','Illiaillia56']
    logging.info("Environment variables loaded.")
    logging.info("Allowed usernames: " + str(allowed_usernames))

    TelegramNotionIntegration(api_id, api_hash, group_username, allowed_usernames, notion_token, database_id).start()
