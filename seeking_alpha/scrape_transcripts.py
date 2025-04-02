import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
import json
from time import sleep
async def main():
    schema = {
        "name": "Example Items",
        "baseSelector": 'div.contents',
        "fields": [
            {"name": "title", "selector": 'h1', "type": "text"},
            {"name": "content", "selector": 'div[data-test-id="content-container"]', "type": "text"},
            
        ]
    }
    # 1) Reference your persistent data directory
    browser_config = BrowserConfig(
        headless=False,             # 'True' for automated runs
        verbose=True,
        use_managed_browser=True,  # Enables persistent browser strategy
        browser_type="chromium",
        user_data_dir="C:/Users/hadoo/my_profile"
    )

    # 2) Standard crawl config
    crawl_config = CrawlerRunConfig(
        # scan_full_page=True,  # Scan the entire page for data
        # scroll_delay=3,
        extraction_strategy=JsonCssExtractionStrategy(schema),
        #magic=True,  # Use magic to extract data from the page
        delay_before_return_html=25,  # Wait for the element to be present before extracting data
        #simulate_user=True,
        #wait_for='div[data-test-id="content-container"]',
        semaphore_count=1,
        #override_navigator=True
        #wait_for_images=True,
    )
    
    with open('sp_500_transcript_list.json', 'r') as json_f:
        json_data = json_f.read()
        target_list = json.loads(json_data)
        #print(f"target_list is {target_list}")
    
    url_tpl = "https://seekingalpha.com/{}"

    all_transcripts = []
    
    with open('sp500_transcripts.json', 'w+', encoding='utf8') as out_f:
        out_f.write("[\n")
        
        async with AsyncWebCrawler(config=browser_config) as crawler:
            for target in target_list:
                items = target['data']
                for item in items:
                    if item['type'] != 'transcript':
                        continue
                    #print(f"item is {item}")
                    url = url_tpl.format(item['links']['self'])
                    print(f"url is {url}")
                    result = await crawler.arun(url=url, config=crawl_config)
                    if result.success:
                        print(f"len(result.extracted_content) is {len(result.extracted_content)}")
                        if len(result.extracted_content) <= 5:
                            print(f"Error: No content extracted for {url}")
                            return
                        all = {'content' :result.extracted_content, 'raw': result.html[:150]} | item 
                        all_transcripts.append(all)
                        #print("Successfully accessed private data with your identity!")
                        out_f.write(json.dumps(all, ensure_ascii=False, indent=4))
                        out_f.write(",\n")
                        out_f.flush()
                    else:
                        print("Error:", result.error_message)
        out_f.write("]")
    # with open('output_transcripts.json', 'w+') as f:
    #     json.dump(all_transcripts, f, indent=4)
if __name__ == "__main__":
    asyncio.run(main())