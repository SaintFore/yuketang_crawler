"""多文件比较核心业务逻辑"""
import os
import csv
import glob
from collections import defaultdict


class MultiComparer:
    """多文件比较业务逻辑类"""
    
    def __init__(self, status_callback=None):
        self.status_callback = status_callback
        
    def update_status(self, message, color="black"):
        """更新状态"""
        if self.status_callback:
            self.status_callback(message, color)
            
    def read_csv_file(self, file_path):
        """读取CSV文件"""
        with open(file_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            return list(reader)
            
    def read_answers_dir(self, answers_dir):
        """读取答案目录中的所有CSV文件"""
        answer_files = {}
        for csv_file in glob.glob(os.path.join(answers_dir, "*.csv")):
            file_name = os.path.basename(csv_file).split(".")[0]
            answer_files[file_name] = self.read_csv_file(csv_file)
        return answer_files
        
    def create_answer_map(self, answer_data):
        """创建题目ID到答案的映射"""
        answer_map = {}
        for item in answer_data:
            problem_id = item.get("题目ID", "")
            answer = item.get("答案", "")
            if problem_id:
                answer_map[problem_id] = answer
        return answer_map
        
    def find_different_answers(self, all_answers):
        """找出不同答案的题目"""
        all_problem_ids = set()
        for user, answers in all_answers.items():
            for problem_id in answers.keys():
                all_problem_ids.add(problem_id)
                
        different_answers = {}
        for problem_id in all_problem_ids:
            current_answers = {}
            answered_users = 0
            
            for user, answers in all_answers.items():
                if problem_id in answers:
                    current_answers[user] = answers[problem_id]
                    answered_users += 1
                    
            unique_answers = set(current_answers.values())
            total_users = len(all_answers)
            
            if len(unique_answers) > 1 or answered_users < total_users:
                different_answers[problem_id] = current_answers
                
        return different_answers
        
    def map_to_original_questions(self, different_answers, original_questions):
        """将不同答案映射到原始题目信息"""
        question_map = {}
        for question in original_questions:
            problem_id = question.get("题目ID", "")
            if problem_id:
                question_map[problem_id] = question
                
        mapped_results = {}
        for problem_id, answers in different_answers.items():
            if problem_id in question_map:
                mapped_results[problem_id] = {
                    "question": question_map[problem_id],
                    "answers": answers,
                }
                
        return mapped_results
        
    def generate_report(self, mapped_results, reference_user="origin"):
        """生成差异报告"""
        report_lines = []
        
        try:
            sorted_results = sorted(
                mapped_results.items(),
                key=lambda x: int(x[1]["question"].get("题目顺序", "0")),
            )
        except:
            sorted_results = list(mapped_results.items())
            
        for problem_id, data in sorted_results:
            question = data["question"]
            answers = data["answers"]
            question_number = question.get("题目顺序", "未知")
            
            line = f"问题{question_number}：题目ID为{problem_id}；"
            
            if reference_user in answers:
                reference_answer = answers[reference_user]
                line += f"你选的是：{reference_answer}；"
            else:
                line += "你没有作答；"
                
            for user, answer in sorted(answers.items()):
                if user != reference_user:
                    line += f"{user}：{answer}；"
                    
            report_lines.append(line)
            
        return report_lines
        
    def compare_answers(self, answers_dir, original_file, reference_user, console_widget):
        """比较多个答案文件"""
        console_widget.clear()
        console_widget.log("开始比较答案文件", False)
        
        try:
            # 检查目录和文件
            if not os.path.exists(answers_dir):
                self.update_status(f"答案目录不存在: {answers_dir}", "red")
                return None
                
            if not os.path.exists(original_file):
                self.update_status(f"原始试卷文件不存在: {original_file}", "red")
                return None
                
            console_widget.log(f"正在读取答案目录: {answers_dir}", False)
            
            # 读取所有答案
            all_answer_files = self.read_answers_dir(answers_dir)
            if not all_answer_files:
                console_widget.log(f"在 {answers_dir} 目录中没有找到CSV文件", False)
                self.update_status("没有找到答案文件", "red")
                return None
                
            console_widget.log(f"找到答案文件: {', '.join(all_answer_files.keys())}", False)
            
            # 转换为映射
            all_answers = {}
            for file_name, answer_data in all_answer_files.items():
                all_answers[file_name] = self.create_answer_map(answer_data)
                
            # 读取原始题目
            console_widget.log(f"正在读取试卷信息: {original_file}", False)
            original_questions = self.read_csv_file(original_file)
            
            # 比较答案
            console_widget.log("正在比较答案...", False)
            different_answers = self.find_different_answers(all_answers)
            console_widget.log(f"发现 {len(different_answers)} 道题目有不同答案", False)
            
            # 映射到原始题目
            mapped_results = self.map_to_original_questions(different_answers, original_questions)
            
            # 生成报告
            console_widget.log(f"正在生成报告，参考用户: {reference_user}", False)
            report = self.generate_report(mapped_results, reference_user)
            
            if report:
                self.update_status(f"比较完成，发现 {len(report)} 道题目有差异", "green")
            else:
                self.update_status("所有答案一致，没有发现差异", "green")
                
            return report
            
        except Exception as e:
            self.update_status(f"比较过程中出错: {e}", "red")
            console_widget.log(f"错误详情: {e}", False)
            return None
            
    def save_report(self, report_lines, output_file):
        """保存报告到文件"""
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                for line in report_lines:
                    f.write(line + "\n")
            return True
        except Exception as e:
            self.update_status(f"保存报告失败: {e}", "red")
            return False
