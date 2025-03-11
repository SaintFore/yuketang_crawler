import os
import subprocess
import threading
import time
import sys

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
                # 直接向控制台输出信息
                sys.stdout.write(f"[开始] 正在启动代理，试卷ID: {exam_id}...\n")
                sys.stdout.flush()
                
                # 检查mitmdump是否存在
                import shutil
                mitmdump_path = shutil.which("mitmdump")
                sys.stdout.write(f"[检查] mitmdump路径: {mitmdump_path or '未找到'}\n")
                sys.stdout.flush()
                
                if not mitmdump_path:
                    error_msg = "找不到mitmdump程序，请确保已安装mitmproxy"
                    sys.stdout.write(f"[错误] {error_msg}\n")
                    sys.stdout.flush()
                    if status_callback:
                        status_callback(error_msg, "red")
                    return
                
                # 创建环境变量字典
                env = os.environ.copy()
                env["EXAM_ID"] = exam_id
                sys.stdout.write(f"[配置] 已设置环境变量 EXAM_ID={exam_id}\n")
                sys.stdout.flush()
                
                # 获取脚本的绝对路径
                script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "yuketang_proxy.py"))
                sys.stdout.write(f"[配置] 脚本绝对路径: {script_path}\n")
                sys.stdout.write(f"[配置] 脚本是否存在: {os.path.exists(script_path)}\n")
                sys.stdout.flush()
                
                # 创建日志文件目录
                log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir)
                log_file = os.path.join(log_dir, "proxy.log")
                
                sys.stdout.write(f"[启动] 正在启动mitmdump，日志将保存到: {log_file}\n")
                sys.stdout.flush()
                
                # 启动代理进程
                cmd = [mitmdump_path, "-s", script_path, "-p", "11000"]
                sys.stdout.write(f"[执行] 命令: {' '.join(cmd)}\n")
                sys.stdout.flush()
                
                # 同时输出到日志文件
                with open(log_file, "w", encoding="utf-8") as f:
                    f.write(f"启动命令: {' '.join(cmd)}\n")
                    f.write(f"环境变量: EXAM_ID={exam_id}\n")
                    f.write("-" * 50 + "\n")
                    
                    process = subprocess.Popen(
                        cmd,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                        env=env
                    )
                    
                    sys.stdout.write("[状态] mitmdump进程已启动\n")
                    sys.stdout.flush()
                    f.write("[状态] mitmdump进程已启动\n")
                    
                    # 读取并显示输出
                    for line in process.stdout:
                        line_text = line.strip()
                        # 同时写入到日志文件
                        f.write(f"{line_text}\n")
                        f.flush()
                        
                        sys.stdout.write(f"[mitmdump] {line_text}\n")
                        sys.stdout.flush()
                        
                        if "已保存至" in line_text and status_callback:
                            status_callback("JSON数据已保存，可以提取试卷内容", "green")
                    
                    process.wait()
                    sys.stdout.write("[结束] mitmdump进程已退出\n")
                    sys.stdout.flush()
                    f.write("[结束] mitmdump进程已退出\n")
                
            except Exception as e:
                error_msg = f"启动代理时出错: {str(e)}"
                sys.stdout.write(f"[异常] {error_msg}\n")
                sys.stdout.flush()
                
                # 写入错误日志
                log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir)
                with open(os.path.join(log_dir, "error.log"), "a", encoding="utf-8") as f:
                    f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {error_msg}\n")
                
                if status_callback:
                    status_callback(error_msg, "red")
        
        # 在新线程中启动代理，避免阻塞GUI
        thread = threading.Thread(target=run_proxy, daemon=True)
        thread.start()
        
        return thread