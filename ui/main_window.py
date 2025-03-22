import os
import time
import customtkinter as ctk
from tools.json_handle import extract_problems
from utils.stdout_redirector import redirect_to_widget, restore_stdout
from proxy.proxy_manager import ProxyManager

class YuketangApp(ctk.CTk):
    """雨课堂试卷提取工具主窗口"""
    
    def __init__(self):
        super().__init__()
        
        # 配置窗口
        self.title("雨课堂试卷提取工具")
        self.geometry("650x750")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # 保存原始stdout
        self.old_stdout = None
        
        # 创建UI组件
        self._create_widgets()
        
    def _create_widgets(self):
        """创建UI组件"""
        # 创建主框架
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # 标题
        self.title_label = ctk.CTkLabel(self.main_frame, 
                                     text="雨课堂试卷提取工具", 
                                     font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # 第一步：设置试卷ID
        self._create_step1_widgets()
        
        # 第二步：启动代理
        self._create_step2_widgets()
        
        # 第三步：处理JSON
        self._create_step3_widgets()
        
        # 状态显示区域
        self.status_label = ctk.CTkLabel(self.main_frame, 
                                      text="准备就绪", 
                                      font=ctk.CTkFont(size=14))
        self.status_label.grid(row=9, column=0, padx=20, pady=(20, 0))
        
        # 输出控制台
        self.console = ctk.CTkTextbox(self.main_frame, height=100)
        self.console.grid(row=10, column=0, padx=20, pady=10, sticky="ew")
    
    def _create_step1_widgets(self):
        """创建步骤1相关的UI组件"""
        self.step1_label = ctk.CTkLabel(self.main_frame, 
                                     text="步骤1: 输入雨课堂试卷ID", 
                                     font=ctk.CTkFont(size=16))
        self.step1_label.grid(row=1, column=0, padx=20, pady=(20, 5), sticky="w")
        
        self.id_frame = ctk.CTkFrame(self.main_frame)
        self.id_frame.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        self.id_frame.grid_columnconfigure(0, weight=1)
        
        self.id_entry = ctk.CTkEntry(self.id_frame, placeholder_text="输入试卷ID")
        self.id_entry.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="ew")
    
    def _create_step2_widgets(self):
        """创建步骤2相关的UI组件"""
        self.step2_label = ctk.CTkLabel(self.main_frame, 
                                     text="步骤2: 启动代理并访问试卷", 
                                     font=ctk.CTkFont(size=16))
        self.step2_label.grid(row=3, column=0, padx=20, pady=(20, 5), sticky="w")
        
        # 创建一个包含启动和终止按钮的框架
        self.proxy_buttons_frame = ctk.CTkFrame(self.main_frame)
        self.proxy_buttons_frame.grid(row=4, column=0, padx=20, pady=5, sticky="ew")
        self.proxy_buttons_frame.grid_columnconfigure(0, weight=1)
        self.proxy_buttons_frame.grid_columnconfigure(1, weight=1)
        
        # 添加启动代理按钮
        self.start_proxy_button = ctk.CTkButton(self.proxy_buttons_frame, 
                                             text="启动代理", 
                                             command=self.start_proxy)
        self.start_proxy_button.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="ew")
        
        # 添加终止代理按钮
        self.stop_proxy_button = ctk.CTkButton(self.proxy_buttons_frame, 
                                            text="终止代理", 
                                            command=self.stop_proxy,
                                            fg_color="#D35B58",  # 设置红色背景
                                            hover_color="#C64F45")  # 设置鼠标悬停颜色
        self.stop_proxy_button.grid(row=0, column=1, padx=(5, 0), pady=5, sticky="ew")
        
        # 提示消息
        self.proxy_hint = ctk.CTkLabel(self.main_frame, 
                                    text="启动代理后，请在浏览器中访问雨课堂试卷。\n成功捕获后，代理会自动保存JSON数据。", 
                                    font=ctk.CTkFont(size=12),
                                    text_color="gray60")
        self.proxy_hint.grid(row=5, column=0, padx=20, pady=5)
    
    def _create_step3_widgets(self):
        """创建步骤3相关的UI组件"""
        self.step3_label = ctk.CTkLabel(self.main_frame, 
                                     text="步骤3: 提取试卷内容", 
                                     font=ctk.CTkFont(size=16))
        self.step3_label.grid(row=6, column=0, padx=20, pady=(20, 5), sticky="w")
        
        # 选项处理选择
        self.reorder_var = ctk.StringVar(value="y")
        self.reorder_frame = ctk.CTkFrame(self.main_frame)
        self.reorder_frame.grid(row=7, column=0, padx=20, pady=5, sticky="ew")
        
        self.reorder_label = ctk.CTkLabel(self.reorder_frame, text="是否重新排序选项(ABCD顺序):")
        self.reorder_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.reorder_yes = ctk.CTkRadioButton(self.reorder_frame, text="是", variable=self.reorder_var, value="y")
        self.reorder_yes.grid(row=0, column=1, padx=10, pady=10)
        
        self.reorder_no = ctk.CTkRadioButton(self.reorder_frame, text="否", variable=self.reorder_var, value="n")
        self.reorder_no.grid(row=0, column=2, padx=10, pady=10)
        
        self.process_button = ctk.CTkButton(self.main_frame, 
                                         text="提取试卷内容", 
                                         command=self.process_json)
        self.process_button.grid(row=8, column=0, padx=20, pady=5)
    
    def start_proxy(self):
        """启动mitmproxy代理"""
        exam_id = self.id_entry.get().strip()
        if not exam_id:
            self.update_status("请输入有效的试卷ID", "red")
            return
            
        self.update_status("正在启动代理...", "orange")
        
        # 重定向输出前先确保控制台可见
        self.console.configure(state="normal")
        self.console.delete("0.0", "end")
        self.console.insert("end", f"==== 启动代理会话 [{time.strftime('%H:%M:%S')}] ====\n")
        self.console.insert("end", f"试卷ID: {exam_id}\n")
        self.console.insert("end", "正在启动代理...\n")
        self.console.configure(state="disabled")
        
        # 重定向输出
        self.old_stdout = redirect_to_widget(self.console)
        
        # 启动代理
        ProxyManager.start_proxy(exam_id, self.update_status)
        
        # 添加一些反馈，确认代理已启动
        self.console.configure(state="normal")
        self.console.insert("end", "\n代理已启动，正在等待连接...\n")
        self.console.insert("end", "请在浏览器中配置代理：127.0.0.1:11000\n")
        self.console.insert("end", "然后访问雨课堂试卷页面...\n")
        self.console.configure(state="disabled")

    def stop_proxy(self):
        """终止mitmproxy代理"""
        self.update_status("正在终止代理...", "orange")
        
        # 如果控制台为空，先添加一些信息
        self.console.configure(state="normal")
        if not self.console.get("1.0", "end").strip():
            self.console.insert("end", f"==== 终止代理会话 [{time.strftime('%H:%M:%S')}] ====\n")
            self.console.insert("end", "正在终止代理进程...\n")
        else:
            self.console.insert("end", "\n==== 终止代理会话 ====\n")
        self.console.configure(state="disabled")
        
        # 确保输出重定向到控制台
        if not self.old_stdout:
            self.old_stdout = redirect_to_widget(self.console)
        
        # 终止代理
        if ProxyManager.stop_proxy(self.update_status):
            self.console.configure(state="normal")
            self.console.insert("end", "代理已成功终止\n")
            self.console.configure(state="disabled")
        else:
            self.console.configure(state="normal")
            self.console.insert("end", "没有找到正在运行的代理进程\n")
            self.console.configure(state="disabled")
    
    def process_json(self):
        """处理JSON数据并提取试卷内容"""
        self.update_status("正在处理JSON数据...", "orange")
        
        # 重定向输出
        redirect_info = redirect_to_widget(self.console)
        
        # 清空控制台
        self.console.configure(state="normal")
        self.console.delete("0.0", "end")
        self.console.configure(state="disabled")
        
        try:
            json_file = "雨课堂文档/exam_data.json"
            if not os.path.exists(json_file):
                self.update_status(f"找不到文件: {json_file}", "red")
                return
                
            reorder_options = (self.reorder_var.get() == "y")
            extract_problems(json_file, reorder_options)
            self.update_status("处理完成!", "green")
            
        except Exception as e:
            self.update_status(f"处理JSON时出错: {e}", "red")
        finally:
            if redirect_info:
                restore_stdout(redirect_info)
    
    def update_status(self, message, color="black"):
        """更新状态标签"""
        self.status_label.configure(text=message, text_color=color)