# -*- coding: utf-8 -*-
# Author: 薄荷你玩
# Date: 2023/08/01

from selenium import webdriver
from lxml import etree
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


# 将爬虫封装成一个类
class BaiduSpider(object):
    def __init__(self):
        # 启动浏览器驱动
        self.driver = webdriver.Chrome()
        # 百度链接
        self.url = 'https://www.baidu.com/s?wd=薄荷分享网'

    def run(self):
        # 向服务器发出请求
        self.driver.get(self.url)
        # 显示等待，通过xpath定位找下一页
        while True:
            next_btn = WebDriverWait(driver=self.driver, timeout=100).until(
                EC.presence_of_element_located((By.XPATH, "//div[@id='page']/div/a[last()]"))
            )
            # # 获取下一页按钮
            # next_btn = self.driver.find_element(By.XPATH, "//div[@id='page']/div/a[last()]")
            # 第一页的情况不考虑
            curr_page = self.driver.find_element(By.XPATH, "//div[@id='page']/div/strong/span").text
            print("当前页码：", curr_page)
            # 判断是否是最后一页或者是第5页，若是，则停止；若不是，则点击下一页
            if "n" not in next_btn.get_attribute("class") or curr_page == "2":
                print("运行结束！")
                break
            else:
                next_btn.click()
            # 获取网页源代码
            source = self.driver.page_source
            # 获取每个检索结果的链接
            self.parse_list_page(source)

    # 获取每个检索结果的链接
    def parse_list_page(self, source):
        # 将网页源代码改成html格式，以便使用xpath定位元素
        html = etree.HTML(source)
        # 获取每个条目的链接
        links = html.xpath("//div[@class='c-container']/div/h3/a/@href")
        for link in links:
            print(link)
            # 根据链接获取每个页面的详细信息（自定义函数）
            self.request_detail_page(link)
        # time.sleep(1)

    # 根据链接获取每个页面的详细信息
    def request_detail_page(self, url):
        # 打开每个链接
        self.driver.execute_script("window.open('%s')" % url)
        # 利用句柄，页面切换到对应链接的页面
        self.driver.switch_to.window(self.driver.window_handles[1])
        # 等待页面加载完成
        wait = WebDriverWait(self.driver, 100)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        source = self.driver.page_source
        # 爬取详细页面的信息（自定义函数）
        self.parse_detail_page(source)
        # 关闭该链接的页面，切换回原先的页面
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    # 解析页面内容
    def parse_detail_page(self, source):
        html = etree.HTML(source)
        title = html.xpath("(//head/title)")[0].text
        current_url = self.driver.current_url
        print(title, current_url)
        print()


if __name__ == '__main__':
    spider = BaiduSpider()
    spider.run()
