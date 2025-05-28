"""雨课堂工具集合 - 主入口点"""
from ui.main_app import UnifiedYuketangApp
from utils.config import setup_app_theme
import sys
import os


def main():
    """主入口函数"""
    # 打印启动信息
    print("=" * 60)
    print("雨课堂工具集合启动")
    print("版本: 2.0 (重构版)")
    print(f"Python版本: {sys.version}")
    print(f"当前工作目录: {os.getcwd()}")
    print("=" * 60)
    print("功能模块:")
    print("  • 试卷提取: 捕获雨课堂试卷数据并转换为Markdown")
    print("  • 答案获取: 直接获取试卷答案并保存为CSV")
    print("  • 多文件比较: 比较多个答案文件找出差异")
    print("=" * 60)
    
    # 设置应用主题
    setup_app_theme()
    
    # 启动应用
    try:
        app = UnifiedYuketangApp()
        app.mainloop()
    except Exception as e:
        print(f"应用启动失败: {e}")
        input("按回车键退出...")
        return 1
        
    return 0


if __name__ == "__main__":
    exit(main())
