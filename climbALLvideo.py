
# coding: utf-8

import re
from bs4 import BeautifulSoup
import requests
import time
import random
from queue import Queue
from fake_useragent import UserAgent
from autoIP import ReptileIp
import sys


# 获取网页源码
def getHTMLText(URL):
    try:
        ip = ReptileIp('https://www.xicidaili.com/nn/2')
        proxies = ip.verify_ip()
        #print(proxies)
        headers= {'User-Agent':str(UserAgent().random)}
        response = requests.get(URL, headers=headers,proxies=proxies, timeout=30)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        return response.text
    except requests.HTTPError as e:
        print(e)
        print("HTTPError")
        sys.exit(1)
    except requests.RequestException as e:
        print(e)
        sys.exit(1)
    except:
        print("Unknown Error!")
        sys.exit(1)


# bv转av
def BVtoAV(bv):
    alphabet = 'fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
    r = 0
    for i, v in enumerate([11, 10, 3, 8, 4, 6]):
        r += alphabet.find(bv[v]) * 58**i
    return (r - 0x2_0840_07c0) ^ 0x0a93_b324


# 判断是否有相关tag
def judgeTag(bv, keyword):
    URL = 'https://www.bilibili.com/video/{}'.format(bv)
    demo = getHTMLText(URL)
    if demo:
        soup = BeautifulSoup(demo, 'html.parser')
        for channel in soup.find_all('span', class_='channel-name'):
            if channel.find(string = keyword):
                return 1
    else:
        print('demo出错')
    return 0


# 根据某个bv号获取其相关的bv号
def get_related_bv(bv, keyword):
    bvs = []
    temp = []
    demo = getHTMLText('https://www.bilibili.com/video/{}'.format(bv))
    if not demo:
        print("获取推荐视频出错")
        return 0
    soup = BeautifulSoup(demo, 'html.parser')
    for related in soup.find_all('a'):
        info = related.get('href')
        if info:  # 有时候可能是空的
            if re.search('BV+[^/]*',info):
                bv = re.search('BV+[^/]*',info).group(0)
                if not bv in temp:  #去掉重复的
                    temp.append(bv)
    for t in temp:
        if judgeTag(t, keyword) == 1:
            bvs.append(t)
    return bvs


def sleep_func():
    sleep_time = random.choice(range(50, 90)) * 0.1
    #time.sleep(random.randint(50,70))
    time.sleep(sleep_time)


if __name__ == '__main__':
    
    '''
    with open('bv.txt','r') as fp:		# 读取文件里的bv号，继续找下一个
        BVS = fp.read()
    bvs = BVS.split('\n')[:-1]  # 除去最后的空格
    bvQueue = Queue(maxsize=0)
    with open('bvQueue.txt','r') as fp:		# 读取文件里的bv号，继续找下一个
        BVQ = fp.read()
    bvQue = BVQ.split('\n')[:-1]
    for bv in bvQue:
        bvQueue.put(bv)
    print(len(bvs), bvQueue.qsize())
    '''


    # 初始化
    # 下次执行时，下面这段可以不要，直接读取bv号的文件（上面注释的代码），可以继续上一次的追加
    bv_initial = 'BVxxxxxxxx'   # 这里随便找一个带有频道标签的视频的bv号填入都行
    bvs = get_related_bv(bv_initial, keyword)  # keyword是要搜索的频道名称
    bvQueue = Queue(maxsize=0)
    for bv in bvs:
        bvQueue.put(bv)


    # 弄个bv_temp是因为，如果直接加入bvs的话，bvs永远在变大
    # 除非bvs不再增加（所有带此标签的视频均收集完），否则会一直有for循环（太久了）
    num = len(bvs) + 1000
    while len(bvs) <= num:    # 每次增加得太多会有412错误
        # 确保一次循环后先判断是否已收集足够数量的视频之后再进行
        if not bvQueue.empty():
            bv = bvQueue.get()
        else:
            print("队列为空")
            break
        t_bv = get_related_bv(bv, 'xxxxxxx')   # 这里填入要搜寻的频道名称
        if not t_bv:  # 获取失败，重新放入队列下次重试
            print('均不符合条件')
            continue
        for b in t_bv:
            if not b in bvs:
                bvs.append(b)  # 获取一个bv号对应的所有推荐视频的bv号
                with open('bv.txt','a') as fp:   # 存入文件
                    fp.write(b+'\n')
                bvQueue.put(b)
        # 如果你想的话，也可以把时间打印出来
        #n += 1
        #if n % 100 == 0:
        #    print("当前时间： ",time.strftime('%Y.%m.%d %H:%M:%S ',time.localtime(time.time())))
        #    print(n)
        sleep_func()


    print(len(bvs))
    # w为覆盖的，r为追加的
    #with open('bv.txt','w+') as fp:	# 保存进txt文件 
    #    for bv in bvs:
    #        fp.write(bv+'\n')

    print(len(list(bvQueue.queue)))
    with open('bvQueue.txt','a') as fp:	# 保存进txt文件
        for bv in list(bvQueue.queue):
            fp.write(bv+'\n')
