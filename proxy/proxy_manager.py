import os
import subprocess
import threading
import time
import sys
import socket
import platform
from winproxy import ProxySetting

class ProxyManager:
    """管理mitmproxy代理进程"""
    
    # 添加类变量来存储当前运行的进程
    current_process = None
    default_port = 11000
    
    @staticmethod
    def proxy_open():
        """启用系统代理"""
        proxy = ProxySetting()
        proxy.enable = True
        proxy.server = "127.0.0.1:" + str(ProxyManager.default_port)
        proxy.override = ["localhost;", "127.*;", "192.168.*;", "10.*;", "172.*;"]
        proxy.registry_write()

    @staticmethod
    def proxy_off():
        """禁用系统代理"""
        proxy = ProxySetting()
        proxy.enable = False
        proxy.registry_write()
    
    @staticmethod
    def is_port_in_use(port):
        """检查端口是否被占用"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(('127.0.0.1', port)) == 0
        except:
            return False
    
    @staticmethod
    def kill_process_by_port(port):
        """终止占用指定端口的进程"""
        try:
            # Windows系统
            cmd = f"netstat -ano | findstr :{port}"
            result = subprocess.check_output(cmd, shell=True).decode("gbk", errors="ignore")
            
            if result:
                lines = result.strip().split('\n')
                pids = set()
                for line in lines:
                    if f":{port}" in line and "LISTENING" in line:
                        parts = line.strip().split()
                        if len(parts) >= 5:
                            pid = parts[-1]
                            pids.add(pid)
                
                for pid in pids:
                    sys.stdout.write(f"[端口] 正在终止占用端口 {port} 的进程 (PID: {pid})\n")
                    sys.stdout.flush()
                    try:
                        subprocess.run(f"taskkill /F /PID {pid}", shell=True)
                        sys.stdout.write(f"[端口] 已终止 PID: {pid}\n")
                    except:
                        sys.stdout.write(f"[端口] 终止 PID: {pid} 失败\n")
                
                return len(pids) > 0
            
            return False
        except Exception as e:
            sys.stdout.write(f"[错误] 终止占用端口进程时出错: {str(e)}\n")
            sys.stdout.flush()
            return False
    
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
                ProxyManager.proxy_open()
                sys.stdout.write("[代理] 系统代理已启用\n")
                # 检查端口是否被占用
                port = ProxyManager.default_port
                if ProxyManager.is_port_in_use(port):
                    sys.stdout.write(f"[警告] 端口 {port} 已被占用，尝试终止占用进程...\n")
                    sys.stdout.flush()
                    
                    if status_callback:
                        status_callback(f"端口 {port} 被占用，正在尝试终止...", "orange")
                    
                    # 尝试终止占用进程
                    if ProxyManager.kill_process_by_port(port):
                        sys.stdout.write(f"[端口] 已尝试终止占用端口 {port} 的进程\n")
                        # 等待端口释放
                        time.sleep(1)
                    
                    # 再次检查端口是否被释放
                    if ProxyManager.is_port_in_use(port):
                        sys.stdout.write(f"[错误] 端口 {port} 仍然被占用，无法启动代理\n")
                        sys.stdout.flush()
                        if status_callback:
                            status_callback(f"端口 {port} 仍然被占用，请手动关闭占用进程", "red")
                        return
                
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
                cmd = [mitmdump_path, "-s", script_path, "-p", str(port)]
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
                    
                    # 保存进程引用到类变量
                    ProxyManager.current_process = process
                    
                    sys.stdout.write("[状态] mitmdump进程已启动\n")
                    sys.stdout.flush()
                    f.write("[状态] mitmdump进程已启动\n")
                    
                    # 读取并显示输出
                    for line in process.stdout:
                        # 如果进程已被终止，退出循环
                        if ProxyManager.current_process is None:
                            break
                        
                        line_text = line.strip()
                        # 同时写入到日志文件
                        f.write(f"{line_text}\n")
                        f.flush()
                        
                        sys.stdout.write(f"[mitmdump] {line_text}\n")
                        sys.stdout.flush()
                        
                        if "已保存至" in line_text and status_callback:
                            status_callback("JSON数据已保存，可以提取试卷内容", "green")
                    
                    if process.poll() is None:
                        process.terminate()
                    
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
    
    @staticmethod
    def stop_proxy(status_callback=None):
        """
        停止当前运行的代理进程
        
        参数:
            status_callback (function): 状态更新回调函数
        """
        try:
            ProxyManager.proxy_off()
            sys.stdout.write("[代理] 系统代理已禁用\n")
            if ProxyManager.current_process:
                sys.stdout.write("[终止] 正在终止代理进程...\n")
                sys.stdout.flush()
                
                # 尝试优雅地终止进程
                try:
                    ProxyManager.current_process.terminate()
                    time.sleep(0.5)
                except:
                    pass
                
                # 如果进程仍在运行，强制终止
                if ProxyManager.current_process.poll() is None:
                    if platform.system() == "Windows":
                        subprocess.run(["taskkill", "/F", "/T", "/PID", str(ProxyManager.current_process.pid)], 
                                       shell=True, stderr=subprocess.DEVNULL)
                    else:
                        ProxyManager.current_process.kill()
                
                # 清空当前进程引用
                ProxyManager.current_process = None
                
                sys.stdout.write("[终止] 代理进程已终止\n")
                sys.stdout.flush()
                
                if status_callback:
                    status_callback("代理已终止", "orange")
                return True
            else:
                sys.stdout.write("[终止] 没有正在运行的代理进程\n")
                sys.stdout.flush()
                
                if status_callback:
                    status_callback("没有正在运行的代理进程", "orange")
                return False
                
        except Exception as e:
            error_msg = f"终止代理时出错: {str(e)}"
            sys.stdout.write(f"[异常] {error_msg}\n")
            sys.stdout.flush()
            
            if status_callback:
                status_callback(error_msg, "red")
            return False