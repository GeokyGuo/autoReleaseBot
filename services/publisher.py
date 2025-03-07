import time
from abc import ABC, abstractmethod
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import logging

class ArticlePublisher(ABC):
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def get_title_locator(self):
        """返回标题输入框定位器"""
        pass

    @abstractmethod
    def get_content_locator(self):
        """返回内容编辑器定位器"""
        pass

    @abstractmethod
    def get_publish_btn_locator(self):
        """返回发布按钮定位器"""
        pass

    def safe_wait(self, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )

    def safe_click(self, element, wait=1):
        self.driver.execute_script("arguments[0].click();", element)
        time.sleep(wait)

    def set_title(self, title):
        title_input = self.safe_wait(self.get_title_locator())
        title_input.clear()
        title_input.send_keys(title)
        self.logger.info(f"已设置标题: {title}")

    def set_content(self, content):
        editor = self.safe_wait(self.get_content_locator())
        editor.clear()
        editor.send_keys(content)
        self.logger.info("内容填充完成")

    def execute_publish(self):
        publish_btn = self.safe_wait(self.get_publish_btn_locator())
        self.safe_click(publish_btn)
        self.logger.info("发布操作已执行")

    def publish_article(self, title, content):
        self.set_title(title)
        time.sleep(1)
        self.set_content(content)
        time.sleep(1)
        self.execute_publish()
        time.sleep(3)
        self.verify_publish_success()

    @abstractmethod
    def verify_publish_success(self):
        """验证发布成功的具体实现"""
        pass