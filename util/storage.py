import os
import json
import configparser
import logging
from datetime import datetime

class StorageUtil:
    @staticmethod
    def safe_cookie_operation(file_path):
        """安全处理cookie文件操作"""
        try:
            if os.path.exists(file_path):
                dir_name, file_name = os.path.split(file_path)
                base, ext = os.path.splitext(file_name)
                new_name = f"{base}_bak{ext}"
                os.rename(file_path, os.path.join(dir_name, new_name))
                logging.info(f"已备份旧cookie文件: {file_path}")
        except Exception as e:
            logging.error(f"cookie文件操作失败: {str(e)}")

    @staticmethod
    def read_config(section='Credentials'):
        """统一读取配置文件"""
        config = configparser.ConfigParser()
        config.read('config.ini')
        return {
            'username': config.get(section, 'username'),
            'password': config.get(section, 'password')
        }

    @staticmethod
    def parse_article_content(file_path):
        """通用文章内容解析方法"""
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        article_title = ""
        article_content = ""
        is_content = False

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

        return article_title.rstrip(), article_content.rstrip()

    @staticmethod
    def generate_file_path(base_dir):
        """生成带日期结构的文件路径"""
        current_date = datetime.now().strftime("%m%d")
        month = current_date[:2].lstrip('0') or '0'
        return os.path.join(base_dir, f"{month}月", f"{current_date}.txt")