import configparser
import json
import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# 判断是否登录成功
def is_login_successful(driver):
    try:
        # 显式等待用户头像元素出现，判断登录成功
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.xui-header-iconNav-item._uH'))
        )
        return True
    except Exception:
        return False


def loop_until_y_case_sensitive():
    while True:
        user_input = input("请输入字符（输入 'y' 退出循环）: ")
        if user_input == 'y':
            print("你输入了 'y'，循环结束。")
            break


# 手动登录函数
def manual_login(driver, username_str, password_str):
    driver.get('https://passport.ximalaya.com/page/web/login')
    time.sleep(3)

    # 定位并点击“账号密码登录”按钮
    login_tab_btn = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'login-tab-btn'))
    )
    login_tab_btn.click()

    # 等待账号和密码输入框出现
    username_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@placeholder="请输入手机号"]'))
    )
    password_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@placeholder="请输入密码"]'))
    )

    # 显式等待元素加载完成
    checkbox_element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.check-box span.check-box__box'))
    )

    # 模拟点击操作，勾选复选框
    checkbox_element.click()
    time.sleep(3)

    # 输入账号和密码
    username_input.send_keys(username_str)
    password_input.send_keys(password_str)

    # 显式等待登录按钮可点击
    login_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.btn.btn-primary.block.submit'))
    )
    login_btn.click()

    # 登录卡点，等待输入 y 继续
    loop_until_y_case_sensitive()

    if is_login_successful(driver):
        # 保存登录后的 Cookies
        cookies = driver.get_cookies()
        with open('ximalaya_cookies.json', 'w') as f:
            json.dump(cookies, f)
        return True
    return False


# 使用 Cookies 登录函数
# todo 待优化为打开网页前先添加cookie
def cookies_login(driver):
    try:
        with open('ximalaya_cookies.json', 'r') as f:
            cookies = json.load(f)
            driver.get('https://www.ximalaya.com/')
            time.sleep(3)
            # 添加 cookie
            for cookie in cookies:
                driver.add_cookie(cookie)
            driver.refresh()

            return is_login_successful(driver)
    except (FileNotFoundError, json.JSONDecodeError):
        return False


# 检查是否存在 cookie 文件且文件有内容
def cookie_file_exists():
    file_path = 'ximalaya_cookies.json'
    return os.path.exists(file_path) and os.path.getsize(file_path) > 0


# 上传作品函数
def upload_work(driver, file_path):
    # 打开创作者中心
    creator_center_url = 'https://creator.ximalaya.com/'
    driver.get(creator_center_url)

    # 显式等待上传作品按钮可点击
    upload_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "上传作品")]'))
    )
    upload_btn.click()

    # # 上传作品卡点，等待输入 y 继续
    # input("已点击上传作品按钮，请检查页面，确认无误后输入 y 继续: ")

    # 显式等待文件输入框出现
    file_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@type="file"]'))
    )
    file_input.send_keys(file_path)

    # 这里可以根据实际情况添加更多等待条件，例如上传进度条消失等
    time.sleep(10)


def main():
    # 设置 Chrome 浏览器选项
    chrome_options = Options()
    # 可以根据需要设置为无头模式，即不显示浏览器窗口
    # chrome_options.add_argument('--headless')

    # 配置 ChromeDriver 路径
    service = Service("../chromedriver-win64/chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 读取配置文件
    config = configparser.ConfigParser()
    config.read('config.ini')
    username = config.get('Credentials', 'username')
    password = config.get('Credentials', 'password')
    file_path = 'path/to/your/file.mp3'

    # 检查是否存在 cookie 文件
    if cookie_file_exists():
        if cookies_login(driver):
            print("使用 Cookies 登录成功！")
        else:
            print("Cookies 已过期或无效，进行手动登录。")
            if manual_login(driver, username, password):
                print("手动登录成功！")
            else:
                print("手动登录失败，请检查账号密码或网络。")
    else:
        print("没有有效的保存的 Cookies，进行手动登录。")
        if manual_login(driver, username, password):
            print("手动登录成功！")
        else:
            print("手动登录失败，请检查账号密码或网络。")

    time.sleep(5)
    # 上传作品
    upload_work(driver, file_path)
    print("作品上传成功！")

    # 关闭浏览器
    driver.quit()


if __name__ == "__main__":
    main()