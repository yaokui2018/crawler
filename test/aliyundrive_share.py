# -*- coding: utf-8 -*-
# Author: 薄荷你玩
# Date: 2023/10/27
import time
import pandas as pd
from playwright.sync_api import Playwright, sync_playwright

DATA_SAVE_PATH = "aliyundrive/data.csv"


def write_data(filename, share_link, save_path=DATA_SAVE_PATH):
    id = filename.split("-")[0]
    with open(save_path, 'a+', encoding="utf8") as f:
        f.write(f"{id},{filename},{share_link}\n")


def load_exists_data(file_path=DATA_SAVE_PATH):
    data = pd.read_csv(file_path)
    filenames, last_id = [], 0
    if not data.empty:
        filenames = list(data.iloc[:, 1].values)
        last_id = data.iloc[-1, 0]
    return filenames, last_id


class AliyundriveSpider(object):
    def __init__(self, playwright: Playwright):
        # 获取分享数据
        self.filenames, self.last_id = load_exists_data()
        # 启动浏览器驱动
        self.browser = playwright.chromium.launch(headless=False)  # 隐藏浏览器窗口
        # 入口链接
        self.url = 'https://www.aliyundrive.com/drive/file/resource/610c8bf54a67eb65551e4c1b9969bcb99a3bcca5'

    def run(self):
        # 向服务器发出请求
        # context = self.browser.new_context()
        # 加载本地cookies，免登陆
        context = self.browser.new_context(storage_state="aliyundrive/auth.json")
        page = context.new_page()
        page.goto(self.url)
        # 设置全局的超时时间为5秒
        page.set_default_timeout(5000)
        # 等待新页面加载完成
        page.wait_for_load_state('domcontentloaded')
        curr_url = page.url
        # 判断是否登录
        try:
            if "https://www.aliyundrive.com/sign/in" not in curr_url:
                page.locator('#login').inner_text()
            input("请先完成登录后按回车继续：")
            # 保存状态文件
            context.storage_state(path="aliyundrive/auth.json")
        except Exception as e:
            print("未发现登录页")
        # 下滑页面 20010
        total_num = self.last_id + 200
        print(f"起始滑动值：total_num = {total_num}")
        page.evaluate("""
            var scrollableDiv = document.getElementsByClassName("grid-scroll--O0kCz")[0];
            var listSum = document.getElementsByClassName("list-sum--0pQHO")[0];
            function run() {
                scrollableDiv.scrollTop = scrollableDiv.scrollTop  + 100000; 
                let sum = listSum.innerText.replace("共 ", "").replace(" 项", "");
                if(sum < {TOTAL_NUM}){
                    console.log(listSum.innerText);
                    setTimeout(run , 500);                    
                }                
            }
            run();    
        """.replace("{TOTAL_NUM}", str(total_num)))
        while int(page.locator(".list-sum--0pQHO").inner_text().replace("共 ", "").replace(" 项", "")) < total_num:
            print(page.locator(".list-sum--0pQHO").inner_text())
            time.sleep(10)
        page.locator(".node-card--wp9KL").last.click()
        err_times = 0
        while True:
            filename = page.locator("span[class='text--KBVB3']").inner_text()
            if filename not in self.filenames:
                # 右侧分享按钮
                page.locator(".toolbar-wrapper--SUoJx > div:nth-child(3) > .icon--D3kMk > svg").click()
                try:
                    if "因为格式限制，暂不支持公开分享" in page.locator(".content-wrapper--BNHuN").inner_text():
                        share_link = "因为格式限制，暂不支持公开分享"
                        save_path = "aliyundrive/err.csv"
                    else:
                        # 选择有效期
                        page.get_by_label("分享文件").get_by_role("img").nth(3).click()
                        page.get_by_text("永久有效").click()
                        page.get_by_role("button", name="创建分享").click()
                        if err_times >= 3:
                            # 判断今日是否分享达到上限
                            try:
                                element = page.wait_for_selector('.content-wrapper--A93tB')
                                # 今日分享次数已达上限\n点击查看细则
                                print(element.inner_text())
                                break
                            except Exception as e:
                                pass
                        share_link = page.locator("div[class='url--9yHLX']").inner_text()
                        save_path = 'aliyundrive/data.csv'
                    print(filename, share_link)
                    write_data(filename, share_link, save_path=save_path)
                    page.locator(".icon-wrapper--TbIdu").click()
                except Exception as e:
                    print(f"Err: {e}")
                    # time.sleep(1)
                    page.locator(".icon-wrapper--TbIdu").click()
                    err_times += 1
                    err_tips = "超时"
                    if err_times <= 3:
                        print("未达到错误次数限制，继续尝试", err_times)
                        continue
                    print(err_tips + "跳过！")
                    write_data(filename, err_tips, save_path="aliyundrive/err.csv")
            else:
                print("该文件已存在，下一位 ", filename)
            err_times = 0
            prev_item = page.locator(".nav-prev--f5MXf")
            if "disabled--S9d6m" not in prev_item.get_attribute('class'):
                prev_item.click()
            else:
                print("over")
                break
        print("运行结束！")
        input()
        context.close()


if __name__ == '__main__':
    with sync_playwright() as playwright:
        spider = AliyundriveSpider(playwright)
        spider.run()
        spider.browser.close()
