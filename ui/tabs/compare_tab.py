"""试卷对比功能Tab页面"""
import customtkinter as ctk
from ui.components.console_output import ConsoleOutput
from core.comparer import ExamComparer


class CompareTab(ctk.CTkFrame):
    """试卷对比功能Tab"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)  # 让控制台区域可扩展
        
        # 创建业务逻辑实例
        self.comparer = ExamComparer(status_callback=self.update_status)
        
        # 创建UI组件
        self._create_widgets()
        
    def _create_widgets(self):
        """创建UI组件"""
        # 说明信息
        self._create_description()
        
        # 输入区域
        self._create_input_widgets()
        
        # 操作按钮区域
        self._create_action_widgets()
        
        # 状态显示
        self._create_status_widgets()
        
        # 控制台
        self._create_console_widgets()
        
    def _create_description(self):
        """创建说明信息"""
        desc_frame = ctk.CTkFrame(self)
        desc_frame.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="ew")
        
        title_label = ctk.CTkLabel(desc_frame, text="雨课堂试卷答案获取工具", 
                                 font=ctk.CTkFont(size=20, weight="bold"))
        title_label.grid(row=0, column=0, padx=15, pady=(15, 5))
        
        desc_label = ctk.CTkLabel(desc_frame,
                                text="本工具用于获取雨课堂试卷答案，将自动保存到'雨课堂答案'文件夹",
                                font=ctk.CTkFont(size=14), text_color="gray60")
        desc_label.grid(row=1, column=0, padx=15, pady=(0, 15))
        
    def _create_input_widgets(self):
        """创建输入组件"""
        input_frame = ctk.CTkFrame(self)
        input_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        input_frame.grid_columnconfigure(1, weight=1)
        
        # 试卷ID
        id_label = ctk.CTkLabel(input_frame, text="试卷ID:", width=120)
        id_label.grid(row=0, column=0, padx=(15, 5), pady=15, sticky="w")
        self.id_entry = ctk.CTkEntry(input_frame, placeholder_text="输入试卷ID (必填)")
        self.id_entry.grid(row=0, column=1, padx=(5, 15), pady=15, sticky="ew")
        
        # 文件名
        name_label = ctk.CTkLabel(input_frame, text="答案文件名:", width=120)
        name_label.grid(row=1, column=0, padx=(15, 5), pady=15, sticky="w")
        self.name_entry = ctk.CTkEntry(input_frame, placeholder_text="默认: 试卷答案.csv")
        self.name_entry.grid(row=1, column=1, padx=(5, 15), pady=15, sticky="ew")
        self.name_entry.insert(0, "试卷答案.csv")
        
        # Token
        token_label = ctk.CTkLabel(input_frame, text="x_access_token:", width=120)
        token_label.grid(row=2, column=0, padx=(15, 5), pady=15, sticky="w")
        self.token_entry = ctk.CTkEntry(input_frame, placeholder_text="输入x_access_token (必填)")
        self.token_entry.grid(row=2, column=1, padx=(5, 15), pady=15, sticky="ew")
        
        # 语言
        lang_label = ctk.CTkLabel(input_frame, text="xt_lang:", width=120)
        lang_label.grid(row=3, column=0, padx=(15, 5), pady=15, sticky="w")
        self.lang_entry = ctk.CTkEntry(input_frame, placeholder_text="默认: zh")
        self.lang_entry.grid(row=3, column=1, padx=(5, 15), pady=15, sticky="ew")
        self.lang_entry.insert(0, "zh")
        
    def _create_action_widgets(self):
        """创建操作按钮组件"""
        action_frame = ctk.CTkFrame(self)
        action_frame.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        action_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.fetch_button = ctk.CTkButton(action_frame, text="获取试卷答案", 
                                        command=self.fetch_data, height=40,
                                        font=ctk.CTkFont(size=16))
        self.fetch_button.grid(row=0, column=0, padx=(15, 5), pady=15, sticky="ew")
        
        self.clear_button = ctk.CTkButton(action_frame, text="清空日志", 
                                        command=self.clear_console, height=40,
                                        font=ctk.CTkFont(size=16),
                                        fg_color="#D35B58", hover_color="#C64F45")
        self.clear_button.grid(row=0, column=1, padx=(5, 15), pady=15, sticky="ew")
        
    def _create_status_widgets(self):
        """创建状态显示组件"""
        status_frame = ctk.CTkFrame(self)
        status_frame.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(status_frame, text="准备就绪", 
                                       font=ctk.CTkFont(size=14))
        self.status_label.grid(row=0, column=0, padx=15, pady=5)
        
        self.dir_label = ctk.CTkLabel(status_frame,
                                    text=f"答案将保存到: {self.comparer.get_answers_dir()}",
                                    font=ctk.CTkFont(size=12), text_color="gray60")
        self.dir_label.grid(row=1, column=0, padx=15, pady=5)
        
    def _create_console_widgets(self):
        """创建控制台组件"""
        self.console = ConsoleOutput(self, height=120)
        self.console.grid(row=4, column=0, padx=20, pady=(5, 10), sticky="nsew")
        
    def fetch_data(self):
        """获取试卷数据"""
        exam_id = self.id_entry.get().strip()
        filename = self.name_entry.get().strip()
        x_access_token = self.token_entry.get().strip()
        xt_lang = self.lang_entry.get().strip()
        
        self.comparer.fetch_exam_data(exam_id, filename, x_access_token, xt_lang, self.console)
        
    def clear_console(self):
        """清空控制台"""
        self.console.clear()
        
    def update_status(self, message, color="black"):
        """更新状态标签"""
        self.status_label.configure(text=message, text_color=color)
