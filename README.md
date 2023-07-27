# Telegram Images Downloader and Notion Database Updater

![Telegram Notion Image Updater](https://github.com/Illia-the-coder/Telegram-Notion-Image-Updater/blob/main/assets/101904816/6d08bf33-e642-4654-9bbc-2d5fdd454a3c.png)

This repository contains a Python script that downloads images from a Telegram group and updates a Notion database with the images. It also includes functionality to generate PDFs from the downloaded images.

## Scheme of Scenario of Code

![Scenario of Code](https://github.com/Illia-the-coder/Telegram-Notion-Image-Updater/blob/main/assets/101904816/f264c30e-9e0b-4bc8-a0a7-26c49a162c86.png)

## Requirements

The following packages are required to run the script:

- telethon
- notion-client
- pandas
- tqdm
- cloudinary
- img2pdf

You can install these packages using pip:

```
pip install telethon notion-client pandas tqdm cloudinary img2pdf
```

You will also need API keys for Telegram and Notion.

## How to Use

1. Clone the repository:

```
git clone https://github.com/Illia-the-coder/Telegram-Notion-Image-Updater.git
```

2. Set up environment variables for the API keys:

```
export API_ID=<Telegram API ID>
export API_HASH=<Telegram API HASH>
export NOTION_TOKEN=<Notion API Key>
export DATABASE_ID=<Notion Database ID>
export GROUP_USERNAME=<Telegram Group username>
```

3. Run the script:

```
python main.py
```

The script will download the images from the Telegram group and add them to the relevant pages in the Notion database. The script will also log information about the status of each step of the process.

4. To generate PDFs from the downloaded images, run the following command:

```
python generate_pdfs.py
```

This will create a PDF file for each page in the Notion database that contains images. The PDFs will be saved in the `pdfs` directory.

## Customization

You can customize the script to fit your specific needs. For example, you can modify the filtering criteria for the Notion database, change the directory to save the images, or modify the settings for generating the PDFs.

## Conclusion

This script provides a simple solution for downloading images from a Telegram group and updating a Notion database with the images. By using this script, you can automate the process of updating your Notion database with the images from a Telegram group, and also generate PDFs from the downloaded images for easy sharing and storage. 

## Acknowledgements

This project was inspired by [this article ↗](https://towardsdatascience.com/how-to-scrape-a-telegram-group-and-store-messages-to-a-database-3290f25d8d64) by David Mezzetti. Special thanks to [notion-sdk-py ↗](https://github.com/ramnes/notion-sdk-py) for the Notion integration, [telethon ↗](https://github.com/LonamiWebs/Telethon) for the Telegram integration, and [img2pdf ↗](https://github.com/josch/img2pdf) for the PDF generation.
