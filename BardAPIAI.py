import os
import requests
import logging
from PIL import Image
from io import BytesIO
from notion_client import Client
from bardapi import Bard
from ProcessNotion import *

class NotionImageProcessor:
    def __init__(self, notion_token, bard_api_key, database_id):
        logging.info("Initializing NotionImageProcessor...")
        self.notion = Client(auth=notion_token)
        self.bard_api_key = bard_api_key
        self.bard = Bard(
            token=self.bard_api_key, session=self._init_bard_session(), timeout=30
        )
        self.database_id = database_id
        self.image_dir = os.path.join(os.getcwd(), 'images')

    def load_database(self):
        # logging.info("Downloading database...")
        # DW = NotionDatabaseDW(self.notion, self.database_id)
        # results = DW.query_database()
        # df = DW.extract_data_and_export_to_csv(results)
        # df = DW.preprocess_df(df)
        # logging.info("Database downloaded and processed.")
        df = pd.read_csv('resources/local_database.csv')
        return df

    def _init_bard_session(self):
        logging.info("Initializing Bard session...")
        session = requests.Session()
        session.headers = {
            "Host": "bard.google.com",
            "X-Same-Domain": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 11.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Origin": "https://bard.google.com",
            "Referer": "https://bard.google.com/",
        }
        session.cookies.set("__Secure-1PSID", self.bard_api_key)
        logging.info("Bard session initialized.")
        return session

    def get_image_urls(self, page_id):
        logging.info(f"Retrieving image URLs for page {page_id}...")
        try:
            page = self.notion.pages.retrieve(page_id)
            image_urls = []
            children = self.notion.blocks.children.list(block_id=page_id).get("results")
            for child in children:
                if child["type"] == "image":
                    if child["image"].get("type") == "external":
                        image_urls.append(child["image"]["external"]["url"])
                    elif child["image"].get("type") == "file":
                        image_urls.append(child["image"]["file"]["url"])
                elif child["type"] == "embed":
                    image_urls.append(child["embed"]["url"])
            logging.info(f"Retrieved {len(image_urls)} image URLs.")
            return image_urls
        except Exception as e:
            logging.error(f"An error occurred while retrieving image URLs: {str(e)}")
            return []

    def update_ai_name(self, page_id, new_name):
        logging.info(f"Updating 'AiName' for page {page_id}...")
        update_properties = {"AiName": {"rich_text": [{"text": {"content": new_name}}]}}
        response = self.notion.pages.update(page_id, properties=update_properties)
        if response:
            logging.info(f"Successfully updated 'AiName' for page {page_id}!")
        else:
            logging.error(f"Failed to update 'AiName' for page {page_id}.")

    def download_image(self, url, index):
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            logging.error(f"HTTP Error occurred: {errh}")
            return None
        except requests.exceptions.ConnectionError as errc:
            logging.error(f"Error Connecting: {errc}")
            return None
        except requests.exceptions.Timeout as errt:
            logging.error(f"Timeout Error: {errt}")
            return None
        except requests.exceptions.RequestException as err:
            logging.error(f"Something went wrong: {err}")
            return None

        image_path = os.path.join(self.image_dir, f"temp_{index}.jpg")
        with open(image_path, "wb") as f:
            f.write(response.content)
        logging.info(f"Downloaded image: {image_path}")
        return image_path

    def process_image(self, image_path, index):
        with open(image_path, "rb") as image_file:
            img = image_file.read()
        response = self.bard.ask_about_image(
            f"Screenshot {index} Rule 1: max sentences = 3 Rule 2: Output must contain only the name of the topic Rule 3: Output must be in Ukrainian. Rule 4: Topic must be bold.",
            img,
        )["content"]
        logging.info(f"Bard API response for image {index}")
        return response

    def process_images(self, images_urls, topic ):
        for index, url in enumerate(images_urls):
            logging.info(f"Processing image {index}...")
            image_path = self.download_image(url, index)
            if image_path:
                self.process_image(image_path, index)

        response = self.bard.get_answer(
            f"So can you give a short description about this lesson? Rule 1: max sentences = 10. Rule 2: Topic must be related or to big topic called {topic}. Rule 3: Output must be in Ukrainian. Rule 4: Topic must be bold like this '**[topic]**'. Rule 5: Topic name must be convinient with the all of the {len(images_urls)} images.",
        )["content"]
        if '**' in response:
            response = response[response.index("**") + 2 : ]
            response = response[:response.index("**")]
            logging.info(f"Short description generated: {response}")
            return response
        else:
            logging.info(f"No short description generated.")
            return response

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    notion_token = os.getenv('NOTION_TOKEN')
    bard_api_key = os.getenv('BARD_API_KEY')
    database_id = os.getenv('DATABASE_ID')

    NIP = NotionImageProcessor(
        notion_token, bard_api_key, database_id
    )

    df = NIP.load_database()
    ids = df['id'].tolist()
    topics = df['Тема'].tolist()
    for index, (id, topic) in enumerate(zip(ids, topics)):
        images_urls = NIP.get_image_urls(id)
        response = NIP.process_images(images_urls, topic)
        NIP.update_ai_name(id, response)
