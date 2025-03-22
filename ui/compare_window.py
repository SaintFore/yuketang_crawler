import os
import time
import customtkinter as ctk
from utils.stdout_redirector import redirect_to_widget, restore_stdout
from compare.result_crawler import fetch_json_data, extract_data, save_to_csv

class CompareApp(ctk.CTk):
    """雨课堂试卷对比工具主窗口"""
    
    def __init__(self):
        super().__init__()
        
        # 配置窗口
        self.title("雨课堂试卷对比工具")
        self.geometry("750x850")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # 创建答案保存目录
        self.answers_dir = os.path.join(os.getcwd(), "雨课堂答案")
        if not os.path.exists(self.answers_dir):
            os.makedirs(self.answers_dir)
        
        # 创建UI组件
        self._create_widgets()
        
    def _create_widgets(self):
        """创建UI组件"""
        # 创建主框架
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(5, weight=1)  # 让包含控制台的行可以扩展
        
        # 标题
        self.title_label = ctk.CTkLabel(self.main_frame, 
                                     text="雨课堂试卷答案获取工具", 
                                     font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # 说明文本
        self.desc_label = ctk.CTkLabel(self.main_frame,
                                     text="本工具用于获取雨课堂试卷答案，将自动保存到'雨课堂答案'文件夹",
                                     font=ctk.CTkFont(size=14))
        self.desc_label.grid(row=1, column=0, padx=20, pady=(0, 20))
        
        # 输入框区域
        self._create_input_widgets()
        
        # 操作按钮区域
        self._create_action_widgets()
        
        # 状态显示区域
        status_frame = ctk.CTkFrame(self.main_frame)
        status_frame.grid(row=4, column=0, padx=20, pady=(15, 5), sticky="ew")
        status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(status_frame, 
                                      text="准备就绪", 
                                      font=ctk.CTkFont(size=14))
        self.status_label.grid(row=0, column=0, padx=10, pady=5)
        
        # 目录信息
        self.dir_label = ctk.CTkLabel(status_frame,
                                   text=f"答案将保存到: {self.answers_dir}",
                                   font=ctk.CTkFont(size=12),
                                   text_color="gray")
        self.dir_label.grid(row=1, column=0, padx=10, pady=5)
        
        # 输出控制台
        console_frame = ctk.CTkFrame(self.main_frame)
        console_frame.grid(row=5, column=0, padx=20, pady=10, sticky="nsew")
        console_frame.grid_columnconfigure(0, weight=1)
        console_frame.grid_rowconfigure(1, weight=1)  # 添加这一行，让文本框可以扩展
        
        console_title = ctk.CTkLabel(console_frame,
                                  text="操作日志",
                                  font=ctk.CTkFont(size=14, weight="bold"))
        console_title.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.console = ctk.CTkTextbox(console_frame, height=150)
        self.console.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        
    def _create_input_widgets(self):
        """创建输入框相关组件"""
        # 创建一个框架来包含所有输入字段
        input_frame = ctk.CTkFrame(self.main_frame)
        input_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        input_frame.grid_columnconfigure(1, weight=1)
        
        # 试卷ID输入
        id_label = ctk.CTkLabel(input_frame, text="试卷ID:", width=110)
        id_label.grid(row=0, column=0, padx=(15, 5), pady=15, sticky="w")
        self.id_entry = ctk.CTkEntry(input_frame, placeholder_text="输入试卷ID (必填)")
        self.id_entry.grid(row=0, column=1, padx=(5, 15), pady=15, sticky="ew")
        
        # 文件名输入
        name_label = ctk.CTkLabel(input_frame, text="答案文件名:", width=110)
        name_label.grid(row=1, column=0, padx=(15, 5), pady=15, sticky="w")
        self.name_entry = ctk.CTkEntry(input_frame, placeholder_text="输入文件名，不需要路径 (默认: 试卷答案.csv)")
        self.name_entry.grid(row=1, column=1, padx=(5, 15), pady=15, sticky="ew")
        self.name_entry.insert(0, "试卷答案.csv")  # 默认值
        
        # x_access_token输入
        token_label = ctk.CTkLabel(input_frame, text="x_access_token:", width=110)
        token_label.grid(row=2, column=0, padx=(15, 5), pady=15, sticky="w")
        self.token_entry = ctk.CTkEntry(input_frame, placeholder_text="输入x_access_token (必填)")
        self.token_entry.grid(row=2, column=1, padx=(5, 15), pady=15, sticky="ew")
        
        # xt_lang输入
        lang_label = ctk.CTkLabel(input_frame, text="xt_lang:", width=110)
        lang_label.grid(row=3, column=0, padx=(15, 5), pady=15, sticky="w")
        self.lang_entry = ctk.CTkEntry(input_frame, placeholder_text="输入xt_lang")
        self.lang_entry.grid(row=3, column=1, padx=(5, 15), pady=15, sticky="ew")
        self.lang_entry.insert(0, "zh")  # 默认值
        
    def _create_action_widgets(self):
        """创建操作按钮相关组件"""
        # 创建一个框架来包含所有按钮
        button_frame = ctk.CTkFrame(self.main_frame)
        button_frame.grid(row=3, column=0, padx=20, pady=15, sticky="ew")
        button_frame.grid_columnconfigure((0, 1), weight=1)
        
        # 获取数据按钮
        self.fetch_button = ctk.CTkButton(button_frame, 
                                       text="获取试卷答案", 
                                       command=self.fetch_data,
                                       height=40,
                                       font=ctk.CTkFont(size=16))
        self.fetch_button.grid(row=0, column=0, padx=(20, 10), pady=15, sticky="ew")
        
        # 清空输出按钮
        self.clear_button = ctk.CTkButton(button_frame, 
                                       text="清空日志", 
                                       command=self.clear_console,
                                       height=40,
                                       font=ctk.CTkFont(size=16),
                                       fg_color="#D35B58",
                                       hover_color="#C64F45")
        self.clear_button.grid(row=0, column=1, padx=(10, 20), pady=15, sticky="ew")
    
    def fetch_data(self):
        """获取试卷数据"""
        # 获取输入
        exam_id = self.id_entry.get().strip()
        filename = self.name_entry.get().strip() or "试卷答案.csv"
        x_access_token = self.token_entry.get().strip()
        xt_lang = self.lang_entry.get().strip() or "zh"
        
        if not exam_id:
            self.update_status("请输入有效的试卷ID", "red")
            return
        
        if not x_access_token:
            self.update_status("请输入x_access_token", "red")
            return
        
        # 确保文件名是合法的
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        # 构建输出文件路径
        output_file = os.path.join(self.answers_dir, filename)
        
        # 更新状态
        self.update_status("正在获取数据...", "orange")
        
        # 清空控制台
        self.clear_console()
        self.console.insert("end", f"==== 开始获取数据 [{time.strftime('%H:%M:%S')}] ====\n")
        self.console.insert("end", f"试卷ID: {exam_id}\n")
        self.console.insert("end", f"输出文件: {output_file}\n")
        self.console.insert("end", "------------------------------\n")
        
        # 重定向输出
        redirect_info = redirect_to_widget(self.console)
        
        try:
            # 构建URL
            url = f"https://examination.xuetangx.com/exam_room/cache_results?exam_id={exam_id}"
            print(f"正在从 {url} 获取数据...")
            
            # 设置cookies
            cookies = {
                "x_access_token": x_access_token,
                "xt_lang": xt_lang
            }
            print("使用提供的Cookie进行认证")
            
            # 获取数据
            json_data = fetch_json_data(url, cookies=cookies)
            extracted_data = extract_data(json_data)
            
            # 保存数据
            save_to_csv(extracted_data, output_file)
            
            self.update_status(f"成功获取并保存答案到 {filename}", "green")
            
        except Exception as e:
            self.update_status(f"获取数据失败: {e}", "red")
            print(f"错误详情: {e}")
        finally:
            # 恢复输出
            if redirect_info:
                restore_stdout(redirect_info)
    
    def clear_console(self):
        """清空控制台输出"""
        self.console.configure(state="normal")
        self.console.delete("0.0", "end")
        self.console.configure(state="normal")
    
    def update_status(self, message, color="black"):
        """更新状态标签"""
        self.status_label.configure(text=message, text_color=color)