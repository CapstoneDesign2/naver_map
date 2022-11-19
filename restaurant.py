from unittest import result
import requests, json, os, sys, time
from unittest import result
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from seleniumwire import webdriver as wired_webdriver
from selenium.webdriver import FirefoxOptions
import pandas as pd
import numpy as np
import math
import json
import matplotlib.pyplot as plt
import seaborn as sns
import time
import re
from bs4 import BeautifulSoup

f1 = open("page.txt", "w")
#f2 = open("page2.html", "w")
# fvwqf 버튼 class

# https://map.naver.com/v5/api/search?caller=pcweb&query=%EC%8B%A0%EC%B4%8C%20%EC%B9%B4%ED%8E%98&page=10
# 한 가게의 url 은 다음과 같은 구조로 된다.
# https://map.naver.com/v5/entry/place/{가게 id}
# 가게 url 에 들어가서 더보기 click 한 다음에 graphql을 지속적으로 받아오면 될꺼 같음
# https://pcmap.place.naver.com/restaurant/1391453544/review/visitor
# 들어가서 더보기 button 찾아서 클릭하면 된다.


def one_store_id_get(data):
    global store_list
    # for datum in data:
    #print(datum['id'], file=f)
    store_list.extend([x['id'] for x in data])
    time.sleep(1)


def one_page_url(query, page_cnt):

    URL = f"https://map.naver.com/v5/api/search?caller=pcweb&query={query}&page={page_cnt}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36'
    }

    try:
        res = requests.get(URL, headers=headers).json()
        one_store_id_get(res['result']['place']['list'])
        return True
    except:
        return False
    # list에 가게들 있는거 같음
    # print(res['result']['place']['list'])


def from_one_store_comment(id, browser):
    BASE_URL = f'https://pcmap.place.naver.com/restaurant/{id}/review/visitor'
    # 이제 여기서 처리한다.
    print(BASE_URL)

    browser.get(BASE_URL)
    
    cnt=0
    while True:
        try:
            more = browser.find_element(
                By.XPATH, '//*[@id="app-root"]/div/div/div/div[7]/div[2]/div[3]/div[2]/a')
            more.click()
            print(f'loop count is {cnt}!')
            #del browser.requests
            cnt+=1
                # 되는거 같으니 network 움직임 분석
        except:
            #print("exception")
            break
    try:
        comment_boxes = browser.find_elements(By.CLASS_NAME, 'YeINN')
    except:
        return
    
    for comment_box in comment_boxes:
        #print(type(comment_box))
        comment = ""
        eval_list = []
        
        # 더보기 건지기
        try:
            comment_box.find_element(By.CLASS_NAME, 'rvCSr')
            comment_box.find_element(By.CLASS_NAME, 'rvCSr').click()
        except:
            pass
            #print('no 더보기')
        
        # 평가 더보기 건지기
        try: 
            comment_box.find_element(By.CLASS_NAME, 'ZGKcF')
            comment_box.find_element(By.CLASS_NAME, 'ZGKcF').click()
        except:
            pass
            #print('no 평가 더보기')
        
        try:
            comment_text = comment_box.find_element(By.CLASS_NAME, 'zPfVt')
            comment = comment_text.text
            #print(comment_text.text)
        except:
            pass
            #print("리뷰 내용 없음")
        
        try:
            eval_list = comment_box.find_element(By.CLASS_NAME ,'gyAGI').find_elements(By.CLASS_NAME, 'P1zUJ')
        except:
            pass
            #print("태그 없음")
        
        eval_list = [x.text for x in eval_list]
        comment = comment.replace('\n', ' ')
        # comment : 댓글 내용
        # eval_list : 평가 항목
        
        print(comment, eval_list, file=f1)
        #print(eval_list)
    
    
    
    
    


def main():
    # make_store_list()
    global browser
    for id in store_list:
        from_one_store_comment(id, browser)
    pass


def make_store_list():
    global query

    page_cnt = 1
    while True:
        print(f'now looking at page : {page_cnt}')
        if not one_page_url(query, page_cnt):
            break
        page_cnt += 1


store_list = []

#query = input("키워드 입력 ㄱㄱ : ")

# print(store_list)
# print(len(store_list))
# 1452440066 // 카페 언더우드

webdriver_service = Service('/usr/bin/geckodriver')

opts = FirefoxOptions()
opts.add_argument("--headless")		# turn off GUI
browser = wired_webdriver.Firefox(service=webdriver_service, options=opts)

#main()

#for i in 
from_one_store_comment(1137614062, browser)

f1.close()
