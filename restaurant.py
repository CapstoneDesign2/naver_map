from unittest import result
import requests, json, os, sys, time
from unittest import result
from playwright.sync_api import Playwright, sync_playwright


import pandas as pd
import numpy as np
import math
import json
import matplotlib.pyplot as plt
import seaborn as sns
import time
import re
from bs4 import BeautifulSoup

#f2 = open("page2.html", "w")
# fvwqf 버튼 class

# https://map.naver.com/v5/api/search?caller=pcweb&query=%EC%8B%A0%EC%B4%8C%20%EC%B9%B4%ED%8E%98&page=10
# 한 가게의 url 은 다음과 같은 구조로 된다.
# https://map.naver.com/v5/entry/place/{가게 id}
# 가게 url 에 들어가서 더보기 click 한 다음에 graphql을 지속적으로 받아오면 될꺼 같음
# https://pcmap.place.naver.com/restaurant/1391453544/review/visitor
# 들어가서 더보기 button 찾아서 클릭하면 된다.

LABEL_MAPPING_TABLE ={
    '가성비가 좋아요' : '가성비',
    
    '매장이 청결해요' : '청결',
    '화장실이 깨끗해요' : '청결',
    
    '디저트가 맛있어요' : '맛',
    '커피가 맛있어요' : '맛',
    '음료가 맛있어요' : '맛',
    '특별한 메뉴가 있어요' : '맛',
    
    '인테리어가 멋져요' : '분위기',
    '뷰가 좋아요' : '분위기',
    '대화하기 좋아요' : '분위기',
    '사진이 잘 나와요' : '분위기',
    '좌석이 편해요' : '분위기',
    
    '친절해요' : '친절'
}

LABEL_COLUMNS = ['가성비', '청결', '맛', '분위기', '친절']

def one_store_id_get(data):
    global store_list
    # for datum in data:
    #print(datum['id'], file=f)
    store_list.extend([x['id'] for x in data])
    time.sleep(0.5)


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


def from_one_store_comment(id, playwright):
    BASE_URL = f'https://pcmap.place.naver.com/restaurant/{id}/review/visitor'
    # 이제 여기서 처리한다.
    print(BASE_URL)

    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    
    # 페이지 열었다.
    page = context.new_page()
    page.goto(BASE_URL)
    #context.tracing.start(screenshots=True, snapshots=True)
    
    
    lim = 0
    while lim < 10000:
        try:
            #print(page.locator('.fvwqf').count())
            page.locator('.fvwqf').click(timeout = 1000)
            print(lim)
            #print()
            #if cnt == 0:
            #    break
            lim+=1
        except:
            break
    print('click ended!\n')
    reviewCounter = page.locator('.YeINN').count()
    
    for idx in range(0, reviewCounter):
        comment_box = page.locator('.YeINN').nth(idx)
        #print(comment_box.locator('.ZZ4OK').text_content(timeout=1000))
        print(f'writing {idx} comment')
        # 더보기 클릭시도
        comment = ""
        label_count = 0
        
        try:
            comment_box.locator('.ZGKcF').click(timeout=1000)
        except:
            pass
            #print('라벨 더보기 없음')
        
        try:
            comment_box.locator('.rvCSr').click(timeout=1000)
        except:
            pass
            #print('더보기 없음')
        
        # 댓글 가져오기
        try:
            comment = comment_box.locator('.ZZ4OK').locator('.zPfVt').text_content(timeout=1000)
        except:
            pass
        
        # 댓글 길이 check해서 짧으면 continue
        
        if len(comment) < 3:
            continue
        
        
        # 라벨 가져오기        
        try:
            label_count = comment_box.locator('.gyAGI').locator('.P1zUJ').count()
        except:
            pass
        
        #print(label_count)
        #print(comment_box.locator('.gyAGI').locator('.P1zUJ').nth(0).text_content(timeout=1000))
        dictionary_label = {
            '가성비' : 0,
            '청결' : 0,
            '맛' : 0,
            '분위기' : 0,
            '친절' : 0
        }
        
        for i in range(0, label_count):
            try:
                #print(comment_box.locator('div.gyAGI').text_context(timeout=1000))
                one_label = comment_box.locator('.gyAGI').locator('.P1zUJ').nth(i).text_content(timeout=1000)
                #print(one_label)
                if one_label in LABEL_MAPPING_TABLE.keys():
                    dictionary_label[LABEL_MAPPING_TABLE[one_label]] += 1
            except:
                print('이게 아닌데;;')
        
        #comment_box.locator('.zPfVt').text_content(timeout=1)
        comment = comment.replace('\n', ' ') # 엔터 스페이스바로 바꾸기
        print(comment, '\t'.join([str(x) for x in dictionary_label.values()]),file=f1, sep='\t')
        
        #print('\t'.join())
        
        #for i in dictionary_label.values():
        #    print(comment, file=f1, end='\t')
        
        #print(dictionary_label, file=f1)
        
    #context.tracing.stop(path = "trace.zip")
    print(reviewCounter)
    
def main():
    global browser
    
    make_store_list()
    with sync_playwright() as playwright:
        for idx ,id in enumerate(store_list):
            from_one_store_comment(id, playwright)
            print(f'finised number {idx} store')
    


def make_store_list():
    global query

    page_cnt = 1
    while True:
        print(f'now looking at page : {page_cnt}')
        if not one_page_url(query, page_cnt):
            break
        page_cnt += 1




if __name__ == "__main__":
    store_list = []
    f1 = open("page.txt", "w")
    print('댓글\t가성비\t청결\t맛\t분위기\t친절', file=f1)
    query = input("키워드 입력 ㄱㄱ : ")

    # print(store_list)
    # print(len(store_list))
    # 1452440066 // 카페 언더우드

    main()    
    #for i in 
    # https://pcmap.place.naver.com/restaurant/1946991741/review/visitor
    #https://pcmap.place.naver.com/restaurant/19796689/review/visitor
    #with sync_playwright() as playwright:
    #    from_one_store_comment(19796689, playwright)

    f1.close()
