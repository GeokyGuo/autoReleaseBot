import configparser
import json
import os
import time
from datetime import datetime
import logging
from util.log_util import setup_logger
from util.auth import BaseLoginHandler
from services.publisher import ArticlePublisher
from util.storage import StorageUtil
from browser.core import SmartWaiter
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# 初始化日志配置
setup_logger('icity自动化', 'icity_automation.log')

# 判断是否登录成功
def is_login_successful(driver):
    try:
        # 这里需要根据icity.ly登录成功后的页面特征来确定定位元素，假设是一个特定的用户信息元素
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'img.avatar'))
        )
        logging.info("检测到登录成功标识，登录成功")
        return True
    except Exception:
        logging.warning("未检测到登录成功标识，登录可能失败")
        return False


def loop_until_y_case_sensitive():
    while True:
        user_input = input("请输入字符（输入 'y' 退出循环）: ")
        if user_input == 'y':
            logging.info("你输入了 'y'，循环结束。")
            break


def js_click_and_wait(driver, target_button, wait_time=1):
    driver.execute_script("arguments[0].click();", target_button)
    time.sleep(wait_time)


def save_cookies(driver, file_path='icity_cookies.json'):
    cookies = driver.get_cookies()
    with open(file_path, 'w') as f:
        json.dump(cookies, f)
    logging.info(f"已将Cookies保存到 {file_path}")


def delete_cookies_file(file_path='icity_cookies.json'):
    if os.path.exists(file_path):
        # 获取文件的目录和文件名
        dir_name, file_name = os.path.split(file_path)
        # 生成新的文件名，添加 _bak 后缀
        new_file_name = os.path.splitext(file_name)[0] + '_bak' + os.path.splitext(file_name)[1]
        # 生成新的文件路径
        new_file_path = os.path.join(dir_name, new_file_name)
        # 重命名文件
        os.rename(file_path, new_file_path)
        logging.info(f"文件 {file_path} 已重命名为 {new_file_path}")

class ICityLoginHandler(BaseLoginHandler):
    def __init__(self, driver):
        super().__init__(driver, 'icity')
        self.login_url = 'https://icity.ly/login'

    def get_login_elements(self):
        return {
            'username': (By.CSS_SELECTOR, 'input[name="username"]'),
            'password': (By.CSS_SELECTOR, 'input[name="password"]'),
            'submit': (By.XPATH, '//button[contains(text(),"登录")]')
        }

    def verify_login_state(self):
        try:
            return self.driver.find_element(By.CSS_SELECTOR, 'img.avatar').is_displayed()
        except:
            return False

    def manual_login(self):
        elements = self.get_login_elements()
        creds = self.load_config()
        waiter = SmartWaiter(self.driver)
        
        username = waiter.wait_for_element(elements['username'])
        password = waiter.wait_for_element(elements['password'])
        
        username.send_keys(creds['username'])
        password.send_keys(creds['password'])
        
        submit = waiter.wait_for_element(elements['submit'])
        waiter.safe_click(submit)
        return self.verify_login_state()

class ICityPublisher(ArticlePublisher):
    def get_title_locator(self):
        return (By.CSS_SELECTOR, 'input.article-title')

    def get_content_locator(self):
        return (By.CSS_SELECTOR, 'div.editor-content')

    def get_publish_btn_locator(self):
        return (By.XPATH, '//button[contains(text(),"发布")]')

    def verify_publish_success(self):
        return self.safe_wait((By.XPATH, '//div[contains(text(),"发布成功")]'))

def main():
    chrome_options = Options()
    service = Service("../chromedriver-win64/chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    login_handler = ICityLoginHandler(driver)
    if not login_handler.execute_login_flow():
        logging.error("登录失败")
        return

    publisher = ICityPublisher(driver)
    title, content = StorageUtil.parse_article_content(
        StorageUtil.generate_file_path("C:\\Users\\jayden\\Desktop\\创作空间")
    )
    publisher.publish_article(title, content)

    time.sleep(5)
    driver.quit()
    logging.info("浏览器已关闭")

if __name__ == "__main__":
    main()