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


begginging_Time = time.time() #程序开始时间

Url_ls=[]
with open("Article_Data_Replenish_3.csv", "a+", newline='', encoding="utf-8_sig") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(
        ["Title", "文章链接","Open Access", "Ciatation", "Citation爬取时间", "Peer review", "Receive Date", "Accept Date", "Publish Date",
         "Open Editor", "Altmetric", "Altmetric_json", "Altmetric爬取时间"])

    with open('Article_Url_Replenish2.txt', 'r') as f:
        for line in f.readlines():
            line = line.strip('\n').strip('\r')  # 去掉列表中每一个元素的换行符
            # print(line)
            Url_ls.append(line)
            #Url_ls存放所有的url链接
        print("url读取成功")

        line_number = 0
        for line_number in range(0,2021):
            url = Url_ls[line_number]
            #设定url地址
            start = time.time()
            print("现在正在爬取 {}".format(Url_ls[line_number]))

            try:
                #url="https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0258747"
                page_text = requests.get(url=url,headers=headers,timeout=10).text
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
                    try:
                        # 获取文章最后几位id识别号
                        c_1 = requests.get(citationUrl_json, timeout=10, headers=headers)

                        try:
                            Citation = json.loads(c_1.text).get('times_cited')
                            print("Ciatation_json第一次读取成功")
                            print("Citation_json网址是:{}".format(citationUrl_json))
                            print("{}爬取成功,Citation大小是{}".format(citationUrl_json,Citation))

                        except:
                            print("Ciatation_json第一次爬取失败")

                            if c_1.status_code == 200:
                                print("Citation_json网址第一次get失败，休息20秒")
                                time.sleep(20)
                                c_2 = requests.get(citationUrl_json, timeout=5, headers=headers)

                                try:
                                    Citation = json.loads(c_2.text).get('times_cited')
                                    print("Ciatation_json读取成功")
                                    print("Citation_json网址是:{}".format(citationUrl_json))
                                    print("{}爬取成功,Citation大小是{}".format(citationUrl_json,Citation))

                                except:
                                    Citation = "异常"
                                    print("Citation_json爬取失败，第二次爬取网页状态码是{}".format(c_2.status_code))
                                    print("无法获取Citation_json网站")

                            else:
                                Citation = "异常"
                                print("Citation_json爬取失败网页状态码是{}".format(c_1.status_code))
                                print("无法获得相关Citation_json网站")


                    except:
                        print("Citation_json第一次爬取超时，休息20秒，进行第二次尝试")
                        time.sleep(20)
                        c_2 = requests.get(citationUrl_json, timeout=10, headers=headers)

                        try:
                            Citation = json.loads(c_2.text).get('times_cited')
                            print("Ciatation_json第二次读取成功")
                            print("Citation_json网址是:{}".format(citationUrl_json))
                            print("{}爬取成功,Citation大小是{}".format(citationUrl_json,Citation))

                        except:
                            print("Ciatation_json第二次爬取失败")

                            if c_2.status_code == 200:
                                print("Citation_json网址第二次get失败，休息20秒")
                                time.sleep(20)
                                c_3 = requests.get(citationUrl_json, timeout=5, headers=headers)

                                try:
                                    Citation = json.loads(c_3.text).get('times_cited')
                                    print("Ciatation_json读取成功")
                                    print("Citation_json网址是:{}".format(citationUrl_json))
                                    print("{}爬取成功,Citation大小是{}".format(citationUrl_json,Citation))

                                except:
                                    print("Citation_json爬取失败，第三次爬取网页状态码是{}".format(c_3.status_code))
                                    print("无法获取Citation_json网站")
                                    Citation = "异常"

                            else:
                                print("Citation_json爬取失败网页状态码是{}".format(c_2.status_code))
                                print("无法获得相关Citation_json网站")

                        print("Citation_json第二次重试超时")
                        Citation = "异常"
                        print(Citation)

                    Open_Access_pattern= re.compile('<p class="license-short" id="licenseShort">(Open Access)<\/p>',re.S)
                    OpenAccess = Open_Access_pattern.search(page_text)
                    #print(OpenAccess)
                    if str(OpenAccess) != "None":
                        print("存在Open Access")
                        OpenAccess_csv = 1
                    else:
                        print("不存在Open Access")
                        OpenAccess_csv = 0


                    Peer_pattern = re.compile('(Peer Review)</a>',re.S)
                    Peer_Review = Peer_pattern.search(page_text)
                    #匹配Peer Review
                    #print(Peer_Review)
                    if str(Peer_Review) != "None":
                        print("存在Peer Review")
                        Peer_Review_csv = 1
                    else:
                        print("不存在Peer Review")
                        Peer_Review_csv = 0
                    #try/except函数，如果有Peer_Review，则输出为1，否则为0


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
                    print("Publish_Date是{}".format(Publish_Date[0]))

                    Editor_pattern = re.compile('<p><strong>Editor:\s</strong>([\s\S]*?)</p>',re.S)
                    Editor = Editor_pattern.search(page_text)
                    #print(Editor)
                    if str(Editor) != "None":
                        print("存在Open Editor")
                        open_Editor_csv = 1
                    else:
                        print("不存在Open Editor")
                        open_Editor_csv = 0
                    #是否open editor,如果是open，返回1；否则返回0



                    try:
                        URL_json = "https://api.altmetric.com/v1/doi/10.1371/journal.pone." + url[-7:]
                        #print(URL_json)
                        #获取文章最后几位id识别号
                        r_1 = requests.get(URL_json, timeout=10, headers=headers)
                        # print(r_1.status_code)
                        try:
                            # altmetric_URL_Raw = json.loads(r.text).get('details_url')
                            # altmetric_URL = "https://www.altmetric.com/details/" + altmetric_URL_Raw[-9:]
                            altmetric_img = json.loads(r_1.text).get('images')
                            # print(altmetric_URL)
                            # 获取altmetrics的文章id号
                            print("json读取成功")
                            print("json网址是:{}".format(URL_json))

                            # print(altmetric_img["small"])
                            almetric_Search = 'size=.*&score=(.*?)&types'
                            almetric = re.findall(almetric_Search, altmetric_img["small"], re.S)[0]
                            # 用正则匹配altmetric
                            print("Almetric是{}".format(almetric))
                            altmetric_csv = almetric  # csv里altmetric数值
                            altmetric_json = URL_json

                        except:
                            print("json第一次爬取失败")

                            if r_1.status_code == 200:
                                print("json网址第一次get失败，休息10秒")
                                time.sleep(10)
                                r_2 = requests.get(URL_json, timeout=5, headers=headers)

                                try:
                                    # altmetric_URL_Raw = json.loads(r.text).get('details_url')
                                    # altmetric_URL = "https://www.altmetric.com/details/" + altmetric_URL_Raw[-9:]
                                    altmetric_img = json.loads(r_2.text).get('images')
                                    # print(altmetric_URL)
                                    # 获取altmetrics的文章id号
                                    print("json第二次get成功")
                                    print("json网址是:{}".format(URL_json))

                                    # print(altmetric_img["small"])
                                    almetric_Search = 'size=.*&score=(.*?)&types'
                                    almetric = re.findall(almetric_Search, altmetric_img["small"], re.S)[0]
                                    # 用正则匹配almetric
                                    print("Almetric是{}".format(almetric))
                                    altmetric_csv = almetric  # csv里altmetric数值
                                    altmetric_json = URL_json
                                    # 第二次尝试获取json
                                except:
                                    print("json爬取失败，第二次爬取网页状态码是{}".format(r_2.status_code))
                                    print("无法获取json网站")
                                    altmetric_csv = "网页状态码为200但get失败"
                                    altmetric_json = URL_json
                            else:
                                print("json爬取失败网页状态码是{}".format(r_1.status_code))
                                print("无法获得相关json网站")
                                altmetric_csv = "无法获取json网址"
                                altmetric_json = r_1.status_code

                    except:
                        print("json第一次爬取超时，休息10秒，进行第二次尝试")
                        time.sleep(10)

                        try:
                            #重复上述操作
                            URL_json = "https://api.altmetric.com/v1/doi/10.1371/journal.pone." + url[-7:]
                            # print(URL_json)
                            # 获取文章最后几位id识别号
                            r_1 = requests.get(URL_json, timeout=10, headers=headers)
                            # print(r_1.status_code)
                            try:
                                # altmetric_URL_Raw = json.loads(r.text).get('details_url')
                                # altmetric_URL = "https://www.altmetric.com/details/" + altmetric_URL_Raw[-9:]
                                altmetric_img = json.loads(r_1.text).get('images')
                                # print(altmetric_URL)
                                # 获取altmetrics的文章id号
                                print("json读取成功")
                                print("json网址是:{}".format(URL_json))

                                # print(altmetric_img["small"])
                                almetric_Search = 'size=.*&score=(.*?)&types'
                                almetric = re.findall(almetric_Search, altmetric_img["small"], re.S)[0]
                                # 用正则匹配altmetric
                                print("Almetric是{}".format(almetric))
                                altmetric_csv = almetric  # csv里altmetric数值
                                altmetric_json = URL_json

                            except:
                                print("json第二次爬取失败")

                                if r_1.status_code == 200:
                                    print("json网址第二次get失败，休息20秒")
                                    time.sleep(10)
                                    r_2 = requests.get(URL_json, timeout=5, headers=headers)

                                    try:
                                        # altmetric_URL_Raw = json.loads(r.text).get('details_url')
                                        # altmetric_URL = "https://www.altmetric.com/details/" + altmetric_URL_Raw[-9:]
                                        altmetric_img = json.loads(r_2.text).get('images')
                                        # print(altmetric_URL)
                                        # 获取altmetrics的文章id号
                                        print("json第三次get成功")
                                        print("json网址是:{}".format(URL_json))

                                        # print(altmetric_img["small"])
                                        almetric_Search = 'size=.*&score=(.*?)&types'
                                        almetric = re.findall(almetric_Search, altmetric_img["small"], re.S)[0]
                                        # 用正则匹配almetric
                                        print("Almetric是{}".format(almetric))
                                        altmetric_csv = almetric  # csv里altmetric数值
                                        altmetric_json = URL_json
                                        # 第三次尝试获取json
                                    except:
                                        print("json爬取失败，第三次爬取网页状态码是{}".format(r_2.status_code))
                                        print("无法获取json网站")
                                        altmetric_csv = "网页状态码为200但get失败"
                                        altmetric_json = URL_json
                                else:
                                    print("json爬取失败，第二次爬取网页状态码是{}".format(r_1.status_code))
                                    print("无相关json网址")
                                    altmetric_csv = "无法获取json网站"
                                    altmetric_json = r_1.status_code
                                    with open('wrong_2.11.txt', 'a+', encoding="utf-8") as f:
                                        f.write(url)
                                        f.write("\n")
                        except:
                            print("json第二次重试超时")
                            altmetric_csv = "无法获取json网站"
                            altmetric_json = "0"
                            with open('wrong_2.11.txt', 'a+', encoding="utf-8") as f:
                                f.write(url)
                                f.write("\n")


                    altmetric_time = time.strftime('%Y-%m-%d', time.localtime())

                    writer.writerow([Title,url,OpenAccess_csv,Citation,citation_time,Peer_Review_csv,Receive_Date[0],Accept_Date[0],Publish_Date[0],open_Editor_csv,altmetric_csv,altmetric_json,altmetric_time])
                    print("{}的csv写入成功".format(url))

                else:
                    print("文章不符合要求，跳过")

                line_number += 1
                end = time.time()
                current_Time = time.time()
                print("当前页面耗时{}秒".format(end - start))
                print("第{}页爬取完成".format(line_number))
                print("程序已经进行了{:.2f}分钟，即{:.2f}小时".format((current_Time - begginging_Time)/60,(current_Time - begginging_Time)/2021))
                print("完成度为{:.4f}%".format((line_number / 2021) * 100))
                print("预计还需要{:.2f}小时".format(((end - start) * (2021- line_number))/3600))
                print("\n")



            except:
                print("访问文章链接超时,休息10秒")
                time.sleep(10)
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
                with open('wrong_2.11.txt','a+',encoding="utf-8") as f:
                    f.write(url)
                    f.write("\n")

    print("爬取成功")


