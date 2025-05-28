"""试卷对比核心业务逻辑"""
import os
import time
from compare.result_crawler import fetch_json_data, extract_data, save_to_csv


class ExamComparer:
    """试卷对比业务逻辑类"""
    
    def __init__(self, status_callback=None):
        self.status_callback = status_callback
        self.answers_dir = os.path.join(os.getcwd(), "雨课堂答案")
        self._ensure_answers_dir()
        
    def _ensure_answers_dir(self):
        """确保答案目录存在"""
        if not os.path.exists(self.answers_dir):
            os.makedirs(self.answers_dir)
            
    def update_status(self, message, color="black"):
        """更新状态"""
        if self.status_callback:
            self.status_callback(message, color)
            
    def get_answers_dir(self):
        """获取答案目录路径"""
        return self.answers_dir
        
    def fetch_exam_data(self, exam_id, filename, x_access_token, xt_lang, console_widget):
        """获取试卷数据"""
        # 验证输入
        if not exam_id.strip():
            self.update_status("请输入有效的试卷ID", "red")
            return False
            
        if not x_access_token.strip():
            self.update_status("请输入x_access_token", "red")
            return False
            
        # 处理文件名
        if not filename.strip():
            filename = "试卷答案.csv"
        elif not filename.endswith('.csv'):
            filename += '.csv'
            
        output_file = os.path.join(self.answers_dir, filename)
        
        # 更新状态
        self.update_status("正在获取数据...", "orange")
        
        # 清空控制台并记录信息
        console_widget.clear()
        console_widget.log(f"开始获取数据", False)
        console_widget.log(f"试卷ID: {exam_id}", False)
        console_widget.log(f"输出文件: {output_file}", False)
        console_widget.log("------------------------------", False)
        
        # 开始重定向输出
        console_widget.start_redirect()
        
        try:
            # 构建URL和cookies
            url = f"https://examination.xuetangx.com/exam_room/cache_results?exam_id={exam_id}"
            print(f"正在从 {url} 获取数据...")
            
            cookies = {
                "x_access_token": x_access_token,
                "xt_lang": xt_lang or "zh"
            }
            print("使用提供的Cookie进行认证")
            
            # 获取和处理数据
            json_data = fetch_json_data(url, cookies=cookies)
            extracted_data = extract_data(json_data)
            save_to_csv(extracted_data, output_file)
            
            self.update_status(f"成功获取并保存答案到 {filename}", "green")
            return True
            
        except Exception as e:
            self.update_status(f"获取数据失败: {e}", "red")
            print(f"错误详情: {e}")
            return False
        finally:
            console_widget.stop_redirect()
