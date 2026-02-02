import requests
from bs4 import BeautifulSoup
import time
import random
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DOMAIN = "https://concords.moneydj.com/z/zg/zge/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def clean_code(x):
    return str(x).strip()

def scrape_category(cat):
    name = cat['name']
    tag = cat['tag']
    suffix = cat['url_suffix']
    
    if 'djhtm' in suffix:
            url = f"https://concords.moneydj.com/z/zg/zge/{suffix}"
    else:
            url = f"https://concords.moneydj.com/z/zg/zge/zge_{suffix}_1.djhtm"
            
    print(f"Scraping '{name}'...")
    
    local_map = {}
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.encoding = 'big5'
        
        matches = re.findall(r"GenLink2stk\('AS(\d{4})','(.*?)'\)", resp.text)
        
        if matches:
            for m in matches:
                stock_id = m[0]
                local_map[stock_id] = tag
                
    except Exception as e:
        print(f"Error scraping {name}: {e}")
        
    return local_map

def scrape_all():
    if not os.path.exists('temp_categories.json'):
        print("Categories file not found.")
        return

    with open('temp_categories.json', 'r', encoding='utf-8') as f:
        categories = json.load(f)
        
    stock_tag_map = {} 
    
    total = len(categories)
    print(f"Starting parallel scrape for {total} categories...")
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(scrape_category, cat): cat for cat in categories}
        
        count_done = 0
        for future in as_completed(futures):
            count_done += 1
            cat_data = future.result()
            
            for sid, tag in cat_data.items():
                if sid not in stock_tag_map:
                    stock_tag_map[sid] = set()
                stock_tag_map[sid].add(tag)
                
            if count_done % 10 == 0:
                print(f"Progress: {count_done}/{total} done...")
                
    final_map = {k: list(v) for k, v in stock_tag_map.items()}
    
    print(f"Finished. Total unique stocks found: {len(final_map)}")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, 'concept_map.json')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_map, f, ensure_ascii=False, indent=2)
        print(f"Saved to {output_path}")

if __name__ == "__main__":
    scrape_all()
