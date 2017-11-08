#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import json
import traceback
import re
import time
def getChinaDailyQuery(word):
    query = "http://searchen.chinadaily.com.cn/search?query=" + word
    r = requests.get(query)
    soup = BeautifulSoup(r.text, "html5lib")
    # print(soup.prettify())
    result = soup.find("ul", { "class" : "cs_sear_list" })
    result = result.select("li p")
    res = []
    num = len(result)
    print("成功获取China Daily例句数据！共找到", num, "句")
    count = 0
    for s in result:
        count += 1
        before = re.search("(?<=[\.\?;]\s).+?(?=<b>)", str(s))
        after = re.search("(?<=</b>).*?[\.\?;]", str(s))
        if before and after:
            before = before.group(0)
            after = after.group(0)
            sen = before + word + after
            print("成功解析正文：", sen)
            tran = getGoogleTrans(sen)
            pretty = before + "【" + word + "】" + after
            res.append({"raw": sen, "pretty": pretty, 'tran': tran})
            print("成功获取翻译", count, "/", num, ":", tran)
            time.sleep(0.2)
    return res

def getWordTrans(word):
    query = "http://dict-co.iciba.com/search.php?word=" + word + "&submit=查询"
    r = requests.get(query)
    soup = BeautifulSoup(r.text, "html5lib")
    result = soup.body.prettify()
    result = result.replace("&amp;", "&") #转回&
    result = result.replace("\xa0", " ") #去除奇怪的无法输出的符号
    result = result.replace("\xe2", " ")  # 去除奇怪的无法输出的符号
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

def inputWords():
    words = []
    while 1:
        word = input("Please input the word you look up (input '0' to end): ")
        if word == "":
            continue
        if word == "0":
            break
        words.append(word)
    num = len(words)
    print("您输入共%d个词：" % num)
    for w in words:
        print(w)
    print("\n")
    return words

def lookUpWords(words):
    result = []
    numWord = len(words)
    count = 0
    for word in words:
        count += 1
        print("" + word)
        wordTrans = getWordTrans(word)
        for wt in wordTrans:
            print("\t\t" + wt)
        res = getChinaDailyQuery(word)
        result.append({"word": word, "wordTrans": wordTrans, "sentence": res})
        print("【%d/%d】完成单词查询" % (count, numWord))
    return result

def selectSentenceAndRecord(data):
    fileName = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + ".log"
    count = 0
    numAll = len(data)
    all = ""
    fo = open(fileName, "a+", encoding='utf-8')
    for d in data:
        count += 1
        print("【%d / %d】进度" % (count, numAll))
        print("\n")
        print("" + d["word"])
        for wt in d["wordTrans"]:
            print("\t\t" + wt)
        num = 0
        for r in d["sentence"]:
            print("\t" + str(num) + ":" + "\t" + r["pretty"])
            print("\t\t" + r["tran"])
            num += 1
        selection = str(input("Please select one (可用&选择多句，如0&2): "))
        selection = selection.replace(" ", "")
        ss = selection.split("&")
        result = "\n" + "\n"
        result += "" + d["word"] + "\n"
        for wt in d["wordTrans"]:
            result += "\t\t" + wt + "\n"
        for s in ss:
            try:
                result += "\t" + d["sentence"][int(s)]["pretty"] + "\n"
                result += "\t" + d["sentence"][int(s)]["tran"] + "\n"
            except:
                print("找不到此例句！")
        # print(result)
        all += result
        fo.write(result)
    fo.close()
    return all


# getChinaDailyQuery("imply")
# getWordTrans("submit")
# getGoogleTrans("Most of the basic models for these objects imply that they are composed almost entirely of neutrons.")
while 1:
    try:
        words = inputWords()
        data =lookUpWords(words)
        all = selectSentenceAndRecord(data)
        print(all)
    except Exception as e:
        print("发生异常!")
        print(e)
        print('traceback:\n%s' % traceback.format_exc())
    finally:
        print("\n\n")
