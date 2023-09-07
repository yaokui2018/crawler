# -*- coding: utf-8 -*-
# Author: 薄荷你玩
# Date: 2023/08/04
import time
from lxml import etree
from playwright.sync_api import Playwright, sync_playwright


class BaiduSpider(object):
    def __init__(self, playwright: Playwright):
        # 启动浏览器驱动
        self.browser = playwright.chromium.launch(headless=True)  # 隐藏浏览器窗口
        # 百度链接
        self.url = 'https://www.baidu.com/'

    def run(self):
        # 向服务器发出请求
        context = self.browser.new_context()
        page = context.new_page()
        page.goto(self.url)
        page.locator("#kw").click()
        page.locator("#kw").fill("薄荷分享网")
        page.locator("#kw").press("Enter")
        # 显示等待，通过xpath定位找下一页
        while True:
            # with page.expect_popup() as page1_info:
            #     page.get_by_role("link", name="薄荷分享网 - 分享是一种快乐!| 猿博客", exact=True).click()
            # page1 = page1_info.value
            # # 等待 DOM 内容加载完成
            # page1.wait_for_load_state('domcontentloaded')
            # print(page1.title(), page1.url)
            # page1.close()

            # 获取下一页按钮
            next_btn = page.wait_for_selector("//div[@id='page']/div/a[last()]")
            # 第一页的情况不考虑
            curr_page_element = page.wait_for_selector("//div[@id='page']/div/strong/span")
            curr_page = curr_page_element.inner_text()
            print("当前页码：", curr_page)
            # 获取每个检索结果的链接
            self.parse_list_page(page.content())
            # 判断是否是最后一页或者是第5页，若是，则停止；若不是，则点击下一页
            if "n" not in next_btn.get_attribute("class") or curr_page == "5":
                print("运行结束！")
                context.close()
                break
            else:
                next_btn.scroll_into_view_if_needed()
                next_btn.click()
                time.sleep(1)
                # 等待新页面加载完成
                page.wait_for_load_state('domcontentloaded')

    # 获取每个检索结果的链接
    def parse_list_page(self, source):
        # 将网页源代码改成html格式，以便使用xpath定位元素
        html = etree.HTML(source)
        # 获取每个条目的真实链接
        real_links = html.xpath("//div[contains(@class, 'c-container') and contains(@class, 'xpath-log')]/@mu")
        print("真实链接：")
        for real_link in real_links:
            print(real_link)
        print()
        # 获取每个条目的链接
        links = html.xpath("//div[@class='c-container']/div/h3/a/@href")
        for link in links:
            print(link)
            # 根据链接获取每个页面的详细信息（自定义函数）
            self.request_detail_page(link)

    # 根据链接获取每个页面的详细信息
    def request_detail_page(self, url):
        # 打开每个链接
        context = self.browser.new_context()
        page = context.new_page()
        page.goto(url)
        source = page.content()
        # 爬取详细页面的信息（自定义函数）
        title = self.parse_detail_page(source)
        curr_url = page.url
        print(title, curr_url)
        print()
        context.close()

    # 解析页面内容
    def parse_detail_page(self, source):
        html = etree.HTML(source)
        title = html.xpath("(//head/title)")[0].text
        return title


if __name__ == '__main__':
    with sync_playwright() as playwright:
        spider = BaiduSpider(playwright)
        spider.run()
        spider.browser.close()
