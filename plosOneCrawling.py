#这是爬取Plos One期刊的程序
# 官网网址：
# 文章目录页：https://journals.plos.org/plosone/browse?page=1
# 文章爬取元素：Open_Access,Altmetric,Citation,Time,Open_Editor,Title


from lxml import etree
import requests
import re
import json
import csv
import time
from fake_useragent import UserAgent


s = requests.session()
s.keep_alive = False
# 关闭多余链接

ua = UserAgent()
headers = {
    'User-Agent': ua.random
}

page_number = 5
#自定义爬取页面

for i in range(1,page_number):
    url="https://journals.plos.org/plosone/browse?page="+str(i)
    response = requests.get(url=url)
    page_text = response.text
    #print(page_text)
    ex = '<h2 class=\"title\">[\n\s]*<a href=\"(.*?)\"'
    dataList = re.findall(ex,page_text,re.S)
    #正则匹配文章链接
    with open('1.txt', 'a+') as f:
        for web in dataList:
            website = "https://journals.plos.org/" +web
            with open('1.txt', 'a+') as f:
                f.write(website)
                f.write('\n')
    print("第{}页爬取完成".format(i))


Url_ls=[]
with open("Article_Data12345.csv", "a+", newline='', encoding="utf-8_sig") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(
        ["Title", "文章链接","Open Access", "Ciatation", "Citation爬取时间", "Peer review", "Receive Date", "Accept Date", "Publish Date",
         "Open Editor", "Altmetric", "Altmetric_json", "Altmetric爬取时间"])

    with open('Article_Url_Initial.txt', 'r') as f:
        for line in f.readlines():
            line = line.strip('\n').strip('\r')  # 去掉列表中每一个元素的换行符
            # print(line)
            Url_ls.append(line)
            #Url_ls存放所有的url链接
        print("url读取成功")

        line_number = 11*page_number
        for line_number in range(0,line_number):
            url = Url_ls[line_number]
            #设定url地址
            start = time.time()
            print("现在正在爬取 {}".format(Url_ls[line_number]))

            try:
                #url="https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0258747"
                page_text = requests.get(url=url,headers=headers).text
                #print(page_text)
                #requests解析网址


                tree = etree.HTML(page_text)
                Title_Raw = tree.xpath('//h1[@id="artTitle"]')[0]
                Title = Title_Raw.xpath('string(.)')#获得所有的text
                # print(Title)
                # print(type(str(Title[0])))
                print("文章标题是{}".format(Title))
                #文章名称爬取

                if "Correction: " not in str(Title) and "Retraction: " not in str(Title):
                    #citationUrl_json = "https://metrics-api.dimensions.ai/doi/10.1371/journal.pone.0191051"
                    citationUrl_json = "https://metrics-api.dimensions.ai/doi/10.1371/journal.pone." + url[-7:]
                    # 获取文章最后几位id识别号

                    c_1 = requests.get(citationUrl_json, timeout=10, headers=headers)
                    Citation = json.loads(c_1.text).get('times_cited')
                    #print("Ciatation_json第一次读取成功")
                    #print("Citation_json网址是:{}".format(citationUrl_json))
                    print("{}爬取成功,Citation大小是{}".format(citationUrl_json,Citation))
                    citation_time = time.strftime('%Y-%m-%d', time.localtime())

                    Open_Access_pattern= re.compile('<p class="license-short" id="licenseShort">(Open Access)<\/p>',re.S)
                    OpenAccess = Open_Access_pattern.search(page_text)
                    #print(OpenAccess)
                    if str(OpenAccess) != "None":
                        #print("存在Open Access")
                        OpenAccess_csv = 1
                    else:
                        #print("不存在Open Access")
                        OpenAccess_csv = 0

                    Peer_pattern = re.compile('(Peer Review)</a>',re.S)
                    Peer_Review = Peer_pattern.search(page_text)
                    #匹配Peer Review
                    #print(Peer_Review)
                    if str(Peer_Review) != "None":
                        #print("存在Peer Review")
                        Peer_Review_csv = 1
                    else:
                        #print("不存在Peer Review")
                        Peer_Review_csv = 0
                    #try/except函数，如果有Peer_Review，则输出为1，否则为0

                    Editor_pattern = re.compile('<p><strong>Editor:\s</strong>([\s\S]*?)</p>',re.S)
                    Editor = Editor_pattern.search(page_text)
                    #print(Editor)
                    if str(Editor) != "None":
                        #print("存在Open Editor")
                        open_Editor_csv = 1
                    else:
                        #print("不存在Open Editor")
                        open_Editor_csv = 0
                    #是否open editor,如果是open，返回1；否则返回0

                    Receive_Search = '<strong>Received:\s</strong>(.*?);\s<strong>'
                    Receive_Date = re.findall(Receive_Search,page_text,re.S)
                    #Receive Date爬取
                    Receive_Date.append("0")
                    #print("Receive_Date是{}".format(Receive_Date[0]))

                    Accept_Search = '<strong>Accepted:\s</strong>(.*?);\s<strong>'
                    Accept_Date = re.findall(Accept_Search,page_text,re.S)
                    #Accept Date爬取
                    Accept_Date.append("0")
                    #print("Accept_Date是{}".format(Accept_Date[0]))

                    Publish_Search = '<strong>Published:\s</strong>\s(.*?)</p><p>'
                    Publish_Date = re.findall(Publish_Search,page_text,re.S)
                    #Publish Date爬取
                    Publish_Date.append("0")
                    #print("Publish_Date是{}".format(Publish_Date[0]))

                    URL_json = "https://api.altmetric.com/v1/doi/10.1371/journal.pone." + url[-7:]
                    #print(URL_json)
                    # 获取文章最后几位id识别号
                    try:
                        r_1 = requests.get(URL_json, timeout=10, headers=headers)
                        try:
                            altmetric_img = json.loads(r_1.text).get('images')
                            almetric_Search = 'size=.*&score=(.*?)&types'
                            almetric = re.findall(almetric_Search, altmetric_img["small"], re.S)[0]
                            # 用正则匹配altmetric
                            print("Almetric是{}".format(almetric))
                            altmetric_csv = almetric  # csv里altmetric数值
                            altmetric_json = URL_json
                        except:
                            print("json第一次爬取失败")
                            if r_1.status_code != 200 and r_1.status_code != 404:
                                altmetric_csv = 0  # csv里altmetric数值
                                altmetric_csv = r_1.status_code
                                with open('wrong.txt', 'a+', encoding='utf-8') as f:
                                    f.write(url)
                                print("网页报错{}".format(r_1.status_code))
                            elif r_1.status_code == 404:
                                altmetric_csv = 0
                                altmetric_csv = URL_json
                            else:
                                altmetric_csv = 0
                                altmetric_csv = "异常错误"
                                with open('wrong.txt', 'a+', encoding='utf-8') as f:
                                    f.write(url)
                    except:
                        print("altmetrics_json访问超时")
                        with open('wrong.txt', 'a+', encoding='utf-8') as f:
                            f.write(url)
                        altmetric_csv = 0
                        altmetric_csv = "超时"

                    altmetric_time = time.strftime('%Y-%m-%d', time.localtime())
                    writer.writerow([Title,url,OpenAccess_csv,Citation,citation_time,Peer_Review_csv,Receive_Date[0],Accept_Date[0],Publish_Date[0],open_Editor_csv,altmetric_csv,altmetric_json,altmetric_time])
                    print("{}的csv写入成功".format(url))

                else:
                    print("文章不符合要求，跳过")
                    line_number += 1
                    print("第{}页爬取完成".format(line_number))
                    print("\n")

            except:
                print("访问文章有误")
                Title= 0
                url = url
                OpenAccess_csv = 0
                Citation = 0
                citation_time = 0
                Peer_Review_csv = 0
                Receive_Date = 0
                Accept_Date = 0
                Publish_Date = 0
                open_Editor_csv = 0
                altmetric_csv = 0
                altmetric_json = 0
                altmetric_time = 0
                writer.writerow(
                    [Title, url, OpenAccess_csv, Citation, citation_time, Peer_Review_csv, Receive_Date,
                     Accept_Date, Publish_Date, open_Editor_csv, altmetric_csv, altmetric_json, altmetric_time])
                print("{}的csv写入成功".format(url))
                print("\n")
                line_number += 1

                with open('wrong.txt','a+',encoding='utf-8') as f:
                    f.write(url)
                    #输出爬取失败文章，准备进行第二次尝试

    print("爬取成功")

