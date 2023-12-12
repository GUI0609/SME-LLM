import streamlit as st
import time
import numpy as np

st.set_page_config(page_title="Google Scholar Search", page_icon="📈")

st.markdown("# Google Scholar Search")
st.sidebar.header("Google Scholar Search")
st.write(
    """Google Scholar Search"""
)

keyword = st.text_input('Input your keyword')



import os.path
import re
import requests
from bs4 import BeautifulSoup
 
class Hubber:
    head = { \
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36' \
        }  # 20210607更新，防止HTTP403错误
 
    def pdf_hub(url,path):
        try:
            pdf = requests.get(url, headers=Hubber.head)
            with open(path, "wb") as f:
                f.write(pdf.content)
            print("\n"+"pdf found directly!")
        except:
            print("\n"+"failed to download pdf directly!\n" +url)
            Hubber.err_log(url)
    def sci_hub(path,doi):
        doi = str(doi).split("https://doi.org/")[1]
        url = "https://www.sci-hub.ren/doi:" + doi + "#"
        r = requests.get(url, headers=Hubber.head)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, "html.parser")
        download_url = soup.iframe.attrs["src"]
        try:
            download_r = requests.get(download_url, headers=Hubber.head)
            download_r.raise_for_status()
            with open(path, "wb+") as temp:
                temp.write(download_r.content)
                print("\n"+"Article downloaded by doi!")
        except:
            print("\n"+"failed to download pdf by doi!\n" +url)
            Hubber.err_log(url)
 
    def err_log(url):
        with open("download_err.txt", "a+", encoding="utf-8") as error:
            error.write("PDF not found,download link may be: \n"+url +"\n")
 
    def getSoup(url):
        r = requests.get(url, headers=Hubber.head)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, "html.parser")
        return soup
 
    def getPDF(url,path):
        if os.path.exists(path) == True:
            print("\n" + "Article already exists")
        else:
            if (len(re.findall('pdf', url)) != 0):
                print ("\n"+'pdf link already!')
                Hubber.pdf_hub(url,path)
            elif re.match("https://www.sci-hub.ren/",url):
                print("\n" + 'sci_hub link!')
                url = str(url).replace("https://www.sci-hub.ren/","https://doi.org/")
                Hubber.sci_hub(path,url)
            #if pdf can be easily found!
            elif re.match("https://academic.oup.com/", url):
                soup = Hubber.getSoup(url)
                pdf_link ="https://academic.oup.com"+soup.find(class_="al-link pdf article-pdfLink").get('href')
                #print("\n"+pdf_link)
                Hubber.pdf_hub(pdf_link,path)
                '''
                doi = soup.select('div[class="ww-citation-primary"]')[0].a.get('href')
                #print("\n"+doi)
                Hubber.sci_hub(path,doi)
                '''
            elif re.match("https://content.iospress.com/", url):
                soup = Hubber.getSoup(url)
                pdf_link = soup.find(class_="btn btn-download btn-right get-pdf").get('href')
                # print("\n"+pdf_link)
                Hubber.pdf_hub(pdf_link, path)
            elif re.match("https://wwwnature.53yu.com/", url):
                soup = Hubber.getSoup(url)
                pdf_link = soup.find(class_="c-pdf-download__link").get('href')
                #print("\n"+pdf_link)
                Hubber.pdf_hub(pdf_link, path)
            elif re.match("https://bjo.bmj.com/", url):
                soup = Hubber.getSoup(url)
                pdf_link = soup.find(class_="article-pdf-download").get('href')
                pdf_link = "https://bjo.bmj.com" + pdf_link
                #print("\n"+pdf_link)
                Hubber.pdf_hub(pdf_link,path)
            elif re.match("https://jamanetwork.com/", url):
                soup = Hubber.getSoup(url)
                pdf_link = soup.find(class_="toolbar-tool toolbar-pdf al-link pdfaccess").get('data-article-url')
                pdf_link = "https://jamanetwork.com" + pdf_link
                #print("\n"+pdf_link)
                Hubber.pdf_hub(pdf_link, path)
 
            #if pdf can't be easily found,but doi can!
            elif re.match("https://sciencedirect.53yu.com/", url):
                soup = Hubber.getSoup(url)
                doi = soup.find(class_="doi").get('href')
                Hubber.sci_hub(path, doi)
            elif re.match("https://diabetes.diabetesjournals.org/", url):
                soup = Hubber.getSoup(url)
                doi = soup.select('.citation-doi')[0].a.get('href')
                Hubber.sci_hub(path, doi)
            elif re.match("https://journals.lww.com/", url):
                soup = Hubber.getSoup(url)
                doi = "https://doi.org/" + str(soup.find(id="ej-journal-doi").text).split("doi: ")[1]
                Hubber.sci_hub(path, doi)
            else:
                '''
                https://europepmc.org/
                https://iovs.arvojournals.org/
                https://linkspringer.53yu.com/
                '''
                print("\n"+"To be prettified!Download link may be: " +"\n" +url)
                Hubber.err_log(url)




