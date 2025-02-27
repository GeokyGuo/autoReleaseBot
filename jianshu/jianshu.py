import configparser
import json
import os
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from util.log_util import setup_logger

# 配置日志记录
logging = setup_logger('简书自动化', 'jianshu_automation.log')


# 判断是否登录成功
def is_login_successful(driver):
    try:
        # 简书登录成功后，用户头像会显示，以此判断登录状态
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.user'))
        )
        return True
    except Exception:
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


def save_cookies(driver, file_path='jianshu_cookies.json'):
    cookies = driver.get_cookies()
    with open(file_path, 'w') as f:
        json.dump(cookies, f)
    logging.info(f"已保存Cookies到 {file_path}")


def delete_cookies_file(file_path='jianshu_cookies.json'):
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


# 手动登录函数
def manual_login(driver):
    config = configparser.ConfigParser()
    config.read('config.ini')
    username_str = config.get('Credentials', 'username')
    password_str = config.get('Credentials', 'password')

    driver.get('https://www.jianshu.com/sign_in')
    time.sleep(3)

    # 等待账号和密码输入框出现
    username_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@placeholder="手机号或邮箱"]'))
    )
    password_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@placeholder="密码"]'))
    )
    # 输入账号和密码
    username_input.send_keys(username_str)
    password_input.send_keys(password_str)

    # 显式等待登录按钮可点击
    login_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[id="sign-in-form-submit-btn"]'))
    )
    js_click_and_wait(driver, login_btn)

    # 登录卡点，等待输入y继续
    loop_until_y_case_sensitive()

    if is_login_successful(driver):
        save_cookies(driver)
        logging.info("手动登录成功！")
        return True
    logging.error("手动登录失败，请检查账号密码或网络。")
    return False


# 使用Cookies登录函数
def cookies_login(driver):
    try:
        with open('jianshu_cookies.json', 'r') as f:
            cookies = json.load(f)
            driver.get('https://www.jianshu.com/')
            time.sleep(3)
            for cookie in cookies:
                driver.add_cookie(cookie)
            driver.refresh()
            time.sleep(3)

            if is_login_successful(driver):
                logging.info("使用Cookies登录成功！")
                return True
            else:
                logging.warning("Cookies已过期或无效，进行手动登录。")
                return False
    except Exception as e:
        delete_cookies_file()
        logging.error(f"登录时出现异常: {e}，已删除 jianshu_cookies.json 文件。")
        return False


# 检查是否存在cookie文件且文件有内容
def cookie_file_exists():
    file_path = 'jianshu_cookies.json'
    return os.path.exists(file_path) and os.path.getsize(file_path) > 0


def new_post(driver):
    # 显式等待元素可点击，最长等待 10 秒
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'i.fa.fa-plus-circle'))
    )
    js_click_and_wait(driver, element)

    current_date = datetime.now().strftime("%Y-%m-%d")
    xpath_expression = f'//input[@type="text" and @value="{current_date}"]'
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, xpath_expression))
    )
    logging.info("新建文章操作完成")


# 设置文章标题
def set_jianshu_title(driver, title):
    current_date = datetime.now().strftime("%Y-%m-%d")
    xpath_expression = f'//input[@type="text" and @value="{current_date}"]'
    title_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, xpath_expression))
    )

    title_input.clear()
    title_input.send_keys(title)
    logging.info(f"已设置文章标题为: {title}")


# 设置文章内容
def set_jianshu_content(driver, content):
    content_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "arthur-editor"))
    )
    content_input.clear()
    # 先点击输入框，使其获得焦点
    content_input.send_keys(content)
    logging.info("已设置文章内容")


# 发布文章函数
def publish_jianshu_post(driver, title, content):
    # 打开简书创作页面
    driver.get('https://www.jianshu.com/writer#/')
    time.sleep(1)

    new_post(driver)
    time.sleep(1)
    set_jianshu_title(driver, title)
    time.sleep(1)
    set_jianshu_content(driver, content)
    time.sleep(1)

    # 点击发布按钮
    publish_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//a[@data-action="publicize"]'))
    )
    js_click_and_wait(driver, publish_btn)
    time.sleep(3)

    # 判断发布成功
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//a[contains(text(), "发布成功")]'))
    )
    logging.info("内容发布成功！")


def read_article_from_file():
    current_date = datetime.now().strftime("%m%d")
    # 提取月份部分
    month = current_date[:2].lstrip('0') if current_date.lstrip('0') else '0'
    # 拼成包含“月”的字符串
    month_str = f"{month}月\\"

    file_name = f"{current_date}.txt"
    file_path1 = "C:\\Users\\jayden\\Desktop\\创作空间\\"
    file_path = os.path.join(file_path1, month_str, file_name)

    # 打开并读取文件
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 初始化标题和内容变量
    article_title = ""
    article_content = ""

    # 标记是否开始读取内容
    is_content = False

    # 遍历文件的每一行
    for line in lines:
        line = line.strip()
        if line == "[标题]":
            continue
        elif line == "[内容]":
            is_content = True
            continue
        if is_content:
            article_content += line + "\n"
        else:
            article_title = line

    # 去除内容末尾多余的换行符
    article_content = article_content.rstrip()
    logging.info(f"从文件 {file_path} 中读取文章标题和内容成功")

    return article_title, article_content


def main():
    # 设置 Chrome 浏览器选项
    chrome_options = Options()
    # 可以根据需要设置为无头模式，即不显示浏览器窗口
    # chrome_options.add_argument('--headless')

    # 配置 ChromeDriver 路径
    service = Service("../chromedriver-win64/chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 检查是否存在 cookie 文件
    if cookie_file_exists():
        if not cookies_login(driver):
            manual_login(driver)
    else:
        logging.info("没有有效的保存的 Cookies，进行手动登录。")
        manual_login(driver)

    time.sleep(5)

    # 读取文章
    article_title, article_content = read_article_from_file()

    publish_jianshu_post(driver, article_title, article_content)

    # 关闭浏览器
    driver.quit()
    logging.info("浏览器已关闭")


if __name__ == "__main__":
    main()
