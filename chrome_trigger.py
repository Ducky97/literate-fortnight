import time
from lxml import etree
from selenium import webdriver
from multiprocessing import Pool
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
# 防重的布隆函数
from pybloom_live import ScalableBloomFilter as SBF

bf_ready = SBF(error_rate=0.001, mode=SBF.LARGE_SET_GROWTH)
bf_file = SBF(error_rate=0.001, mode=SBF.LARGE_SET_GROWTH)

option = webdriver.ChromeOptions()
option.add_experimental_option('excludeSwitches', ['enable-automation'])

# 这里记得改
school_name = 'tsinghua'

def Extractor(url):
    # print(url)
    num = url.count("/")
    if "?" in url:
        url_ = url.strip().split("?", 1)
        return url_[0]
    elif num >= 3:
        if url[-1] == "/":
            url_ = url.strip().rsplit("/", 1)
        url_ = url.strip().rsplit("/", 1)
        return url_[0]
    else:
        return url.strip()

def check_login(driver):
    # print("now, checking {}".format(driver.current_url))
    doc = driver.page_source
    html = etree.HTML(doc)
    # 查找login
    login = html.xpath("//input[@type='password']")
    if login:
        print("Login find! Url: {}".format(driver.current_url))
        return driver.current_url
    else:
        return None

def check_sub_login(driver):
    login_urls = list()
    # print("then, checking sub login {}".format(driver.current_url))
    elements = driver.find_elements_by_partial_link_text("登录")
    # print("elements, {}".format(elements))
    for i in range(len(elements)):
        elements[i].click()
        WebDriverWait(driver, 5, ignored_exceptions=True).until(
            EC.presence_of_all_elements_located
        )
        login_url = check_login(driver)
        if login_url:
            login_urls.append(driver.current_url)
        driver.back()
        elements = driver.find_elements_by_partial_link_text("登录")
    return login_urls


def spider(url):
    global option
    login_urls = list()
    driver = webdriver.Chrome(options = option)
    driver.get(url)
    time.sleep(15)
    # 检查两种情况
    # 情况一：当前页面有login
    login_url = check_login(driver)
    if login_url:
        login_urls.append(login_url)
    # 情况二：当前页面有很多个登录buttion
    login_sub_urls = check_sub_login(driver)
    for sub_url in login_sub_urls:
        login_urls.append(sub_url)
    driver.close()
    driver.quit()
    print(login_urls)
    return login_urls


def wrt(login_urls):
    global bf_file
    try:
        f_w = open(school_name + "_login_url.txt", 'a+')
        for url in login_urls:
            if not url in bf_file:
                bf_file.add(url)
                f_w.write(url+"\n")
    finally:
        f_w.close()


def main(urls):
    global bf_ready
    ret_lis = list()
    pool = Pool()
    for url in urls:
        # 先判断是否检查过
        # print("Extractor: {}, {}", url, Extractor(url))
        if Extractor(url) in bf_ready:
            continue
        # print("Extractor add, {}", Extractor(url))
        bf_ready.add(Extractor(url))
        ret = pool.apply_async(spider, args=(url,), callback=wrt)
        ret_lis.append(ret)
    pool.close()
    pool.join()



if __name__ == "__main__":
    start_time = time.time()
    f_r = open(school_name + ".edu.cn.txt", 'r')
    line = f_r.readline()
    while line:
        urls = list()
        for i in range(20):
            if not line:
                break
            else:
                urls.append(line.strip())
                line = f_r.readline()
        start_time_main = time.time()
        main(urls)
        print('20 domain use time:{:.2f}s'.format(time.time() - start_time_main))
        line = f_r.readline()
    print('Use time:{:.2f}s'.format(time.time() - start_time))
