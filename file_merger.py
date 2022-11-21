CAFE_LIST = ['신촌', 
             '성수', 
             '홍대', 
             '강남', 
             '익선', 
             '이태원', 
             '압구정', 
             '잠실', 
             '망원', 
             '여의도', 
             '반포']


f_merge = open('target.txt', 'w')

for i in CAFE_LIST:
    file_name = f'{i}.txt'
    # 파일 열기
    f_temp = open(file_name, 'r')
    
    for i in f_temp.readlines():
        print(i.strip(), file=f_merge)
    
    
    # 파일 닫기
    f_temp.close()
    

f_merge.close()