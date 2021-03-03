import sys
from pixiv.pixivbase import PixivBase
import threading
from utils.utils import get_ip, download, replace_data, create_thread, join_thread
from utils.image_data import ImageData
import json
import requests
from bs4 import BeautifulSoup


class pixiv_recommand(PixivBase):

    def __init__(self, cookie='', thread_number=3):
        super().__init__(cookie, thread_number)
        self.url = ''

    def get_urls(self):
        self.url='https://www.pixiv.net/ajax/top/illust?mode=all&lang=zh'

    def run_get_picture_url(self):
        """
        获取全部图片URL
        :return:
        """
        url = self.url
        if not self.proxy:
            req = requests.get(url, headers=self.headers,
                                   cookies=self.cookie).text
        else:
            ip = get_ip()
            proxies = {
                'http': 'http://' + ip,
                # 'https': 'https://' + proxy
            }
            req = requests.get(url, headers=self.headers,
                                   cookies=self.cookie, proxies=proxies).text
        new_data = json.loads(json.dumps(req))
        # 处理json数据
        # 字符串转字典
        _dict = eval(replace_data(new_data))
        # 获取图片数据
        info = _dict['body']['page']['recommend']['ids']

        for cnt in info:
            self.picture_id.append(ImageData(cnt))


    def run(self):
        """
        运行获取推荐图片功能
        :return:
        """
        self.get_urls()

        self.run_get_picture_url()
        # 获取线程
        thread_lst = []

        # 启动多个线程 获取图片ID
        # for _ in range(self.thread_number):
        #     t = utils.utils.create_thread(self.run_get_picture_url)
        #     thread_lst.append(t)
        # # 阻塞线程 等执行完后再去筛选图片
        # for thread_ in thread_lst:
        #     thread_.join()

        # 获取合适图片用于下载
        for _ in range(self.thread_number * 2):
            t = create_thread(self.get_picture_info, self.picture_id)
        thread_lst.append(t)
        # 阻塞线程 等执行完后再去下载图片
        join_thread(thread_lst)

        # 下载图片
        for _ in range(self.thread_number):
            t = create_thread(download, self.result)
        thread_lst.append(t)
        # 阻塞线程 等执行完
        join_thread(thread_lst)
