# Telegram Images Downloader and Notion Database Updater

This repository contains a Python script that downloads images from a Telegram group and updates a Notion database with the images.

## Requirements

The following packages are required to run the script:

- telethon
- notion-client
- pandas
- tqdm
- cloudinary

You can install these packages using pip:

```
pip install telethon notion-client pandas tqdm cloudinary
```

You will also need API keys for Telegram and Notion.

## How to use

1. Clone the repository:

```
git clone https://github.com/<username>/Telegram-Images-Downloader-and-Notion-Database-Updater.git
```

2. Set up environment variables for the API keys:

```
export API_ID=<Telegram API ID>
export API_HASH=<Telegram API HASH>
export NOTION_TOKEN=<Notion API Key>
export DatabaseID=<Notion Database ID>
export GROUP_USERNAME=<Telegram Group username>
```

3. Run the script:

```
python main.py
```

The script will download the images from the Telegram group and add them to the relevant pages in the Notion database. The script will also log information about the status of each step of the process.

## Customization

You can customize the script to fit your specific needs. For example, you can modify the filtering criteria for the Notion database, or change the directory to save the images.

## Conclusion

This script provides a simple solution for downloading images from a Telegram group and updating a Notion database with the images. By using this script, you can automate the process of updating your Notion database with the images from a Telegram group.