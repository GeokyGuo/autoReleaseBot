import logging
from typing import Optional

def setup_logger(platform_name: str, log_file: str, log_level: int = logging.INFO):
    """
    统一日志配置函数
    :param platform_name: 平台名称（用于日志格式）
    :param log_file: 日志文件名
    :param log_level: 日志级别，默认为INFO
    """
    formatter = logging.Formatter(
        f'{platform_name} - %(asctime)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger(platform_name)
    logger.setLevel(log_level)

    # 防止重复添加handler
    if not logger.handlers:
        # 文件处理器（带UTF-8编码）
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)

        # 控制台处理器
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger