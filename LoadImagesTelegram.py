import os
import csv
import asyncio
from telethon import TelegramClient
from telethon.tl.types import InputMessagesFilterPhotos
import pandas as pd
from tqdm.asyncio import tqdm as tqdm_async
from datetime import datetime
import cloudinary
import cloudinary.uploader
import pytz
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class TelegramImageDownloader:
    def __init__(self, api_id, api_hash, group_username, allowed_usernames):
        self.api_id = api_id
        self.api_hash = api_hash
        self.group_username = group_username
        self.IMAGE_DIR = 'images'
        self.allowed_usernames = allowed_usernames
        self._create_image_directory()
        self._configure_cloudinary()

    def _create_image_directory(self):
        if not os.path.exists(self.IMAGE_DIR):
            os.makedirs(self.IMAGE_DIR)
  
    def _configure_cloudinary(self):
        cloudinary.config(
            cloud_name="dw8hy0djm",
            api_key="467249925385789",
            api_secret="ABAjN3ZCbGMPS60y7mlrps5INBU",
            secure=True
        )

    async def get_message_count(self, client):
        messages = await client.get_messages(self.group_username)
        return len(messages)

    async def download_images(self, client, start_dates, from_usernames, embed = False):
        data = []
        message_count = await self.get_message_count(client)
        start_dates = [start_date.date() for start_date in start_dates]

        async for message in client.iter_messages(self.group_username, filter=InputMessagesFilterPhotos):
            day = pd.Timestamp(message.date).date()

            if day in start_dates and message.sender.username in from_usernames:
                if not embed:
                    file_name = f'{message.id}.jpg'
                    file_path = os.path.join(self.IMAGE_DIR, file_name)
                    logging.info(f'Downloading image to: {file_path}')
                    await client.download_media(message=message, file=file_path)
                    response = self._upload_to_cloudinary(file_path)['secure_url'] 
                else:
                    response = f'https://t.me/physics171/{message.id}'
                data.append([message.id, day, message.sender.first_name,response])

        df = pd.DataFrame(data, columns=['id', 'date', 'from', 'url'])
        df = df.sort_values(by=['id'], ascending=True)
        grouped_df = dict(df.groupby('date')['url'].apply(list))
        # logging.info(f'Image download complete. Grouped images: {grouped_df}')
        return grouped_df

    def _upload_to_cloudinary(self, file_path):
        response = cloudinary.uploader.upload(file_path)
        return response

    async def main(self, start_date, embed = False):
        async with TelegramClient('anon', self.api_id, self.api_hash) as client:
            return await self.download_images(client, start_date, self.allowed_usernames,embed  = embed)