from ProcessNotion import *
from LoadImagesTelegram import *

inc = False 
webmark = False

if __name__ == "__main__":
    notion_token = os.environ['NOTION_TOKEN']
    database_id = os.environ['DatabaseID']

    DW = NotionDatabaseDW(notion_token, database_id)
    results = DW.query_database()
    df = DW.extract_data_and_export_to_csv(results)
    df = DW.preprocess_df(df)
    filtered_df = DW.filter_df(df, inc)
    logging.info("Filtered DataFrame:")
    print(list(filtered_df['Date']))

    api_id = os.environ['API_ID']
    api_hash = os.environ['API_HASH']
    group_username = os.environ['GROUP_USERNAME']
    start_dates = list(filtered_df['Date'])

    downloader = TelegramImageDownloader(api_id, api_hash, group_username)

    loop = asyncio.get_event_loop()
    tlDfUrl = loop.run_until_complete(downloader.main(start_dates))
    print(tlDfUrl.keys())
    print(filtered_df['Date'].apply(lambda x: x.date()))
    filtered_df['img_urls'] = filtered_df['Date'].apply(
        lambda x: tlDfUrl[x.date()] if x.date() in tlDfUrl.keys() else [])

    for i in filtered_df.iterrows():
        print(i[1].keys())
        for url in i[1]['img_urls']:
            DW.add_image_to_page(page_id=i[1]['id'], image_url=url, webmark=webmark)
        if len(i[1]['img_urls']):
            DW.tick_lesson_checkbox(page_id=i[1]['id'])
        print(f'Submitted {i[1]["id"]}')
