import os
import csv
import glob
import argparse
from collections import defaultdict
import json

def read_csv_file(file_path):
    """读取CSV文件，返回字典列表"""
    with open(file_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return list(reader)

def read_answers_dir(answers_dir):
    """读取答案目录中的所有CSV文件"""
    answer_files = {}
    for csv_file in glob.glob(os.path.join(answers_dir, "*.csv")):
        file_name = os.path.basename(csv_file).split(".")[0]
        answer_files[file_name] = read_csv_file(csv_file)
    return answer_files


def create_answer_map(answer_data):
    """创建题目ID到答案的映射"""
    answer_map = {}
    for item in answer_data:
        problem_id = item.get("题目ID", "")
        answer = item.get("答案", "")
        if problem_id:
            answer_map[problem_id] = answer
    return answer_map


def find_different_answers(all_answers):
    """找出不同答案的题目，包括独有题目"""
    # 获取所有题目ID
    all_problem_ids = set()
    for user, answers in all_answers.items():
        for problem_id in answers.keys():
            all_problem_ids.add(problem_id)

    # 找出有分歧的题目
    different_answers = {}
    for problem_id in all_problem_ids:
        current_answers = {}
        answered_users = 0  # 记录回答该题的用户数

        for user, answers in all_answers.items():
            if problem_id in answers:
                current_answers[user] = answers[problem_id]
                answered_users += 1

        # 判断条件：1. 有多个不同答案 或 2. 不是所有用户都回答了这道题
        unique_answers = set(current_answers.values())
        total_users = len(all_answers)

        if len(unique_answers) > 1 or answered_users < total_users:
            different_answers[problem_id] = current_answers

    return different_answers


def map_to_original_questions(different_answers, original_questions):
    """将不同答案映射到原始题目信息"""
    # 创建题目ID到题目信息的映射
    question_map = {}
    for question in original_questions:
        problem_id = question.get("题目ID", "")
        if problem_id:
            question_map[problem_id] = question

    # 将不同答案映射到题目信息
    mapped_results = {}
    for problem_id, answers in different_answers.items():
        if problem_id in question_map:
            mapped_results[problem_id] = {
                "question": question_map[problem_id],
                "answers": answers,
            }

    return mapped_results


def generate_report(mapped_results, reference_user="mzl"):
    """生成差异报告，包括独有题目的显示"""
    report_lines = []

    # 按题目顺序排序
    try:
        sorted_results = sorted(
            mapped_results.items(),
            key=lambda x: int(x[1]["question"].get("题目顺序", "0")),
        )
    except:
        # 如果排序失败，使用原始顺序
        sorted_results = list(mapped_results.items())

    for problem_id, data in sorted_results:
        question = data["question"]
        answers = data["answers"]
        question_number = question.get("题目顺序", "未知")

        # 构建报告行
        line = f"问题{question_number}：题目ID为{problem_id}；"

        # 添加"你选的是"部分，使用参考用户的答案
        if reference_user in answers:
            reference_answer = answers[reference_user]
            line += f"你选的是：{reference_answer}；"
        else:
            line += "你没有作答；"

        # 添加所有用户的答案，标记未回答的用户
        all_users = set(answers.keys())

        # 按顺序添加已回答用户
        for user, answer in sorted(answers.items()):
            if user != reference_user:  # 避免重复显示参考用户
                line += f"{user}：{answer}；"

        report_lines.append(line)

    return report_lines


def compare_answers(answers_dir, original_file, reference_user="mzl"):
    """比较多个答案文件，找出不同之处"""
    # 读取所有答案
    print(f"正在读取答案目录: {answers_dir}")
    all_answer_files = read_answers_dir(answers_dir)
    if not all_answer_files:
        print(f"警告: 在 {answers_dir} 目录中没有找到CSV文件")
        return []

    print(f"找到以下答案文件: {', '.join(all_answer_files.keys())}")

    # 将答案转换为映射
    all_answers = {}
    for file_name, answer_data in all_answer_files.items():
        all_answers[file_name] = create_answer_map(answer_data)

    # 读取原始题目信息
    print(f"正在读取试卷信息: {original_file}")
    original_questions = read_csv_file(original_file)

    # 找出答案不同的题目
    print("正在比较答案...")
    different_answers = find_different_answers(all_answers)
    print(f"发现 {len(different_answers)} 道题目有不同答案")

    # 映射到原始题目
    mapped_results = map_to_original_questions(different_answers, original_questions)

    # 生成报告
    print(f"正在生成报告，参考用户: {reference_user}")
    report = generate_report(mapped_results, reference_user)

    return report


def save_report(report_lines, output_file):
    """保存报告到文件"""
    with open(output_file, "w", encoding="utf-8") as f:
        for line in report_lines:
            f.write(line + "\n")
    print(f"报告已保存到: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="比较多个雨课堂答案CSV文件")
    parser.add_argument(
        "--answers-dir",
        type=str,
        default="雨课堂答案",
        help="包含答案CSV文件的目录 (默认: 雨课堂答案)",
    )
    parser.add_argument(
        "--original-file",
        type=str,
        default="雨课堂答案原始/试卷答案.csv",
        help="原始试卷信息CSV文件 (默认: 雨课堂答案原始/试卷答案.csv)",
    )
    parser.add_argument(
        "--r",
        type=str,
        default="origin",
        help='参考用户名，在报告中显示为"你" (默认: origin)',
    )
    parser.add_argument(
        "--output",
        type=str,
        default="答案比对结果.txt",
        help="输出报告文件名 (默认: 答案比对结果.txt)",
    )

    args = parser.parse_args()

    # 确保路径存在
    if not os.path.exists(args.answers_dir):
        print(f"错误: 答案目录不存在: {args.answers_dir}")
        return 1

    if not os.path.exists(args.original_file):
        print(f"错误: 原始试卷文件不存在: {args.original_file}")
        return 1

    # 比较答案
    report = compare_answers(args.answers_dir, args.original_file, args.r)

    if not report:
        print("没有找到需要比较的答案或所有答案一致")
        return 0

    # 打印报告
    print("\n===== 答案比对结果 =====")
    for line in report:
        print(line)

    # 保存报告
    save_report(report, args.output)

    return 0


if __name__ == "__main__":
    main()
