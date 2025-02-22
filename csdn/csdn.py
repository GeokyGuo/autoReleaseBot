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
            EC.presence_of_element_located((By.CSS_SELECTOR, '.user-avatar'))
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
    driver.get('https://passport.csdn.net/login')
    time.sleep(3)

    # 定位并点击“账号密码登录”按钮
    login_tab_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//a[@title="账号密码登录"]'))
    )
    login_tab_btn.click()

    # 等待账号和密码输入框出现
    username_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'all'))
    )
    password_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'password-number'))
    )

    # 输入账号和密码
    username_input.send_keys(username_str)
    password_input.send_keys(password_str)

    # 显式等待登录按钮可点击
    login_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//button[@type="submit"]'))
    )
    login_btn.click()

    # 登录卡点，等待输入 y 继续
    loop_until_y_case_sensitive()

    if is_login_successful(driver):
        # 保存登录后的 Cookies
        cookies = driver.get_cookies()
        with open('csdn_cookies.json', 'w') as f:
            json.dump(cookies, f)
        return True
    return False


# 使用 Cookies 登录函数
def cookies_login(driver):
    try:
        with open('csdn_cookies.json', 'r') as f:
            cookies = json.load(f)
            driver.get('https://www.csdn.net/')
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
    file_path = 'csdn_cookies.json'
    return os.path.exists(file_path) and os.path.getsize(file_path) > 0


# 发布文章函数
def publish_article(driver, title, content):
    # 打开创作中心
    creator_center_url = 'https://editor.csdn.net/md'
    driver.get(creator_center_url)

    # 显式等待标题输入框出现
    title_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'article-title'))
    )
    title_input.send_keys(title)

    # 显式等待内容输入框出现
    content_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.w-e-text'))
    )
    driver.execute_script(f"arguments[0].innerHTML = '{content}'", content_input)

    # 显式等待发布按钮可点击
    publish_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "发布")]'))
    )
    publish_btn.click()

    time.sleep(5)


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
    article_title = '自动化发布文章测试'
    article_content = '这是一篇使用 Selenium 自动化发布的测试文章。'

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
    # 发布文章
    publish_article(driver, article_title, article_content)
    print("文章发布成功！")

    # 关闭浏览器
    driver.quit()


if __name__ == "__main__":
    main()