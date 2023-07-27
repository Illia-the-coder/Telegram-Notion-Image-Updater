import os
import logging
import pandas as pd
from notion_client import Client
from PDFCreator import create_pdf

def get_image_urls(page_id):
    """
    Retrieves a list of image URLs from a Notion page.

    Args:
        page_id (str): The ID of the Notion page.

    Returns:
        list: List of image URLs.
    """
    try:
        # Initialize Notion client
        notion = Client(auth=os.environ.get("NOTION_TOKEN"))

        # Retrieve the page
        page = notion.pages.retrieve(page_id)

        # Get list of image URLs
        image_urls = []
        children = notion.blocks.children.list(block_id=page_id).get("results")
        for child in children:
            if child["type"] == "image":
                if child["image"].get("type") == "external":
                    image_urls.append(child["image"]["external"]["url"])
                elif child["image"].get("type") == "file":
                    image_urls.append(child["image"]["file"]["url"])
            elif child['type'] == "embed":
                image_urls.append(child["embed"]['url'])
        return image_urls

    except Exception as e:
        # Handle API limit or other exceptions here
        raise Exception(f"Error while retrieving image URLs for page_id={page_id}: {str(e)}")

def create_pdf_by_notion_id(notion_id, grade, name):
    """
    Creates a PDF using image URLs from a Notion page and logs the process.

    Args:
        notion_id (str): The ID of the Notion page.
        grade (str): The grade associated with the PDF.
        name (str): The name of the PDF file.
    """
    try:
        images = get_image_urls(notion_id)
        logging.info(f"create_pdf_by_notion_id called with id={notion_id}, grade={grade}, name={name}")
        logging.info(f"Found {len(images)} images for notion_id={notion_id}, grade={grade}, name={name}")

        if len(images):
            create_pdf(images, grade, name)
            logging.info(f"PDF creation successful for notion_id={notion_id}, grade={grade}, name={name}")
        else:
            logging.warning(f"No images found for notion_id={notion_id}, grade={grade}, name={name}")

    except Exception as e:
        # Log any exception that occurred during PDF creation
        logging.error(f"Error creating PDF for notion_id={notion_id}, grade={grade}, name={name}: {str(e)}")

def main():
    # Set up logging
    logging.basicConfig(filename='pdf_creation.log', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    try:
        df = pd.read_csv('local_database.csv')
        for index, row in df.iterrows():
            create_pdf_by_notion_id(row['id'], row['Grade'], row['Date'])

    except Exception as e:
        # Log any exception that occurred during the main process
        logging.error(f"An error occurred during the main process: {str(e)}")

if __name__ == "__main__":
    main()
