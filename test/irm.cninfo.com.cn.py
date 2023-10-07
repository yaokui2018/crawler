# -*- coding: utf-8 -*-
# Author: 薄荷你玩
# Date: 2023/10/07

import csv
import datetime
import json

import requests

URL = 'http://irm.cninfo.com.cn/newircs/index/search'
SAVE_PATH = 'result.csv'
SAVE_HEADER = ['序号,问题,答复,公司名,提问者,来源,pubClient,提问时间,答复时间,原始数据\n']

PLATFORM_MAP = {
    '1': 'App',
    '2': 'App',
    '4': '网站',
    '6': '网站',
    '5': '公众号'
}


def write_data(lines: list, is_init=False):
    if is_init:
        with open(SAVE_PATH, 'w', encoding='utf8') as f:
            f.writelines(lines)
        return
    with open(SAVE_PATH, 'a+', encoding='utf8', newline='') as f:
        writer = csv.writer(f)
        for line in lines:
            writer.writerow(line)


def timestamp2str(timestamp):
    if type(timestamp) == str:
        timestamp = int(timestamp) / 1000
    # 将时间戳转换为日期时间对象
    dt_object = datetime.datetime.fromtimestamp(timestamp)
    formatted_date = dt_object.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_date


def get_question_answer(index=1, page=1):
    url = URL
    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.289 Safari/537.36',
    }

    data = {
        "pageNo": page,
        "pageSize": 100,
        "searchTypes": "1,11",
        "highLight": True
    }

    response = requests.post(url, headers=headers, data=data).json()
    results = response['results']
    print(len(results))
    if len(results) > 0:
        lines = []
        for data in results:
            question = data['mainContent']
            question_time = timestamp2str(data['pubDate'])
            author_name = data['authorName']
            pub_client = data['pubClient']
            platform = PLATFORM_MAP['4' if pub_client not in PLATFORM_MAP.keys() else pub_client]
            if data['contentType'] == 11:
                answer = data['attachedContent']
                answer_time = timestamp2str(data['attachedPubDate'])
                company_name = f"{data['attachedAuthor']} [{data['stockCode']}]"
            else:
                answer = ''
                answer_time = ''
                company_name = ''

            line = [index, question, answer, company_name, author_name, platform, pub_client, question_time,
                    answer_time, json.dumps(data)]
            lines.append(line)
            index += 1
        write_data(lines)
        print("继续获取下一页数据：", page + 1)
        get_question_answer(index, page + 1)
    else:
        print("没有数据了")


if __name__ == '__main__':
    write_data(SAVE_HEADER, True)
    get_question_answer()
