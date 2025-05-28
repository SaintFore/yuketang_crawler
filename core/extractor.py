"""试卷提取核心业务逻辑"""
import os
import time
from tools.json_handle import extract_problems
from tools.json_save import extract_answers
from proxy.proxy_manager import ProxyManager


class ExamExtractor:
    """试卷提取业务逻辑类"""
    
    def __init__(self, status_callback=None):
        self.status_callback = status_callback
        self.old_stdout = None
        
    def update_status(self, message, color="black"):
        """更新状态"""
        if self.status_callback:
            self.status_callback(message, color)
            
    def start_proxy(self, exam_id, console_widget):
        """启动代理"""
        if not exam_id.strip():
            self.update_status("请输入有效的试卷ID", "red")
            return False
            
        self.update_status("正在启动代理...", "orange")
        
        # 清空控制台并添加初始信息
        console_widget.clear()
        console_widget.log(f"启动代理会话，试卷ID: {exam_id}", False)
        console_widget.log("正在启动代理...", False)
        
        # 开始重定向输出
        console_widget.start_redirect()
        
        # 启动代理
        ProxyManager.start_proxy(exam_id, self.update_status)
        
        # 添加提示信息
        console_widget.log("代理已启动，正在等待连接...", False)
        console_widget.log("请在浏览器中配置代理：127.0.0.1:11000", False)
        console_widget.log("然后访问雨课堂试卷页面...", False)
        
        return True
        
    def stop_proxy(self, console_widget):
        """停止代理"""
        self.update_status("正在终止代理...", "orange")
        
        console_widget.log("正在终止代理进程...", False)
        
        # 确保输出重定向
        if not console_widget.redirect_info:
            console_widget.start_redirect()
            
        # 终止代理
        if ProxyManager.stop_proxy(self.update_status):
            console_widget.log("代理已成功终止", False)
        else:
            console_widget.log("没有找到正在运行的代理进程", False)
            
    def process_json(self, reorder_options, console_widget):
        """处理JSON数据"""
        self.update_status("正在处理JSON数据...", "orange")
        
        # 清空控制台
        console_widget.clear()
        console_widget.start_redirect()
        
        try:
            json_file = "雨课堂文档/exam_data.json"
            if not os.path.exists(json_file):
                self.update_status(f"找不到文件: {json_file}", "red")
                return False
                
            extract_problems(json_file, reorder_options)
            self.update_status("处理完成!", "green")
            return True
            
        except Exception as e:
            self.update_status(f"处理JSON时出错: {e}", "red")
            return False
        finally:
            console_widget.stop_redirect()
            
    def save_answers_to_csv(self, exam_id, console_widget):
        """保存答案到CSV"""
        self.update_status("正在提取答案数据...", "orange")
        
        # 清空控制台
        console_widget.clear()
        console_widget.log("提取答案数据", False)
        console_widget.start_redirect()
        
        try:
            json_file = os.path.abspath("雨课堂文档/exam_data.json")
            
            if not os.path.exists(json_file):
                self.update_status(f"找不到文件: {json_file}", "red")
                console_widget.log(f"错误: 找不到文件 {json_file}", False)
                return False
                
            output_dir = "雨课堂答案"
            output_file = extract_answers(json_file, output_dir)
            
            if output_file:
                self.update_status(f"答案已保存到: {output_file}", "green")
                return True
            else:
                self.update_status("未能提取答案数据", "red")
                return False
                
        except Exception as e:
            self.update_status(f"处理数据时出错: {e}", "red")
            console_widget.log(f"错误详情: {e}", False)
            return False
        finally:
            console_widget.stop_redirect()
