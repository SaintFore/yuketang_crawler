import os
import subprocess
import threading

class ProxyManager:
    """管理mitmproxy代理进程"""
    
    @staticmethod
    def start_proxy(exam_id, status_callback=None):
        """
        启动mitmproxy代理
        
        参数:
            exam_id (str): 雨课堂试卷ID
            status_callback (function): 状态更新回调函数
        """
        def run_proxy():
            try:
                # 创建环境变量字典
                env = os.environ.copy()
                env["EXAM_ID"] = exam_id
                
                # 启动代理进程
                script_path = os.path.join(os.path.dirname(__file__), "yuketang_proxy.py") # 设置代理脚本路径
                process = subprocess.Popen(
                    ["mitmdump", "-s", script_path],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    env=env
                )
                
                # 将试卷ID发送到进程的标准输入
                process.stdin.write(exam_id + "\n")
                process.stdin.flush()
                
                # 读取并显示输出
                for line in process.stdout:
                    print(line.strip())
                    if "已保存至" in line and status_callback:
                        status_callback("JSON数据已保存，可以提取试卷内容", "green")
                
                process.wait()
                
            except Exception as e:
                if status_callback:
                    status_callback(f"启动代理时出错: {e}", "red")
        
        # 在新线程中启动代理，避免阻塞GUI
        thread = threading.Thread(target=run_proxy, daemon=True)
        thread.start()
        
        return thread