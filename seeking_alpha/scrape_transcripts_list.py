import asyncio
from time import sleep
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
import re, json
from tickers import dow_jones,sp_500
async def main():
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

        
    )
    
    url_tpl= "https://seekingalpha.com/api/v3/symbols/{}/transcripts?filter[until]=0&id={}&include=author%2CprimaryTickers%2CsecondaryTickers%2Csentiments&isMounting=true&page[size]=40&page[number]={}"

    async with AsyncWebCrawler(config=browser_config) as crawler:
        tickers = dow_jones
        
        scraped_data = []
        for ticker in tickers:
            id = 1
            while True:
                sleep(5)
                url = url_tpl.format(ticker, ticker, id)
                print(f"id is {id}， url is {url}")
                try:
                    result = await crawler.arun(url=url, config=crawl_config)
                    if result.success:
                        pattern = r'<pre>(.*)</pre>'
                        json_str = re.search(pattern, result.html, re.DOTALL)
                        #print(json_str.group(1))
                        out_put = json.loads(json_str.group(1))
                        scraped_data.append(out_put)
                        total_page = out_put['meta']['page']['totalPages']
                        print("total_page is", total_page)
                        if id >= total_page:
                            break
                        else:
                            id += 1
                    else:
                        print("Error:", result.error_message)
                except Exception as e:
                    print(f"Error occurred: {e}")
                    

        with open('sp_500_list_output.json', 'w+') as f:
            json.dump(scraped_data, f, indent=4)
if __name__ == "__main__":
    asyncio.run(main())