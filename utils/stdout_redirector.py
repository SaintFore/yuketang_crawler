import sys

class StdoutRedirector:
    """将标准输出重定向到GUI控制台的类"""
    
    def __init__(self, text_widget):
        self.text_widget = text_widget
        
    def write(self, string):
        self.text_widget.configure(state="normal")
        self.text_widget.insert("end", string)
        self.text_widget.see("end")
        self.text_widget.configure(state="disabled")
        
    def flush(self):
        pass

def redirect_to_widget(text_widget):
    """将标准输出重定向到文本控件"""
    old_stdout = sys.stdout
    sys.stdout = StdoutRedirector(text_widget)
    return old_stdout

def restore_stdout(old_stdout):
    """恢复标准输出"""
    sys.stdout = old_stdout