from ui.main_window import YuketangApp
from utils.config import setup_app_theme
import sys
import os

def main():
    # 打印调试信息
    print("=" * 50)
    print("雨课堂试卷提取工具启动")
    print(f"Python版本: {sys.version}")
    print(f"当前工作目录: {os.getcwd()}")
    print("=" * 50)
    
    # 设置应用主题
    setup_app_theme()
    
    # 启动应用
    app = YuketangApp()
    app.mainloop()

if __name__ == "__main__":
    main()