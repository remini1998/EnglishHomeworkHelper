#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import json
import re
def getChinaDailyQuery(word):
    query = "http://searchen.chinadaily.com.cn/search?query=" + word
    r = requests.get(query)
    soup = BeautifulSoup(r.text, "html5lib")
    result = soup.find("ul", { "class" : "cs_sear_list" })
    result = result.select("li p")
    res = []
    for s in result:
        before = re.search("(?<=[\.\?;]\s).+?(?=<b>)", str(s))
        after = re.search("(?<=</b>).*?[\.\?;]", str(s))
        if before and after:
            before = before.group(0)
            after = after.group(0)
            sen = before + word + after
            tran = getGoogleTrans(sen)
            pretty = before + "【" + word + "】" + after
            res.append({"raw": sen, "pretty": pretty, 'tran': tran})
    return res

def getWordTrans(word):
    query = "http://dict-co.iciba.com/search.php?word=" + word + "&submit=查询"
    r = requests.get(query)
    soup = BeautifulSoup(r.text, "html5lib")
    result = soup.body.prettify()
    result = result.replace("&amp;", "&") #转回&
    result = result.replace("\xa0", " ") #去除奇怪的无法输出的符号
    result = re.sub("<.+>", "", result, count=0, flags=0) #过滤html标签
    result = re.sub("返回查词首页", "", result, count=0, flags=0) #去除最后一句话
    result = re.sub("(?<=\n)(\s+)\n", "", result, count=0, flags=0) #删除空行
    result = result[1:-1].split("\n")
    return result
    
def getGoogleTrans(sen):
    googleTransUrl = "http://translate.hotcn.top/translate/api"
    data = {'text': sen}
    result = requests.post(googleTransUrl, data)
    result = result.json()
    return result["text"]

def lookUpOneWord(word):
    print("\t" + word)
    wordTrans = getWordTrans(word)
    for wt in wordTrans:
        print("\t\t"+ wt)
    res = getChinaDailyQuery(word)
    num = 0
    for r in res:
        print("\t" + str(num) + ":" + "\t" + r["pretty"])
        print("\t\t" + r["tran"])
        num += 1
    selection = int(input("Please select one: "))
    print("\n")
    print("\t" + word)
    for wt in wordTrans:
        print("\t\t"+ wt)
    print("\t" + res[selection]["pretty"])
    print("\t" + res[selection]["tran"])

# getChinaDailyQuery("imply")
# getWordTrans("submit")
# getGoogleTrans("Most of the basic models for these objects imply that they are composed almost entirely of neutrons.")
while 1:
    word = input("Please input the word you look up: ")
    lookUpOneWord(word)
    print("\n\n")
