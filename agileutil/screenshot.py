#coding=utf-8

'''
python 2.7+
pip install selenium
download chromedriver from https://npm.taobao.org/mirrors/chromedriver/
'''

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import traceback
import time

class Screenshot(object):

    def __init__(self, url, width, height, driverPath, pic, sleepIntval = 10):
        self.url = url
        self.width = width
        self.height = height
        self.driverPath = driverPath
        self.pic = pic
        self.sleepIntval = sleepIntval

    def save(self):
        '''
        保存截图
        成功返回None, 否则返回错误信息
        '''
        try:
            os.environ["webdriver.chrome.driver"] = self.driverPath
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--headless')
            driver = webdriver.Chrome(self.driverPath, chrome_options=chrome_options)
            driver.set_window_size(self.width, self.height)
            driver.get(self.url)
            time.sleep(self.sleepIntval)
            driver.save_screenshot(self.pic)
            driver.close()
            return None
        except Exception as ex:
            return str(ex) + traceback.format_exc()