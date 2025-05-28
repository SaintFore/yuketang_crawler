import customtkinter as ctk
from utils.stdout_redirector import redirect_to_widget, restore_stdout
import time


class ConsoleOutput(ctk.CTkFrame):
    """可复用的控制台输出组件"""
    
    def __init__(self, parent, height=150, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # 标题
        self.title_label = ctk.CTkLabel(
            self, 
            text="操作日志", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=10, pady=(5, 0), sticky="w")
        
        # 控制台文本框
        self.console = ctk.CTkTextbox(self, height=height)
        self.console.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        
        # 重定向信息
        self.redirect_info = None
        
    def clear(self):
        """清空控制台"""
        self.console.configure(state="normal")
        self.console.delete("0.0", "end")
        self.console.configure(state="normal")
        
    def log(self, message, timestamp=True):
        """添加日志信息"""
        self.console.configure(state="normal")
        if timestamp:
            time_str = time.strftime('%H:%M:%S')
            self.console.insert("end", f"[{time_str}] {message}\n")
        else:
            self.console.insert("end", f"{message}\n")
        self.console.see("end")
        self.console.configure(state="normal")
        
    def start_redirect(self):
        """开始重定向标准输出"""
        self.redirect_info = redirect_to_widget(self.console)
        
    def stop_redirect(self):
        """停止重定向标准输出"""
        if self.redirect_info:
            restore_stdout(self.redirect_info)
            self.redirect_info = None
