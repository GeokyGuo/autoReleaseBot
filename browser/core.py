from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time

class SmartWaiter:
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.timeout = timeout
        self.logger = logging.getLogger(self.__class__.__name__)

    def wait_for_element(self, locator):
        """智能等待元素出现"""
        try:
            return WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located(locator)
            )
        except Exception as e:
            self.logger.error(f"元素定位失败: {locator}")
            raise

    def safe_click(self, element, wait=1):
        """安全点击操作"""
        try:
            self.driver.execute_script("arguments[0].click();", element)
            time.sleep(wait)
        except Exception as e:
            self.logger.error(f"点击操作失败: {str(e)}")
            raise

    def switch_to_frame(self, frame_locator):
        """框架切换处理"""
        try:
            frame = self.wait_for_element(frame_locator)
            self.driver.switch_to.frame(frame)
        except Exception as e:
            self.logger.error(f"框架切换失败: {frame_locator}")
            raise