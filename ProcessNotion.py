import os
import csv
import pandas as pd
from notion_client import Client
import logging
import asyncio
from telethon import TelegramClient
from telethon.tl.types import InputMessagesFilterPhotos

class NotionDatabaseDW:
    def __init__(self, notion_token, database_id):
        self.notion = Client(auth=notion_token)
        self.database_id = database_id

    def add_image_to_page(self, page_id, image_url):
        logging.info("Adding image to Notion page...")
        block_properties = {
            "object": "block",
            "type": "embed",
            "embed": {
                "url": image_url
            }
        }
        response = self.notion.blocks.children.append(
            block_id=page_id,
            children=[block_properties]
        )
        if response:
            logging.info(f"Image {image_url} added to the page successfully!")
        else:
            logging.info(f"Failed to add image {image_url} to the page.")

    def query_database(self):
        logging.info("Querying Notion database...")
        results = self.notion.databases.query(database_id=self.database_id)
        logging.info("Database query successful.")
        return results

    def extract_data_and_export_to_csv(self, results):
        logging.info("Extracting data from query results...")
        data = []
        columns = results["results"][0]["properties"].keys()

        for page in results["results"]:
            row = {}
            row['id'] = page["id"]
            for column in columns:
                property_type = page["properties"][column]["type"]
                if property_type in page["properties"][column]:
                    row[column] = page["properties"][column][property_type]
                else:
                    row[column] = ""
            data.append(row)

        df = pd.DataFrame(data)
        df.to_csv("notion_database.csv", index=False,
                  quoting=csv.QUOTE_NONNUMERIC)
        logging.info("Data extracted and exported to CSV.")
        return df

    def preprocess_df(self, df):
        logging.info("Preprocessing DataFrame...")
        df['Date'] = df['Date'].apply(lambda x: x['start'])
        df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
        df = df[['Date', 'id', 'Lesson']]
        df = df.sort_values(by=['Date'])
        logging.info("DataFrame preprocessed.")
        return df

    def filter_df(self, df):
        logging.info("Filtering DataFrame...")
        df_false = df[df['Lesson'] == False]
        filtered_df = df_false[(df_false['Date'] > df[df['Lesson']].iloc[-1]
                                ['Date']) & (df_false['Date'] <= pd.to_datetime('today'))]
        logging.info("DataFrame filtered.")
        return filtered_df
    
    def tick_lesson_checkbox(self, page_id):
        logging.info(f"Ticking 'Lesson' checkbox for page {page_id}...")
        update_properties = {
            "Lesson": {
                "checkbox": True
            }
        }
        response = self.notion.pages.update(page_id, properties=update_properties)
        if response:
            logging.info(f"Successfully ticked 'Lesson' checkbox for page {page_id}!")
        else:
            logging.info(f"Failed to tick 'Lesson' checkbox for page {page_id}.")

