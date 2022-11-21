from unittest import result
import requests, json, os, sys, time
from unittest import result
from playwright.sync_api import Playwright, sync_playwright


import pandas as pd
import numpy as np
import math
import json
import time
import random
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

store_list = []
review_list = []
TOTAL_COMMENTS = 0

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


def from_one_store_comment(id, playwright, query):
    BASE_URL = f'https://pcmap.place.naver.com/restaurant/{id}/review/visitor'
    # 이제 여기서 처리한다.
    print(BASE_URL)
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    
    # 페이지 열었다.
    page = context.new_page()
    page.goto(BASE_URL)
    #context.tracing.start(screenshots=True, snapshots=True)
    
    global TOTAL_COMMENTS
    local_list = []

    
    lim = 0
    while lim < 5000:
        try:
            #print(page.locator('.fvwqf').count())
            page.locator('.fvwqf').click(timeout = 1000)
            print(lim)
            time.sleep(random.random())
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
            time.sleep(random.uniform(0.4, 1.6))
        except:
            pass
            
        
        try:
            comment_box.locator('.rvCSr').click(timeout=1000)
            time.sleep(random.uniform(0.6, 1.4))
        except:
            pass
        
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
        comment = comment.replace('\n', ' ').replace('\t', ' ') # 엔터 스페이스바로 바꾸기 tab도 스페이스바로 바꾸기
        label_string = '\t'.join([str(x) for x in dictionary_label.values()])
        final_string = f'{comment}\t{label_string}'
        
        local_list.append(final_string)
        #print(final_string)
    TOTAL_COMMENTS += len(local_list)

    print(f'reviewed {reviewCounter} comments from store {BASE_URL}')
    # 완료하면 페이지 닫기
    page.close()
    
    write_file = open(f'{query}.tsv', 'a', encoding='UTF-8')
    for i in local_list:
        print(i, file=write_file)
    write_file.close()


    
def read_from_store_list(read_file):    
    global store_list
    
    for i in read_file.readlines():
        store_list.append(i)
    
    
    
    
def main():
    global browser
    global review_list
    global TOTAL_COMMENTS
    
    query = "강남"
    
    # 파일에서 카페목록 읽어오기
    read_file = open(f'{query}.txt', 'r')
    read_from_store_list(read_file)
    read_file.close()
    # 읽어오기 종료
    
    write_file = open(f'{query}.tsv', 'a', encoding='UTF-8')
    print('댓글\t가성비\t청결\t맛\t분위기\t친절', file=write_file)
    write_file.close()


    with sync_playwright() as playwright:
        for idx ,id in enumerate(store_list):
            from_one_store_comment(id, playwright, query)
            print(f'finised number {idx + 1} store')
            print(f'now total comment number is {TOTAL_COMMENTS}')
    
    
    for i in review_list:
        print(i, file=write_file)
    

def make_store_list(query):
    #global query
    global store_list
    #query = input("키워드 입력 ㄱㄱ : ")
    
    # store list 초기화
    store_list = []
    
    f1 = open(f'{query}.txt', 'w')
    print(f'looking for cafe in {query}!')
    
    page_cnt = 1
    while True:
        print(f'now looking at page : {page_cnt}')
        if not one_page_url(query, page_cnt):
            break
        page_cnt += 1

    # store list 저장
    
    for i in store_list:
        print(i, file=f1)
    
    f1.close()

if __name__ == "__main__":
    #query = input("키워드 입력 ㄱㄱ : ")

    # print(store_list)
    # print(len(store_list))
    # 1452440066 // 카페 언더우드
    #CAFE_LIST = ['신촌 카페', '성수 카페', '홍대 카페', '강남 카페', '익선 카페', '이태원 카페', '압구정 카페', '잠실 카페', '망원 카페', '여의도 카페', '반포 카페']
    #for i in CAFE_LIST:
    #    make_store_list(i)
    #make_store_list('여의도 카페')
    main()
    # https://pcmap.place.naver.com/restaurant/1946991741/review/visitor
    #https://pcmap.place.naver.com/restaurant/19796689/review/visitor
    #with sync_playwright() as playwright:
    #    from_one_store_comment(19796689, playwright
