import customtkinter as ctk

def setup_app_theme():
    """设置应用程序主题和外观"""
    # 设置主题和外观
    ctk.set_appearance_mode("System")  # 可选: "System", "Dark", "Light"
    ctk.set_default_color_theme("blue")  # 可选: "blue", "dark-blue", "green"