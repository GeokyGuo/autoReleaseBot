import os
import json
import logging
from abc import ABC, abstractmethod
from configparser import ConfigParser
from selenium.webdriver.remote.webdriver import WebDriver

class BaseLoginHandler(ABC):
    def __init__(self, driver: WebDriver, platform: str):
        self.driver = driver
        self.platform = platform
        self.cookie_file = f'{platform}_cookies.json'
        self.config = ConfigParser()
        
    def load_config(self):
        self.config.read('config.ini')
        return {
            'username': self.config.get('Credentials', 'username'),
            'password': self.config.get('Credentials', 'password')
        }

    @abstractmethod
    def get_login_elements(self):
        """返回平台特定的登录元素定位器"""
        pass

    def cookie_login(self):
        try:
            with open(self.cookie_file, 'r') as f:
                cookies = json.load(f)
                self.driver.get(self.login_url)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
                self.driver.refresh()
                return self.verify_login_state()
        except Exception as e:
            logging.error(f'Cookie登录失败: {str(e)}')
            return False

    @abstractmethod
    def verify_login_state(self) -> bool:
        """验证登录状态的具体实现"""
        pass

    def execute_login_flow(self):
        if os.path.exists(self.cookie_file):
            if not self.cookie_login():
                return self.manual_login()
            return True
        return self.manual_login()

    @abstractmethod
    def manual_login(self):
        """平台特定的手动登录流程"""
        pass