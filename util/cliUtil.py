import os
import subprocess
import threading


class PythonScriptRunner:
    def __init__(self, folders):
        self.folders = folders
        self.threads = []

    def run_script(self, file_path):
        try:
            # 获取脚本所在目录
            script_dir = os.path.dirname(file_path)
            print(f"正在运行脚本: {file_path}")
            # 使用subprocess模块运行Python脚本，并设置工作目录为脚本所在目录
            subprocess.run(['python', file_path], check=True, cwd=script_dir)
            print(f"脚本 {file_path} 运行完成")
        except subprocess.CalledProcessError as e:
            print(f"运行脚本 {file_path} 时出现错误: {e}")
        except Exception as e:
            print(f"执行脚本 {file_path} 时发生未知错误: {e}")

    def multi_thread_run_scripts(self):
        for folder in self.folders:
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        # 创建线程并启动
                        thread = threading.Thread(target=self.run_script, args=(file_path,))
                        self.threads.append(thread)
                        thread.start()

        # 等待所有线程执行完毕
        for thread in self.threads:
            thread.join()
        print(f"所有脚本运行完毕")


if __name__ == "__main__":
    folders = []
    folders.append("../bokeyuan")
    folders.append("../csdn")
    folders.append("../icity")
    folders.append("../jianshu")
    folders.append("../juejin")
    runner = PythonScriptRunner(folders)
    runner.multi_thread_run_scripts()
