## crawler

![GitHub last commit](https://img.shields.io/github/last-commit/yaokui2018/crawler)
![](https://img.shields.io/badge/python-3.8-blue)

一些爬虫自动化工具的简单使用..

(仅包含模拟浏览器的web自动化工具，requests+bs4可参考：[yaokui2018/picture_climb](https://github.com/yaokui2018/picture_climb/blob/master/spider.py))

###  环境依赖
`pip install -r requirements.txt`

### 1. selenium
Selenium是一个用于Web应用程序测试的工具。Selenium测试直接运行在浏览器中，就像真正的用户在操作一样。支持的浏览器包括IE（7, 8, 9, 10, 11），Mozilla Firefox，Safari，Google Chrome，Opera，Edge等。
**优点**：
- 可视化界面，易于入门，对于初学者来说上手较容易。
- 不需要深入理解动态加载和后端交互的细节，即可进行数据采集。
- 操作方式与普通人在网页上进行操作的习惯相符合。

**缺点**：
- 加载效率较低，可能会导致页面阻塞和采集效率低下。
- 在迁移至没有界面的 Linux 环境时，可能需要进行较多的修改和适配工作。
- 可视化采集容易受到浏览器问题影响，稳定性相对较差。

#### Demo
`python selenium_demo.py`
