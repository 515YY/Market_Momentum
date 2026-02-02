import pandas as pd
import json
import os
import numpy as np
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_MARKET = os.path.join(BASE_DIR, 'StockList.csv')
FILE_KNOWLEDGE_BASE = os.path.join(BASE_DIR, 'Stock_Knowledge_Base.json')
FILE_DASHBOARD_JS = os.path.join(BASE_DIR, 'dashboard_data.js')

def clean_code(x):
    x = str(x).strip()
    if x.startswith('="') and x.endswith('"'):
        return x[2:-1]
    return x

def run_update():
    
    concept_map = {}
    csv_path = 'c:/coding/code/Market_Momentum/concept_map.json'
    if os.path.exists(csv_path):
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                concept_map = json.load(f)
            print(f"Loaded concept tags for {len(concept_map)} stocks")
        except Exception as e:
            print(f"Warning: Could not load concept map: {e}")
    
    if not os.path.exists(FILE_MARKET):
        print(f"Error: {FILE_MARKET} not found.")
        return

    try:
        df_market = pd.read_csv(FILE_MARKET, encoding='utf-8-sig')
    except:
        df_market = pd.read_csv(FILE_MARKET, encoding='big5')
    
    df_market['Code'] = df_market['代號'].apply(clean_code)
    
    def is_valid_stock(row):
        industry = str(row.get('產業別', ''))
        if 'ETF' in industry or 'ETN' in industry or '存託憑證' in industry: return False
        return True

    if '產業別' in df_market.columns:
        df_market = df_market[df_market.apply(is_valid_stock, axis=1)]
    
    col_mappings = {
        'Change(%)': ['漲跌幅', '漲跌'],
        'Turnover(M)': ['成交額(百萬)', '成交額'],
        'Volume': ['成交量', '成交量(張)', '成交數', '成交張數'],
        'Turnover_Rate(%)': ['週轉率', '周轉率'],
        'Amplitude': ['振幅'],
        'Market_Cap': ['市值(億)', '市值'],
        'Price': ['成交價', '成交'] 
    }

    def find_col_name(keywords, columns):
        for kw in keywords:
            if kw in columns: return kw
            for col in columns:
                if kw in col: return col
        return None

    for target_key, keywords in col_mappings.items():
        found_col = None
        
        if target_key == 'Price':
             if '成交價' in df_market.columns: found_col = '成交價'
             elif '成交' in df_market.columns: found_col = '成交'
             else:
                 for col in df_market.columns:
                     if '成交' in col and '額' not in col and '量' not in col and '值' not in col:
                         found_col = col
                         break
        else:
            found_col = find_col_name(keywords, df_market.columns)
            
        if found_col:
            df_market[target_key] = pd.to_numeric(
                df_market[found_col].astype(str).str.replace(',', '', regex=False).str.replace('%', '', regex=False),
                errors='coerce'
            ).fillna(0)
        else:
            df_market[target_key] = 0
            print(f"Warning: Column for {target_key} not found.")

    all_stocks = []
    
    tag_stats = {}
    
    for index, row in df_market.iterrows():
        try:
            change = float(row['Change(%)'])
            turnover = float(row['Turnover(M)'])
            market_cap = float(row['Market_Cap'])
        except (ValueError, TypeError):
            continue
            
        sector = str(row.get('產業別', ''))
        stock_id = str(row['Code']).strip()
        name = str(row.get('名稱', row.get('Name', ''))).strip()
        
        stock_data = {
            'Code': str(row['Code']),
            'Name': row.get('名稱', row.get('Name', '')),
            'Price': row['Price'],
            'Change(%)': change,
            'Amplitude': row.get('Amplitude', 0),
            'Turnover(M)': turnover,
            'Volume': row.get('Volume', 0),
            'Turnover_Rate(%)': row.get('Turnover_Rate(%)', 0),
            'Market_Cap': market_cap,
            'Sector': sector if sector and sector != 'nan' else 'Unknown',
            'themes': [],
            'supply_chain': '' 
        }
        
    
        tags = []
             
        related_industry = str(row.get('相關產業', ''))
        if related_industry and related_industry != 'nan':
            raw_tags = related_industry.split(',')
            for t in raw_tags:
                t = t.strip()
                if not t: continue
                
                if t.startswith('櫃') or t.startswith('興'):
                    t = t[1:]
                
                clean_tag = t.replace('–', '-').replace('—', '-').replace('─', '-')
                
                if '-' in clean_tag:
                    sub_tag = clean_tag.split('-')[-1].strip()
                    if sub_tag and sub_tag not in tags:
                        tags.append(sub_tag)
                else:
                    if t not in tags:
                        tags.append(t)
        
        stock_data['themes'] = tags
        
        concept_tags = []
        if stock_id in concept_map:
            concept_tags = sorted(list(concept_map[stock_id]))
            
        stock_data['concepts'] = concept_tags
        
        all_stocks.append(stock_data)

        combined_tags = set(tags + concept_tags)
        
        for tag in combined_tags:
            if tag not in tag_stats:
                tag_stats[tag] = {
                    'total_turnover': 0,
                    'weighted_change_sum': 0,
                    'market_cap_sum': 0,
                    'count': 0,
                    'up_count': 0
                }
            
            stats = tag_stats[tag]
            stats['total_turnover'] += turnover
            stats['weighted_change_sum'] += change * turnover
            stats['market_cap_sum'] += market_cap
            stats['count'] += 1
            if change > 0:
                stats['up_count'] += 1
        
    theme_stats = []
    for tag_name, stats in tag_stats.items():
        total_turnover = stats['total_turnover']
        avg_change = stats['weighted_change_sum'] / total_turnover if total_turnover > 0 else 0
        up_ratio = stats['up_count'] / stats['count'] if stats['count'] > 0 else 0
        
        theme_stats.append({
            'name': tag_name,
            'count': stats['count'],
            'market_cap_flow': round(stats['total_turnover'], 2), 
            'avg_change': round(avg_change, 2),
            'up_ratio': round(up_ratio, 2)
        })
    
    theme_stats.sort(key=lambda x: x['avg_change'], reverse=True)
    
    final_data = {
        'last_updated': time.strftime("%Y-%m-%d %H:%M:%S"),
        'themes': theme_stats,
        'stocks': all_stocks
    }
    
    with open(FILE_DASHBOARD_JS, 'w', encoding='utf-8') as f:
        json_str = json.dumps(final_data, ensure_ascii=False)
        f.write(f"window.DASHBOARD_DATA = {json_str};")

if __name__ == '__main__':
    run_update()
