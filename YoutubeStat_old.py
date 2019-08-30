#! /usr/bin/env python
#
# Copyright 2018 Tao Li. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#    1. Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import optparse
import sys
import re
import datetime
import time
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# print(urllib.request.urlopen("https://www.12306.cn/mormhweb/").read())

def get_HTML(URL):
    options = webdriver.ChromeOptions()
    chrome_driver = 'D:/Research/text_analysis/YouTube-Statistics-master/chromedriver.exe'
    browser = webdriver.Chrome(chrome_options=options, executable_path=chrome_driver)
    options.add_argument('--ignore-certificate-errors')
    # options.add_argument('--ignore-ssl-errors')
    browser.get(URL)
    time.sleep(10)
    html = browser.page_source.encode("utf-8")
    browser.close()
    return html

def get_data(html):
    soup = BeautifulSoup(html, "lxml")

    countries = []
    for i in soup.find_all("div", class_="b-list-section b-section-c b-ib b-vat"):
        name = i.get_text()
        if name: countries.append(name)

    channelNames = []
    channelURLs = []
    for i in soup.find_all("a", href=re.compile(r"/youtube/en/channel/.+/*")):
        cID = i['href'].split("/")[-1]
        cName = i.get_text()
        channelURLs.append("https://www.youtube.com/channel/" + cID)
        channelNames.append(cName)

    monthlyViews = []
    for i in soup.find_all("div", class_="b-list-section b-section-s b-ib b-vat b-section-mviews"):
        views = i.get_text().replace(",", "")
        monthlyViews.append(views)

    subscribers = []
    for i in soup.find_all("div", class_="b-list-section m-hide b-section-s b-section-subs b-ib b-vat"):
        subs = i.get_text().replace(",", "")
        subscribers.append(subs)

    res = []
    for i in range(len(subscribers)):
        item = [channelNames[i], countries[i], monthlyViews[i], subscribers[i], channelURLs[i]]
        res.append(item)
    return res

def output(res, topN=20, fmt="csv"):
    res = res[:topN]
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d")

    if fmt == "csv":
        with open("./data/top {} channels as of {}.csv".format(str(topN), timestamp), "w") as f:
            counter = 1
            for i in res:
                line = ",".join([str(counter)] + i)
                f.write(line + "\n")
                print(line)
                counter += 1

    if fmt == "md":
        counter = 1
        print("| # | Channel | Country | Monthly Views | Subscribers | ")
        print("|----:|----:|----:|----:|----:|")
        for i in res:
            print("| {} | [{}]({}) | {} | {} | {} |".format(str(counter), i[0], i[-1], i[1], i[2], i[3]))
            counter += 1

def main():
    usage = "youtubestat.py [options] <query string>"
    fmt = optparse.IndentedHelpFormatter(max_help_position=50, width=100)
    parser = optparse.OptionParser(usage=usage, formatter=fmt)
    group = optparse.OptionGroup(parser, 'Query arguments', 'These options define search query arguments and parameters.')
    group.add_option('-C', '--category', metavar='CATEGORY', default=None, help='Indicate the category, e.g. news, sports, education, etc.')
    group.add_option('-N', '--topN', metavar='TOPN', default=None, help='Indicate the number of channels to show')
    group.add_option('-L', '--lang', metavar='LANGUAGE', default=None, help='Indicate the channel language, e.g. en, zh, es, etc.')
    group.add_option('-F', '--fmt', metavar='FORMAT', default=None, help='Indicate the output format, e.g. csv, txt, md, etc.')

    parser.add_option_group(group)

    options, _ = parser.parse_args()

    # Show help if we have neither keyword search nor author name
    if len(sys.argv) == 1:
        parser.print_help()
        return 1

    URL = "https://www.kedoo.com/youtube/en/top-channels.html?period=2017-11-01&category=2&lang=en"
    # URL = "https://www.baidu.com/s?wd=news&rsv_spt=1&rsv_iqid=0xfd03b200002f9eff&issp=1&f=8&rsv_bp=1&rsv_idx=2&ie=utf-8&tn=baiduhome_pg&rsv_enter=1&rsv_dl=ib"
    html = get_HTML(URL)
    res = get_data(html)
    # print("res === ", res)
    output(res, topN=int(options.__dict__["topN"]), fmt=options.__dict__["fmt"])

    return 0

if __name__ == "__main__":
    sys.exit(main())
