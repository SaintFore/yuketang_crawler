"""试卷提取功能Tab页面"""
import customtkinter as ctk
from ui.components.console_output import ConsoleOutput
from core.extractor import ExamExtractor


class ExtractTab(ctk.CTkFrame):
    """试卷提取功能Tab"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1)  # 让控制台区域可扩展
        
        # 创建业务逻辑实例
        self.extractor = ExamExtractor(status_callback=self.update_status)
        
        # 创建UI组件
        self._create_widgets()
        
    def _create_widgets(self):
        """创建UI组件"""
        # 步骤1：试卷ID输入
        self._create_step1_widgets()
        
        # 步骤2：代理控制
        self._create_step2_widgets()
        
        # 步骤3：处理JSON
        self._create_step3_widgets()
        
        # 步骤4：提取答案
        self._create_step4_widgets()
        
        # 状态显示
        self._create_status_widgets()
        
        # 控制台
        self._create_console_widgets()
        
    def _create_step1_widgets(self):
        """创建步骤1相关组件"""
        step1_frame = ctk.CTkFrame(self)
        step1_frame.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="ew")
        step1_frame.grid_columnconfigure(1, weight=1)
        
        step1_label = ctk.CTkLabel(step1_frame, text="步骤1: 输入雨课堂试卷ID", 
                                 font=ctk.CTkFont(size=16, weight="bold"))
        step1_label.grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 5), sticky="w")
        
        id_label = ctk.CTkLabel(step1_frame, text="试卷ID:", width=80)
        id_label.grid(row=1, column=0, padx=(15, 5), pady=15, sticky="w")
        
        self.id_entry = ctk.CTkEntry(step1_frame, placeholder_text="输入试卷ID")
        self.id_entry.grid(row=1, column=1, padx=(5, 15), pady=15, sticky="ew")
        
    def _create_step2_widgets(self):
        """创建步骤2相关组件"""
        step2_frame = ctk.CTkFrame(self)
        step2_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        step2_frame.grid_columnconfigure((0, 1), weight=1)
        
        step2_label = ctk.CTkLabel(step2_frame, text="步骤2: 启动代理并访问试卷", 
                                 font=ctk.CTkFont(size=16, weight="bold"))
        step2_label.grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 5), sticky="w")
        
        self.start_proxy_button = ctk.CTkButton(step2_frame, text="启动代理", 
                                              command=self.start_proxy)
        self.start_proxy_button.grid(row=1, column=0, padx=(15, 5), pady=15, sticky="ew")
        
        self.stop_proxy_button = ctk.CTkButton(step2_frame, text="终止代理", 
                                             command=self.stop_proxy,
                                             fg_color="#D35B58", hover_color="#C64F45")
        self.stop_proxy_button.grid(row=1, column=1, padx=(5, 15), pady=15, sticky="ew")
        
        # 提示信息
        hint_label = ctk.CTkLabel(step2_frame, 
                                text="启动代理后，请在浏览器中访问雨课堂试卷页面\n成功捕获后，代理会自动保存JSON数据",
                                font=ctk.CTkFont(size=12), text_color="gray60")
        hint_label.grid(row=2, column=0, columnspan=2, padx=15, pady=(0, 15))
        
    def _create_step3_widgets(self):
        """创建步骤3相关组件"""
        step3_frame = ctk.CTkFrame(self)
        step3_frame.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        step3_frame.grid_columnconfigure(0, weight=1)
        
        step3_label = ctk.CTkLabel(step3_frame, text="步骤3: 提取试卷内容", 
                                 font=ctk.CTkFont(size=16, weight="bold"))
        step3_label.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
        
        # 重排序选项
        self.reorder_var = ctk.StringVar(value="y")
        reorder_frame = ctk.CTkFrame(step3_frame)
        reorder_frame.grid(row=1, column=0, padx=15, pady=5, sticky="ew")
        
        reorder_label = ctk.CTkLabel(reorder_frame, text="是否重新排序选项(ABCD顺序):")
        reorder_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.reorder_yes = ctk.CTkRadioButton(reorder_frame, text="是", 
                                            variable=self.reorder_var, value="y")
        self.reorder_yes.grid(row=0, column=1, padx=10, pady=10)
        
        self.reorder_no = ctk.CTkRadioButton(reorder_frame, text="否", 
                                           variable=self.reorder_var, value="n")
        self.reorder_no.grid(row=0, column=2, padx=10, pady=10)
        
        self.process_button = ctk.CTkButton(step3_frame, text="提取试卷内容", 
                                          command=self.process_json)
        self.process_button.grid(row=2, column=0, padx=15, pady=15)
        
    def _create_step4_widgets(self):
        """创建步骤4相关组件"""
        step4_frame = ctk.CTkFrame(self)
        step4_frame.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        
        step4_label = ctk.CTkLabel(step4_frame, text="步骤4: 提取答案到CSV", 
                                 font=ctk.CTkFont(size=16, weight="bold"))
        step4_label.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
        
        hint_label = ctk.CTkLabel(step4_frame, text="答案将保存到: 雨课堂答案原始 目录",
                                font=ctk.CTkFont(size=12), text_color="gray60")
        hint_label.grid(row=1, column=0, padx=15, pady=5, sticky="w")
        
        self.save_button = ctk.CTkButton(step4_frame, text="提取答案到CSV", 
                                       command=self.save_answers_to_csv,
                                       fg_color="#2B7539", hover_color="#1E5C2C")
        self.save_button.grid(row=2, column=0, padx=15, pady=15)
        
    def _create_status_widgets(self):
        """创建状态显示组件"""
        status_frame = ctk.CTkFrame(self)
        status_frame.grid(row=4, column=0, padx=20, pady=5, sticky="ew")
        
        self.status_label = ctk.CTkLabel(status_frame, text="准备就绪", 
                                       font=ctk.CTkFont(size=14))
        self.status_label.grid(row=0, column=0, padx=15, pady=10)
        
    def _create_console_widgets(self):
        """创建控制台组件"""
        self.console = ConsoleOutput(self, height=120)
        self.console.grid(row=6, column=0, padx=20, pady=(5, 10), sticky="nsew")
        
    def start_proxy(self):
        """启动代理"""
        exam_id = self.id_entry.get()
        self.extractor.start_proxy(exam_id, self.console)
        
    def stop_proxy(self):
        """停止代理"""
        self.extractor.stop_proxy(self.console)
        
    def process_json(self):
        """处理JSON"""
        reorder_options = self.reorder_var.get() == "y"
        self.extractor.process_json(reorder_options, self.console)
        
    def save_answers_to_csv(self):
        """保存答案到CSV"""
        exam_id = self.id_entry.get()
        self.extractor.save_answers_to_csv(exam_id, self.console)
        
    def update_status(self, message, color="black"):
        """更新状态标签"""
        self.status_label.configure(text=message, text_color=color)
