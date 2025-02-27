import configparser
import json
import os
import time
from datetime import datetime
import logging
from util.log_util import setup_logger

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# 初始化日志配置
setup_logger('掘金自动化', 'juejin_automation.log')

# 判断是否登录成功
def is_login_successful(driver):
    try:
        # 显式等待用户头像元素出现，判断登录成功
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//img[@class="lazy avatar-img immediate"]'))
        )
        return True
    except Exception:
        logging.warning("未检测到用户头像，登录可能失败")
        return False


def loop_until_y_case_sensitive():
    while True:
        user_input = input("请输入字符（输入 'y' 退出循环）: ")
        if user_input == 'y':
            logging.info("你输入了 'y'，循环结束。")
            break


def click_and_wait(element, wait_time=1):
    element.click()
    time.sleep(wait_time)


def save_cookies(driver, file_path='juejin_cookies.json'):
    # 保存登录后的 Cookies，以覆盖模式写入文件（即先清空原内容再写入）
    cookies = driver.get_cookies()
    with open(file_path, 'w') as f:
        json.dump(cookies, f)
    logging.info(f"已将Cookies保存到 {file_path}")


def delete_cookies_file(file_path='juejin_cookies.json'):
    if os.path.exists(file_path):
        # 获取文件的目录和文件名
        dir_name, file_name = os.path.split(file_path)
        # 生成新的文件名，添加 _bak 后缀
        new_file_name = os.path.splitext(file_name)[0] + '_bak' + os.path.splitext(file_name)[1]
        # 生成新的文件路径
        new_file_path = os.path.join(dir_name, new_file_path)
        # 重命名文件
        os.rename(file_path, new_file_path)
        logging.info(f"文件 {file_path} 已重命名为 {new_file_path}")


# 手动登录函数
def manual_login(driver):
    # 读取配置文件
    config = configparser.ConfigParser()
    config.read('config.ini')
    username_str = config.get('Credentials', 'username')
    password_str = config.get('Credentials', 'password')

    driver.get('https://juejin.cn/')
    time.sleep(3)

    # 显式等待按钮可点击，最多等待 10 秒
    button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.login-button'))
    )
    click_and_wait(button)

    password_login_span = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//span[@class="clickable" and contains(text(), "密码登录")]'))
    )
    click_and_wait(password_login_span)

    # 等待账号和密码输入框出现
    username_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input.account-input'))
    )
    password_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input.login-password'))
    )

    # 输入账号和密码
    username_input.send_keys(username_str)
    password_input.send_keys(password_str)

    # 显式等待登录按钮可点击
    login_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.btn.btn-login'))
    )
    click_and_wait(login_btn)

    # 登录卡点，等待输入 y 继续
    loop_until_y_case_sensitive()

    if is_login_successful(driver):
        save_cookies(driver)
        logging.info("手动登录成功，已保存Cookies")
        return True
    logging.error("手动登录失败，请检查账号密码或网络。")
    return False


# 使用 Cookies 登录函数
def cookies_login(driver):
    try:
        with open('juejin_cookies.json', 'r') as f:
            cookies = json.load(f)
            driver.get('https://juejin.cn/')
            time.sleep(3)
            # 添加 cookie
            for cookie in cookies:
                driver.add_cookie(cookie)
            driver.refresh()
            time.sleep(3)

            if is_login_successful(driver):
                logging.info("使用Cookies登录成功！")
                return True
            else:
                logging.warning("Cookies已过期或无效，将进行手动登录。")
                return False
    except Exception as e:
        delete_cookies_file()
        logging.error(f"登录时出现异常: {e}，已删除 juejin_cookies.json 文件。")
        return False


# 检查是否存在 cookie 文件且文件有内容
def cookie_file_exists():
    file_path = 'juejin_cookies.json'
    result = os.path.exists(file_path) and os.path.getsize(file_path) > 0
    return result


def set_article_title(driver, title):
    # 显式等待标题输入框出现
    title_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[contains(@placeholder, "文章标题")]'))
    )
    title_input.send_keys(title)


def set_article_content(driver, content):
    # 显式等待内容输入框出现
    content_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div.bytemd-editor'))
    )

    # 执行 JavaScript 代码来设置编辑器的内容
    driver.execute_script("""
        var editor = arguments[0];
        var cm = editor.querySelector('.CodeMirror').CodeMirror;
        cm.setValue(arguments[1]);
    """, content_input, content)


def select_tags(driver):
    # 显式等待标签输入框出现
    button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//button[@class="xitu-btn" and contains(text(), "发布")]'))
    )
    # 点击按钮
    click_and_wait(button)

    # 显式等待标签输入框出现
    tag1 = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//div[@class="item" and contains(text(), "阅读")]'))
    )
    # 点击按钮
    click_and_wait(tag1)

    # 显式等待下拉框出现并可点击，最长等待 10 秒
    dropdown = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.select-plus.byte-select.byte-select--normal'))
    )
    # 点击下拉框展开选项列表
    click_and_wait(dropdown)

    tag2 = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//li[@classname="tag-option" and contains(text(), "面试")]'))
    )
    # 点击 “后端标签” 选项
    click_and_wait(tag2)

def upload_cover_image(driver):
    current_date = datetime.now().strftime("%m%d")
    file_name = f"{current_date}.jpg"
    file_path = os.path.join("C:\\Users\\jayden\\Desktop\\创作空间\\cover_picture", file_name)

    # 检查文件是否存在
    if os.path.exists(file_path):
        # 显式等待文件输入框出现
        file_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"][style="display: none;"]'))
        )
        # 上传图片
        file_input.send_keys(file_path)
        # 显式等待图片上传完成，这里需要根据实际情况调整等待条件
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'img.preview-image'))
        )
        logging.info(f"成功上传图片: {file_path}")
    else:
        logging.error(f"文件 {file_path} 不存在，请检查路径。")
        raise FileNotFoundError(f"文件 {file_path} 不存在，请检查路径。")


# 发布文章函数
def publish_article(driver, title, content):
    # 打开创作中心
    creator_center_url = 'https://juejin.cn/editor/drafts/new?v=2'
    driver.get(creator_center_url)

    set_article_title(driver, title)
    time.sleep(1)
    set_article_content(driver, content)
    time.sleep(1)
    select_tags(driver)
    time.sleep(1)
    upload_cover_image(driver)
    time.sleep(1)

    # 显式等待发布按钮可点击
    publish_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "确定并发布")]'))
    )
    click_and_wait(publish_btn)
    time.sleep(2)

    # 等待发布成功
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[@class="thanks" and contains(text(), "发布成功")]'))
    )
    logging.info("文章发布成功！")


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
        line = line.strip()  # 去除行首尾的空白字符
        if line == "[标题]":
            continue  # 跳过标题标记行
        elif line == "[内容]":
            is_content = True  # 开始读取内容
            continue  # 跳过内容标记行
        if is_content:
            article_content += line + "\n"  # 拼接内容行
        else:
            article_title = line  # 记录标题

    # 去除内容末尾多余的换行符
    article_content = article_content.rstrip()

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

    time.sleep(3)

    # 读取文章
    article_title, article_content = read_article_from_file()

    publish_article(driver, article_title, article_content)

    # 关闭浏览器
    driver.quit()
    logging.info("关闭Chrome浏览器")


if __name__ == "__main__":
    main()