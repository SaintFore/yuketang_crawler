"""多文件比较功能Tab页面"""
import customtkinter as ctk
from ui.components.console_output import ConsoleOutput
from core.multi_comparer import MultiComparer
import os


class MultiCompareTab(ctk.CTkFrame):
    """多文件比较功能Tab"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)  # 让控制台区域可扩展
        
        # 创建业务逻辑实例
        self.multi_comparer = MultiComparer(status_callback=self.update_status)
        
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
        
        title_label = ctk.CTkLabel(desc_frame, text="多文件答案比较工具", 
                                 font=ctk.CTkFont(size=20, weight="bold"))
        title_label.grid(row=0, column=0, padx=15, pady=(15, 5))
        
        desc_label = ctk.CTkLabel(desc_frame,
                                text="比较多个答案CSV文件，找出不同答案的题目",
                                font=ctk.CTkFont(size=14), text_color="gray60")
        desc_label.grid(row=1, column=0, padx=15, pady=(0, 15))
        
    def _create_input_widgets(self):
        """创建输入组件"""
        input_frame = ctk.CTkFrame(self)
        input_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        input_frame.grid_columnconfigure(1, weight=1)
        
        # 答案目录
        answers_label = ctk.CTkLabel(input_frame, text="答案目录:", width=120)
        answers_label.grid(row=0, column=0, padx=(15, 5), pady=15, sticky="w")
        self.answers_entry = ctk.CTkEntry(input_frame, placeholder_text="包含答案CSV文件的目录")
        self.answers_entry.grid(row=0, column=1, padx=(5, 15), pady=15, sticky="ew")
        self.answers_entry.insert(0, "雨课堂答案")
        
        # 原始文件
        original_label = ctk.CTkLabel(input_frame, text="原始试卷文件:", width=120)
        original_label.grid(row=1, column=0, padx=(15, 5), pady=15, sticky="w")
        self.original_entry = ctk.CTkEntry(input_frame, placeholder_text="原始试卷信息CSV文件")
        self.original_entry.grid(row=1, column=1, padx=(5, 15), pady=15, sticky="ew")
        self.original_entry.insert(0, "雨课堂答案原始/试卷答案.csv")
        
        # 参考用户
        reference_label = ctk.CTkLabel(input_frame, text="参考用户名:", width=120)
        reference_label.grid(row=2, column=0, padx=(15, 5), pady=15, sticky="w")
        self.reference_entry = ctk.CTkEntry(input_frame, placeholder_text="在报告中显示为'你'的用户名")
        self.reference_entry.grid(row=2, column=1, padx=(5, 15), pady=15, sticky="ew")
        self.reference_entry.insert(0, "origin")
        
        # 输出文件
        output_label = ctk.CTkLabel(input_frame, text="输出报告文件:", width=120)
        output_label.grid(row=3, column=0, padx=(15, 5), pady=15, sticky="w")
        self.output_entry = ctk.CTkEntry(input_frame, placeholder_text="报告文件名")
        self.output_entry.grid(row=3, column=1, padx=(5, 15), pady=15, sticky="ew")
        self.output_entry.insert(0, "答案比对结果.txt")
        
    def _create_action_widgets(self):
        """创建操作按钮组件"""
        action_frame = ctk.CTkFrame(self)
        action_frame.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        action_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.compare_button = ctk.CTkButton(action_frame, text="开始比较", 
                                          command=self.compare_answers, height=40,
                                          font=ctk.CTkFont(size=16))
        self.compare_button.grid(row=0, column=0, padx=(15, 5), pady=15, sticky="ew")
        
        self.view_button = ctk.CTkButton(action_frame, text="查看报告", 
                                       command=self.view_report, height=40,
                                       font=ctk.CTkFont(size=16),
                                       fg_color="#2B7539", hover_color="#1E5C2C")
        self.view_button.grid(row=0, column=1, padx=5, pady=15, sticky="ew")
        
        self.clear_button = ctk.CTkButton(action_frame, text="清空日志", 
                                        command=self.clear_console, height=40,
                                        font=ctk.CTkFont(size=16),
                                        fg_color="#D35B58", hover_color="#C64F45")
        self.clear_button.grid(row=0, column=2, padx=(5, 15), pady=15, sticky="ew")
        
    def _create_status_widgets(self):
        """创建状态显示组件"""
        status_frame = ctk.CTkFrame(self)
        status_frame.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        
        self.status_label = ctk.CTkLabel(status_frame, text="准备就绪", 
                                       font=ctk.CTkFont(size=14))
        self.status_label.grid(row=0, column=0, padx=15, pady=10)
        
    def _create_console_widgets(self):
        """创建控制台组件"""
        self.console = ConsoleOutput(self, height=120)
        self.console.grid(row=4, column=0, padx=20, pady=(5, 10), sticky="nsew")
        
    def compare_answers(self):
        """比较答案文件"""
        answers_dir = self.answers_entry.get().strip()
        original_file = self.original_entry.get().strip()
        reference_user = self.reference_entry.get().strip()
        
        # 比较答案
        report = self.multi_comparer.compare_answers(answers_dir, original_file, reference_user, self.console)
        
        if report:
            # 保存报告
            output_file = self.output_entry.get().strip()
            if self.multi_comparer.save_report(report, output_file):
                self.console.log(f"报告已保存到: {output_file}", False)
                
            # 在控制台显示报告
            self.console.log("\\n===== 答案比对结果 =====", False)
            for line in report[:10]:  # 只显示前10行，避免界面过于拥挤
                self.console.log(line, False)
            if len(report) > 10:
                self.console.log(f"... 还有 {len(report) - 10} 行结果，请查看完整报告文件", False)
                
    def view_report(self):
        """查看报告文件"""
        output_file = self.output_entry.get().strip()
        if os.path.exists(output_file):
            try:
                os.startfile(output_file)  # Windows
            except:
                self.update_status(f"无法打开文件: {output_file}", "red")
        else:
            self.update_status("报告文件不存在，请先进行比较", "red")
            
    def clear_console(self):
        """清空控制台"""
        self.console.clear()
        
    def update_status(self, message, color="black"):
        """更新状态标签"""
        self.status_label.configure(text=message, text_color=color)
