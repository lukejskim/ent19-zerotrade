from selenium import webdriver as wd
from bs4 import BeautifulSoup as bs

from selenium.webdriver.common.by import By
from tqdm import tqdm_notebook

# 명시적 대기를 위해
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from IPython.display import Image

import numpy as np
import pandas as pd
import platform
import time
import sys
import csv
import re

class BlVolvo:

    def get_driver(self):
        # 드라이브 로드
        if platform.system() == 'Darwin':    # MacOS
            driver = wd.Chrome(executable_path='./driver/chromedriver')      
        elif platform.system() == 'Windows': # Windows
            driver = wd.Chrome(executable_path='./driver/chromedriver.exe')    
        else:
            print("It's unknown system. Hangul fonts are not supported!")
        
        return driver
       

        
    def get_lastpage(self, driver, schBrand='1'):       
        '''
        Get a lastpage by brand
        Args:  
            driver : obj, web driver instance
            schBrand : str, value of brand code    
                       cf. 1:볼보트럭, 2:유디트럭  
        Returns:
            last_page  : int, page number
        '''
        last_page = 0

        target_url = 'http://parts.volvotruck.kr/main.html?schWord=&schBrand={}&schGroup1=&schGroup2=&schCarType=&page={}'
        # schBrand = schBrand      # 1:볼보트럭, 2:유디트럭  
        # schPage  = 1
        # driver.get(target_url.format(schBrand, schPage))
        driver.get(target_url.format(schBrand, 1))

        html = driver.page_source
        soup = bs(html, "lxml")


        # 마지막 네비게이션페이지 링크 확인
        tmp = soup.find('a', 'first_back')

        if tmp is None:
            print('데이터가 많지 않습니다.')
        else :
            lastlink = tmp['href']

            page = re.search('page=\d+', lastlink)

            if page is None:
                last_page = 1
            else:
                last_page = page.group()[5:]
                last_page = int(last_page)

            result_cnt = last_page * 10
            brand_nm = (lambda schBrand : '볼보트럭' if schBrand == '1' else '유디트럭' if schBrand == '2' else '모든트럭')(schBrand)

            print('{} 데이터수는 약 {}건이며, 마지막 페이지는 {}입니다.'.format(brand_nm, result_cnt, last_page))

        return last_page



    def is_number(self, value):
        '''
        Check whether the value is a number
        
        Args:  
            value : str, value to check 
        Returns: 
            chk_num : bool, True/False
        '''    
        
        chk_num = True
        num_chk_list = list('0123456789')

        for char in str(value):
            is_num = char in num_chk_list
            chk_num *= is_num
            if not is_num:
                break

        return chk_num
    
    
    def get_device_info(self, td_tags):
        '''
        Get informations of a device data
        Args:  
            td_tags : list, column data of a device in the table
        Returns: 
            device_info : dict, parcing data
        '''    
        
        shift = -1
        device_info = dict()
        td_tags_0 = ''  # td_tags[0].get_text().strip()    # 순번, ord_no
        td_tags_1 = td_tags[1+shift].get_text().strip()    # 브랜드, brand
        td_tags_2 = td_tags[2+shift].get_text().strip()    # 부품그룹, device_grp
        td_tags_3 = td_tags[3+shift].get_text().strip()    # 부품번호, device_no
        td_tags_4 = td_tags[4+shift].get_text().strip()    # 부품명(한글), device_nm_kr
        td_tags_5 = td_tags[5+shift].get_text().strip()    # 부품명(영문), device_nm_en
        td_tags_6 = td_tags[6+shift].get_text().strip()    # 가격(VAT별도), price
        td_tags_6 = td_tags_6.replace(',' , '')
        td_tags_6 = td_tags_6.replace('\\', '')
        td_tags_6 = td_tags_6.strip()
        td_tags_7 = td_tags[7+shift].get_text().strip()    # 적용일, update_dt

        # 숫자형
        # td_tags_0 = int(td_tags_0)
        # td_tags_6 = int(self.is_number(td_tags_6))


        device_info['ord_no'      ] = td_tags_0
        device_info['brand'       ] = td_tags_1
        device_info['device_grp'  ] = td_tags_2
        device_info['device_no'   ] = td_tags_3
        device_info['device_nm_kr'] = td_tags_4
        device_info['device_nm_en'] = td_tags_5
        device_info['price'       ] = td_tags_6
        device_info['update_dt'   ] = td_tags_7

        return device_info

    

    def get_device_list(self, tr_tags):
        '''
        Get informations of a device data
        Args:  
            tr_tags : list, device data list of a navigation page 
        Returns: 
            device_list : list[of dict], parcing data by page
        '''    
        
        device_list = list()

        tr_cnt = len(tr_tags)
        if tr_cnt == 0:
            return 

        for i in range(tr_cnt):
            td_tags = tr_tags[i].find_all('td')
            device_info = self.get_device_info(td_tags)
            device_list.append(device_info)

        return device_list

    

    def get_device_list_by_page(self, driver, brand_cd, start_pg, end_pg):
        '''
        Get informations of page ranges
        Args:  
            driver : obj, web driver instance
            brand_cd : str, brand code of volvo     cf. 1:볼보트럭, 2:유디트럭  
            start_pg : int, start page of gathering data 
            end_pg   : int, end page of gathering data
        Returns: 
            device_list_total : list[of dict], parcing data of page ranges
        '''    

        device_list_total = list()

        page_url = 'http://parts.volvotruck.kr/main.html?schWord=&schBrand={}&schGroup1=&schGroup2=&schCarType=&page={}'

        for navi_page in tqdm_notebook(range(start_pg, end_pg+1)):
            sch_brand  = brand_cd
            param_page = navi_page
            driver.get(page_url.format(sch_brand, param_page))

            time.sleep(1)
            html = driver.page_source
            soup = bs(html, "lxml")

            table_tag = soup.find('table', 'ta_list')
            tbody_tag = table_tag.find('tbody')
            tr_tags = tbody_tag.find_all('tr')
            tr_cnt = len(tr_tags)

            if tr_cnt > 0:
                device_list = list()
            else:
                break

            device_list = self.get_device_list(tr_tags)

            device_list_total.extend(device_list)

        return device_list_total
    
    


    def save_dict_to_csv(self, device_list_total, dirname='data', filename='scania_data.csv'):
        '''
        Save crawling data to csv file
        Args:  
            device_list_total : list[of dict], parcing data of page ranges
            dirname  : str, folder name
            filename : str, file name 
        Returns: 
            csv_file : str, full path of saved files
            ret_msg  : str, result message
        '''    
        
        # csv_columns = [ 'ord_no', 'brand', 'device_grp', 'device_no', 'device_nm_kr', 'device_nm_en', 'price' ]
        csv_columns = [ 'ord_no', 'brand', 'device_grp', 'device_no', 'device_nm_kr', 'device_nm_en', 'price', 'update_dt' ]
        dict_data = device_list_total

        if not dirname.endswith('/'):
            dirname += '/'

        if not filename.endswith('.csv'):
            filename += '.csv'

        csv_file = dirname + filename
        ret_msg = '성공적으로 저장되었습니다! '
        
        try:
            with open(csv_file, 'w', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                writer.writeheader()
                for data in dict_data:
                    writer.writerow(data)
        except IOError:
            print("I/O error") 
            
        return csv_file, ret_msg

    

    def chk_module(self, msg):
        if msg is None:
            msg = 'No Param'
            
        return msg
    
