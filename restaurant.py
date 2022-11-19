from unittest import result
import requests, json, os, sys, time


f = open("test.json", "w")

#https://map.naver.com/v5/api/search?caller=pcweb&query=%EC%8B%A0%EC%B4%8C%20%EC%B9%B4%ED%8E%98&page=10

def one_store_id_get(data):
    for datum in data:
        print(datum['id'], file=f)
    

def one_page_url(query, page_cnt):
        
    URL = f"https://map.naver.com/v5/api/search?caller=pcweb&query={query}&page={page_cnt}"
    try:
        res = requests.get(URL).json()
        one_store_id_get(res['result']['place']['list'])
        return True
    except:
        return False
    # list에 가게들 있는거 같음
    #print(res['result']['place']['list'])
    

def main():
    query = "신촌 카페"
    
    page_cnt = 1
    
    while True:
        
        if not one_page_url(query, page_cnt):
            break
        page_cnt+=1

main()
f.close()