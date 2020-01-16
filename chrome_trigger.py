import unittest
import os
import re
import time
import asyncio
import multiprocessing
import aiofiles
from lxml import etree
from selenium import webdriver
from multiprocessing import Pool
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as EC



# 防重的布隆函数
from pybloom_live import ScalableBloomFilter as SBF
global bf_ready, bf_file
global option, school_name
option = webdriver.ChromeOptions()
option.add_experimental_option('excludeSwitches', ['enable-automation'])

urls = [
    "https://id.tsinghua.edu.cn/"
]

def wrt(url):
    print("hi1")
    try:
        if not url in bf_file:
            print("hi2")
            bf_file.add(url)
            f_w = open(school_name + "_login_url.txt", 'a+')
            f_w.write(url)
            print("Login find! Url: {}".format(url))
    finally:
        f_w.close()

def Extractor(url):
    # print(url)
    num = url.count("/")
    if "?" in url:
        url_ = url.strip().split("?", 1)
        return url_[0]
    elif num >= 3:
        url_ = url.strip().rsplit("/", 1)
        return url_[0]
    else:
        return url.strip()


def spider_sub_page(link):
    global option
    driver_s = webdriver.Chrome(options=option)
    # driver_s.set_script_timeout(10)
    driver_s.get(link)
    try:
        WebDriverWait(driver_s, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='password']"))
        )
        return driver_s.current_url
    finally:
        driver_s.close()
        driver_s.quit()


def get_sub_links(driver, url):
    try:
        doc = driver.page_source
        html = etree.HTML(doc)
        # 查找所有的links
        links = list()
        for link in html.xpath("//a[@href]/@href"):
            if ("javascript:" in link) or (".pdf" in link):
                continue
            if not (re.match(r'http://', link) or re.match(r'https://', link)):
                link = url + link
            links.append(link)
        # print(links)
        return links
    except:
        return

# def check(driver):
#     print("now, checking {}".format(driver.current_url))
#     doc = driver.page_source
#     html = etree.HTML(doc)
#     # 查找login
#     login = html.xpath("//input[@type='password']")
#     if login:
#         print("find!!, {}".format(driver.current_url))
#     else:
#         print("no!")


async def spider_one_page(url):
    global bf_ready, option, school_name
    if not Extractor(url) in bf_ready:
        # print("1"+Extractor(url))
        bf_ready.add(Extractor(url))
        driver = webdriver.Chrome(options=option)
        print(url)
        driver.get(url)
        try:
            WebDriverWait(driver, 10, ignored_exceptions=True).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='password']"))
            )
            wrt(driver.current_url)
        finally:
            links = get_sub_links(driver, url)
            ret_lis = list()
            print(links)
            pool = Pool()
            for link in links:
                if Extractor(link) in bf_ready:
                    continue
                if not school_name in link:
                    continue
                else:
                   bf_ready.add(Extractor(link))
                   ret = pool.apply_async(spider_sub_page, args=(link,), callback=wrt)
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
    global bf_ready, bf_file
    bf_ready = SBF(initial_capacity=len(urls)*50, error_rate=0.001, mode=SBF.LARGE_SET_GROWTH)
    bf_file = SBF(initial_capacity=len(urls)*50, error_rate=0.001, mode=SBF.LARGE_SET_GROWTH)
    spider()
    return 0

if __name__ == "__main__":

    global school_name
    school_name = "tsinghua"
    # f_r = open(school_name + ".edu.cn.txt", 'r')
    # line = f_r.readline()
    # while line:
    #     line = line.strip()
    #     if len(line):
    #         print(line)
    #     line = f_r.readline()
    #     urls.append(line)
    start_time = time.time()
    main()
    print('Use time:{:.2f}s'.format(time.time() - start_time))
