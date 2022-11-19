from unittest import result
import requests, json, os, sys, time



#f = open("test.json", "w")

#https://map.naver.com/v5/api/search?caller=pcweb&query=%EC%8B%A0%EC%B4%8C%20%EC%B9%B4%ED%8E%98&page=10
#한 가게의 url 은 다음과 같은 구조로 된다.
#https://map.naver.com/v5/entry/place/{가게 id}
# 가게 url 에 들어가서 더보기 click 한 다음에 graphql을 지속적으로 받아오면 될꺼 같음

def one_store_id_get(data):
    global store_list
    #for datum in data:
        #print(datum['id'], file=f)
    store_list.extend([x['id'] for x in data])
    time.sleep(1)
    

def one_page_url(query, page_cnt):
    
    URL = f"https://map.naver.com/v5/api/search?caller=pcweb&query={query}&page={page_cnt}"
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    }
    
    
    try:
        res = requests.get(URL, headers= headers).json()
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


store_list = []

main()
print(store_list)
print(len(store_list))

#f.close()


