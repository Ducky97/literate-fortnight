import unittest
import re
import time
import asyncio
import multiprocessing
from lxml import etree
from selenium import webdriver
from multiprocessing import Pool
from selenium.webdriver.support.ui import WebDriverWait

urls = ["https://dagyy.v.zzu.edu.cn/login",
     "https://mail.v.zzu.edu.cn",
     "https://uts.zuel.edu.cn/Home/studentCommon/studentLogin.jsp",
     "https://c.zju.edu.cn/webapps/login/",
     "https://mail.zju.edu.cn",
     "https://zlgc.ynu.edu.cn/zlgc/index.do",
     "https://webmail.ynu.edu.cn/",
     "http://ydarts.ybu.edu.cn/",
     "https://mail.ybu.edu.cn",
     "https://examination.xmu.edu.cn/jiaofei/login/",
     "http://weixin.lib.xju.edu.cn",
     "http://mail.xju.edu.cn"
     ]

def spider_sub_page(link):
    print(link)
    # time.sleep(5)
    driver_s = webdriver.Chrome()
    driver_s.get(link)
    WebDriverWait(driver_s, 10)
    check(driver_s)
    driver_s.close()
    driver_s.quit()

def get_sub_links(driver):
    doc = driver.page_source
    html = etree.HTML(doc)
    # 查找所有的links
    links = list()
    for link in html.xpath("//a[@href]/@href"):
        if ("javascript" in link) and ("void" in link):
            continue
        if not (re.match(r'http://', link) or re.match(r'https://', link)):
            link = driver.current_url + link
        links.append(link)
    # print(links)
    return links

def check(driver):
    doc = driver.page_source
    html = etree.HTML(doc)
    # 查找login
    login = html.xpath("//input[@type='password']")
    if login:
        print("yes!")
    else:
        print("no!")

async def spider_one_page(url):
    driver = webdriver.Chrome()
    driver.get(url)
    WebDriverWait(driver, 10)
    check(driver)

    # 打算在这里开始多进程'
    links = get_sub_links(driver)
    ret_lis = list()
    pool = Pool()
    for link in links:
        ret = pool.apply_async(spider_sub_page, args=(link,))
        ret_lis.append(ret)
    pool.close()
    pool.join()

    driver.close()
    driver.quit()



def spider():
    loop = asyncio.get_event_loop()
    cor = [spider_one_page(url) for url in urls]
    loop.run_until_complete(asyncio.gather(*cor))

def main():
    spider()
    return 0

if __name__ == "__main__":
    start_time = time.time()
    main()
    print('Use time:{:.2f}s'.format(time.time() - start_time))
