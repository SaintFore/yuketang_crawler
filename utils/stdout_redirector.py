import sys
import threading
import queue

class StdoutRedirector:
    """将标准输出重定向到GUI控制台的类"""
    
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.queue = queue.Queue()
        self.running = True
        
        # 启动更新线程
        self.update_thread = threading.Thread(target=self._update_widget, daemon=True)
        self.update_thread.start()
        
    def write(self, string):
        # 将输出放入队列
        if string:  # 忽略空字符串
            self.queue.put(string)
            
    def flush(self):
        pass
        
    def _update_widget(self):
        """在单独的线程中更新文本控件"""
        while self.running:
            try:
                # 等待新的输出（最多100毫秒）
                try:
                    text = self.queue.get(timeout=0.1)
                    
                    # 在主线程中更新UI
                    self.text_widget.after(0, self._insert_text, text)
                    self.queue.task_done()
                except queue.Empty:
                    continue
            except Exception as e:
                print(f"Error in _update_widget: {e}")
                
    def _insert_text(self, text):
        """在GUI线程中执行的插入文本方法"""
        try:
            self.text_widget.configure(state="normal")
            self.text_widget.insert("end", text)
            self.text_widget.see("end")
            self.text_widget.configure(state="disabled")
        except Exception as e:
            print(f"Error in _insert_text: {e}")
            
    def close(self):
        """关闭更新线程"""
        self.running = False
        if self.update_thread.is_alive():
            self.update_thread.join(1.0)  # 等待线程结束（最多1秒）

def redirect_to_widget(text_widget):
    """将标准输出重定向到文本控件"""
    old_stdout = sys.stdout
    redirector = StdoutRedirector(text_widget)
    sys.stdout = redirector
    return (old_stdout, redirector)

def restore_stdout(redirect_info):
    """恢复标准输出"""
    old_stdout, redirector = redirect_info
    # 关闭重定向器
    redirector.close()
    sys.stdout = old_stdout