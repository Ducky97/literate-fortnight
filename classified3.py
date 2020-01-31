import json
import time
import requests
from multiprocessing import Pool
from selenium import webdriver
from lxml import etree
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as EC

global school_name
option = webdriver.ChromeOptions()
option.add_experimental_option('excludeSwitches', ['enable-automation'])

def add(l_a, l_b):
    for l in l_b:
        if not l in l_a:
            l_a.append(l)

def get_login_elements(driver):
    elements = list()
    try:
        element_dl = driver.find_elements_by_partial_link_text("登录")
        add(elements, element_dl)
    except:
        pass
    try:
        element_rk = driver.find_elements_by_partial_link_text("入口")
        add(elements, element_rk)
    except:
        pass
    try:
        element_gly = driver.find_elements_by_partial_link_text("管理员")
        add(elements, element_gly)
    except:
        pass
    try:
        element_cbz = driver.find_elements_by_partial_link_text("登陆")
        add(elements, element_cbz)
    except:
        pass
    try:
        element_zc = driver.find_elements_by_partial_link_text("注册")
        add(elements, element_cbz)
    except:
        pass
    try:
        element_lg = driver.find_elements_by_partial_link_text("login")
        add(elements, element_lg)
    except:
        pass
    return elements

def check_sub_login(driver):
    elements = get_login_elements(driver)
    if len(elements) >= 1:
        print("Login find! Url: {}".format(driver.current_url))
        return True
    else:
        return None

def check_main_login(driver):
    # print("now, checking {}".format(driver.current_url))
    try:
        doc = driver.page_source
        html = etree.HTML(doc)
    except:
        return None
    try:
        WebDriverWait(driver, 5, ignored_exceptions=True).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='password']"))
        )
        print("Login find! Url: {}".format(driver.current_url))
        return True
    except:
        return None

def check_login(driver):
    # 检查两种情况
    # 情况一：当前页面有login
    login_main_url = check_main_login(driver)
    # 情况二：当前页面有很多个登录buttion
    login_sub_url = check_sub_login(driver)
    if login_main_url or login_sub_url:
        return driver.current_url
    else:
        return None

def get_status_code(current_url, url):
    # if not current_url:
    #     return None
    # 因为driver可能无效
    try:
        # print("requests: ", current_url)
        if current_url:
            status_code = requests.get(current_url, timeout=5).status_code
        else:
            status_code = requests.get(url, timeout=5).status_code
        return status_code
    except Exception as e:
        return str(e)

def start_driver(url):
    try:
        driver = webdriver.Chrome(options=option)
        WebDriverWait(driver, 5, ignored_exceptions=True).until(
            EC.presence_of_element_located
        )
        # WebDriverWait(driver, 5, ignored_exceptions=True).until(
        #     EC.presence_of_element_located or By.XPATH("//span[@jsselect='heading'][text()='无法访问此网站']")
        # )
        driver.get(url)
        doc = driver.page_source
        html = etree.HTML(doc)
        if html.xpath("//span[@jsselect='heading'][text()='无法访问此网站']") and \
                html.xpath(("//p[@jsselect='summary']")) and \
                html.xpath(("//button[@id='reload-button'][text()='重新加载']")) and \
                html.xpath("//button[text()='详细信息']") and \
                html.xpath("//div[@id='details']"):
            print("close succeed!!!")
            driver.close()
            driver.quit()
            return None
        return driver
    except:
        return None

def connection(url):
    driver = start_driver(url)
    current_url = None
    status_code = None
    login_url = None

    if driver:
        current_url = driver.current_url
        # status_code = get_status_code(current_url)
        login_url = check_login(driver)
        try:
            driver.close()
            driver.quit()
        except:
            driver.quit()
    status_code = get_status_code(current_url, url)
    # print(((status_code, current_url), login_url))
    return ((status_code, current_url), login_url)


def test(domain):
    login = set()
    # 先检测https
    url_s = "https://" + domain
    r_s = connection(url_s)
    if r_s[1]:
        login.add(r_s[1])
    # print("http!!!!")
    # 先检测http
    url = "http://" + domain
    r = connection(url)
    if r[1]:
        login.add(r[1])

    dict = {
        'domain': domain,
        'http': r[0],
        'https': r_s[0]
    }
    # result = ({'url': url, 'current_url': url}, "hello")
    result = (dict, login)
    print(result)
    return result

def wrt(result):
    print("Result: {}".format(result))
    global school_name
    f_result_w = open("E:\\https_project\\result\\" + school_name + "_result.json", 'a+')

    result_dict = result[0]
    # print(type(result_dict))
    result_json = json.dumps(result_dict)
    f_result_w.write(result_json)
    f_result_w.write("\n")
    f_result_w.close()

    if len(result[1]):
        f_login_w = open("E:\\https_project\\result\\" + school_name + "_login_result.txt", 'a+')
        for url in result[1]:
            login_url = url + '\n'
            f_login_w.write(login_url)
        f_login_w.close()

def main(domains):
    ret_lis = list()
    pool = Pool()
    for domain in domains:
        ret = pool.apply_async(test, args=(domain,), callback=wrt)
        ret_lis.append(ret)
    pool.close()
    pool.join()

if __name__ == "__main__":
    start_time = time.time()
    school_name = input("input the school name: ")
    f_r = open("E:\\https_project\\domain\\" + school_name + ".txt", 'r')
    line = f_r.readline()
    j = 1
    while line:
        domains = list()
        for i in range(20):
            if not line:
                break
            else:
                domains.append(line.strip())
                line = f_r.readline()
        start_time_main = time.time()
        # print(domains)
        main(domains)
        print('20 domain use time:{:.2f}s'.format(time.time() - start_time_main))
        j = j + 1
        print(j)
        line = f_r.readline()
    print('Use time:{:.2f}s'.format(time.time() - start_time))
    # school_name = "dlmu"
    # domain = input("input a domain: ")
    # r = test(domain)
    # print(r)
    # wrt(r)