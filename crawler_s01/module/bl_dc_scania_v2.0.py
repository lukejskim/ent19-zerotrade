from selenium import webdriver as wd
from bs4 import BeautifulSoup as bs

from selenium.webdriver.common.by import By

# 명시적 대기를 위해
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from IPython.display import Image

import numpy as np
import pandas as pd
import platform
import time
import sys


def get_device_info(td_tags):
    device_info = dict()
    td_tags_0 = td_tags[0].get_text().strip()    # 순번, ord_no
    td_tags_1 = td_tags[1].get_text().strip()    # 브랜드, brand
    td_tags_2 = td_tags[2].get_text().strip()    # 부품그룹, device_grp
    td_tags_3 = td_tags[3].get_text().strip()    # 부품번호, device_no
    td_tags_4 = td_tags[4].get_text().strip()    # 부품명(한글), device_nm_kr
    td_tags_5 = td_tags[5].get_text().strip()    # 부품명(영문), device_nm_en
    td_tags_6 = td_tags[6].get_text().strip()    # 가격(VAT별도), price
    td_tags_6 = td_tags_6.replace(',' , '')
    td_tags_6 = td_tags_6.replace('\\', '')
    td_tags_6 = td_tags_6.strip()
    
    # 숫자형
    td_tags_0 = int(td_tags_0)
    td_tags_6 = int(td_tags_6)
    
    
    device_info['ord_no'      ] = td_tags_0
    device_info['brand'       ] = td_tags_1
    device_info['device_grp'  ] = td_tags_2
    device_info['device_no'   ] = td_tags_3
    device_info['device_nm_kr'] = td_tags_4
    device_info['device_nm_en'] = td_tags_5
    device_info['price'       ] = td_tags_6
    
    return device_info


def get_device_list(tr_tags):
    device_list = list()
    
    tr_cnt = len(tr_tags)
    if tr_cnt == 0:
        return 
    
    for i in range(tr_cnt):
        td_tags = tr_tags[i].find_all('td')
        device_info = get_device_info(td_tags)
        device_list.append(device_info)
    
    return device_list


def get_device_list_by_page(start_pg, end_pg):
    device_list_total = list()
    
    page_url = 'http://221.143.43.214/index.html?page={}&key=Y&brend={}&series2=&&series3=&part_no=&type1=&type2='
    
    for navi_page in range(start_pg, end_pg+1):
        param_page  = navi_page
        param_brend = 'SCANIA'
        driver.get(page_url.format(param_page, param_brend))
        
        time.sleep(1)
        html = driver.page_source
        soup = bs(html, "lxml")
        
        table_tag = soup.find('table', 'tbl2')
        tbody_tag = table_tag.find('tbody')
        tr_tags = tbody_tag.find_all('tr')
        tr_cnt = len(tr_tags)
        
        if tr_cnt > 0:
            device_list = list()
        else:
            break
        
        device_list = get_device_list(tr_tags)
        
        device_list_total.extend(device_list)
    
    return device_list_total


