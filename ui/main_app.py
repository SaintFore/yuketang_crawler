"""统一的主应用窗口，使用TabView整合所有功能"""
import customtkinter as ctk
from ui.tabs.extract_tab import ExtractTab
from ui.tabs.compare_tab import CompareTab
from ui.tabs.multi_compare_tab import MultiCompareTab
from proxy.proxy_manager import ProxyManager


class UnifiedYuketangApp(ctk.CTk):
    """雨课堂工具集合主窗口"""
    
    def __init__(self):
        super().__init__()
        
        # 配置窗口
        self.title("雨课堂工具集合")
        self.geometry("900x800")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)  # 让TabView可以扩展
        
        # 创建UI组件
        self._create_widgets()

        # 设置窗口关闭时的处理
        self.protocol("WM_DELETE_WINDOW", self.on_closing)


    def on_closing(self):
        """窗口关闭时的处理函数"""
        ProxyManager.proxy_restore()
        self.destroy()

    def _create_widgets(self):
        """创建UI组件"""
        # 创建标题区域
        # self._create_header()
        
        # 创建TabView
        self._create_tabview()
        
    def _create_header(self):
        """创建标题区域"""
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="雨课堂工具集合",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=15)
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="试卷提取 • 答案获取 • 多文件比较",
            font=ctk.CTkFont(size=16),
            text_color="gray60"
        )
        subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 15))
        
    def _create_tabview(self):
        """创建TabView"""
        self.tabview = ctk.CTkTabview(self, width=850, height=650)
        self.tabview.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # 添加Tab页面
        self.tabview.add("试卷提取")
        self.tabview.add("答案获取")
        self.tabview.add("多文件比较")
        
        # 创建各个Tab的内容
        self.extract_tab = ExtractTab(self.tabview.tab("试卷提取"))
        self.extract_tab.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.compare_tab = CompareTab(self.tabview.tab("答案获取"))
        self.compare_tab.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.multi_compare_tab = MultiCompareTab(self.tabview.tab("多文件比较"))
        self.multi_compare_tab.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # 配置Tab内容区域的网格权重
        for tab_name in ["试卷提取", "答案获取", "多文件比较"]:
            self.tabview.tab(tab_name).grid_columnconfigure(0, weight=1)
            self.tabview.tab(tab_name).grid_rowconfigure(0, weight=1)
            
        # 设置默认选中的Tab
        self.tabview.set("试卷提取")
