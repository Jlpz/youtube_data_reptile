# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import random

def getHTMLText(url, headers, code='utf8'):
    try:
        pro = ['175.149.204.24', '119.118.8.100', '183.187.73.184', '49.86.62.148', '58.217.89.173']  # 网上找免费代理
        r = requests.get(url, proxies={'http':random.choice(pro)}, headers=headers, timeout=30)
        r.raise_for_status()
        r.encoding = code
        # r.encoding=r.apparent_encoding
        # print(r.text[:1000])
        return r.text
    except:
        return "爬取失败"


def getComment(url, headers):
    html = getHTMLText(url, headers)
    soup = BeautifulSoup(html, 'html.parser')
    print("soup:",soup)
    comment = soup.findAll('span', 'short')
    lst = []
    for com in comment:
        lst.append(com.getText() + '\n')
    return lst


def main():
    # headers = {'Accept': '*/*',
    #            'Accept-Encoding': 'gzip, deflate, br',
    #            'Accept-Language': 'zh-CN,zh;q=0.9',
    #            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36'
    #                          '(KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'
    #            }
    headers = {
        'Host': 'movie.douban.com',
        'Referer': 'https://movie.douban.com/subject/26322644/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
        'Cookie': 'yourCookie'
    }
    f = open('流浪地球豆瓣评论.txt', 'w', encoding='utf-8')
    for page in range(10):
        url = 'https://movie.douban.com/subject/26266893/comments?start=' + str(
            20 * page) + '&limit=20&sort=new_score&status=P'
        print("正在爬取第%s页的评论：" % (page + 1))
        print(url + '\n')
        for i in getComment(url, headers):
            f.write(i)
    print("爬取完成")


if __name__ == '__main__':
    main()