# -*- coding: utf-8 -*-
 
import requests
from bs4 import BeautifulSoup

import xlwt,os
from time import sleep
from tqdm import tqdm
 
 
TotalNum=0
class Article(object):
    title = ""
    article_link = ""
    authors = ""
    authors_link = ""
    abstract = ""
    def __init__(self):
        title = "New Paper"
 
def save_xls(sheet, paper):
    # 将数据按列存储入excel表格中
    global TotalNum
    sheet.write(TotalNum, 0, TotalNum)
    sheet.write(TotalNum, 1, paper.title)
    sheet.write(TotalNum, 2, paper.article_link)
    sheet.write(TotalNum, 3, paper.journal)
    sheet.write(TotalNum, 4, paper.authors_link)
    sheet.write(TotalNum, 5, paper.abstract)
    TotalNum += 1
 
head = { \
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36' \
        }  # 20210607更新，防止HTTP403错误
article_titles = []
article_links = []
 
def GetInfo(sheet,url):
  r = requests.get(url, headers=head)
  r.raise_for_status()
  r.encoding = r.apparent_encoding
  soup = BeautifulSoup(r.text, "html.parser")
  #print("\n"+soup)
  articles = soup.find_all(class_="gs_ri")
  for article in articles:
      paper =Article()
      try:
          title = article.find('h3')
          paper.title = title.text
          #print("\n"+paper.title)
          article_titles.append(paper.title)
          paper.article_link = title.a.get('href')
          #print("\n"+paper.article_link)
          article_links.append(paper.article_link)
 
          journal = article.find(class_="gs_a")
          paper.journal =journal.text
          #print("\n"+paper.authors)
          authors_addrs = journal.find_all('a')
          for authors_addr in authors_addrs:
              #print("\n"+authors_addr.get('href'))
              paper.authors_link=paper.authors_link +(authors_addr.get('href'))+"\n"
 
          abstract = article.find(class_="gs_rs")
          paper.abstract = abstract.text
          #print("\n"+paper.abstract)
      except:
          continue
      save_xls(sheet,paper)
  return
 
 
def getArticle(article_titles,article_links):
    dir = ".\\Articles\\" +keyword +"\\"
    #print (dir)
    if os.path.exists(dir) == False:
        os.mkdir(dir)
    for k in tqdm(range(len(article_titles))):
        article_titles[k]="{0}".format(article_titles[k].replace(':', ' ')).replace('.', '')
        path = dir + article_titles[k] + ".pdf"
        #print("\n"+path)
        try:
            Hubber.getPDF(article_links[k],path)
            sleep(0.5)
        except:
            continue
 
def query_in_google_scholar(keyword):
    TotalNum=0
    myxls = xlwt.Workbook()
    sheet1 = myxls.add_sheet(u'PaperInfo', True)
    column = ['序号', '文章题目','文章链接','期刊', '作者链接', '摘要']
    for i in range(0, len(column)):
        sheet1.write(TotalNum, i, column[i])
    TotalNum+=1
    #keyword = diabetes and conjunctiva and (microcirculation or microvasculature)
    #print("\n"+keyword)
    key = keyword.replace(" ","+")
    info = keyword + "_PaperInfo.xls"
 
    print("\n"+"检索中……")
    if os.path.exists(info) == True:
        print("\n" + "PaperInfo already exists!")
    else:
        start = 0
        # for i in tqdm(range(10)):
        url = f'https://scholar.lanfanshu.cn/scholar?hl=zh-CN&as_sdt=0%2C5&q={"+".join(keyword.split(" "))}&btnG='#需要更换可用的网址
            # start = start + 10
        GetInfo(sheet1,url)
        myxls.save('/home/ggl/langchain/autogen/SMEui/googlescholar_xlsx/'+keyword+'_PaperInfo.xls')
        sleep(0.5)
    print("\n"+"检索完成")

import pandas as pd
if st.button("Submit"):
    query_in_google_scholar(keyword)
    df = pd.read_excel('/home/ggl/langchain/autogen/SMEui/googlescholar_xlsx/'+keyword+'_PaperInfo.xls',names=['INDEX', 'Title','Link','Journal', 'Authors', 'Abstract'])
    # df['text'] = df[1]+df[5]
    st.dataframe(df)
  







