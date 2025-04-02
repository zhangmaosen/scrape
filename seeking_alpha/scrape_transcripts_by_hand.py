from time import sleep
from playwright.sync_api import sync_playwright
import shutil
import json
import os

def save_progress(progress_file, last_target_index, last_item_index):
    with open(progress_file, 'w') as f:
        json.dump({'last_target_index': last_target_index,
                   'last_item_index': last_item_index}, f)
        f.flush()

def load_progress(progress_file):
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            progress = json.load(f)
            return (progress.get('last_target_index', 0), progress.get('last_item_index', 0))
    return 0

def scrape_seeking_alpha():
    progress_file = 'progress.json'
    last_target_index, last_item_index = load_progress(progress_file)

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(user_data_dir="C:/Users/hadoo/new", 
                                                       headless=False,
                                                       args=['--disable-blink-features=AutomationControlled'],
                                                       viewport={"width": 1280, "height": 1600})
        page = browser.new_page()
        
        page.goto("https://seekingalpha.com/")
        page.wait_for_load_state('networkidle')
        
        with open('sp_500_transcript_list.json', 'r') as json_f:
            json_data = json_f.read()
            target_list = json.loads(json_data)
        
        url_tpl = "https://seekingalpha.com/{}"
        all_transcripts = []
            
        with open('sp500_transcripts.json', 'a+', encoding='utf8') as out_f:
            out_f.seek(0, os.SEEK_END)
            if out_f.tell() == 0:
                out_f.write("[\n")
            else:
                out_f.seek(out_f.tell() - 2, os.SEEK_SET)  # Move back to overwrite the last comma
            
            for index, target in enumerate(target_list):
                if index < last_target_index:
                    continue  # Skip already processed targets
                
                items = target['data']
                for iid, item in enumerate(items):
                    if iid < last_item_index:
                        continue
                    if item['type'] != 'transcript':
                        continue
                    url = url_tpl.format(item['links']['self'])
                    print(f"url is {url}")
                    page.goto(url)
                    page.wait_for_load_state('networkidle')
                    paragraph = page.query_selector('div.contents div[data-test-id="content-container"]')
                    if paragraph:
                        paragraph_text = page.evaluate("(element) => element.textContent", paragraph)
                        print(paragraph_text)
                    else:
                        print("No content found")
                        continue

                    title = page.query_selector('div.contents h1')
                    if title:
                        title_text = page.evaluate("(element) => element.textContent", title)
                        print(title_text)
                    all = {'content': {'title': title_text, 'content': paragraph_text}} | item
                    sleep(5)
                    all_transcripts.append(all)
                    out_f.write(json.dumps(all, ensure_ascii=False, indent=4))
                    out_f.write(",\n")
                    out_f.flush()
                    save_progress(progress_file, index, iid + 1)  # Save progress after processing each target
                save_progress(progress_file, index + 1, 0)
            out_f.seek(out_f.tell() - 2, os.SEEK_SET)  # Move back to overwrite the last comma
            out_f.write("\n]")
        
        page.wait_for_timeout(5000)
        browser.close()

if __name__ == "__main__":
    scrape_seeking_alpha()