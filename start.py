from ui.main_window import YuketangApp
from utils.config import setup_app_theme

def main():
    # 设置应用主题
    setup_app_theme()
    
    # 启动应用
    app = YuketangApp()
    app.mainloop()

if __name__ == "__main__":
    main()