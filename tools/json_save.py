import json
import os
import csv
import argparse
from typing import Dict, List, Union, Any

def extract_answers(json_file: str = None, output_dir: str = None) -> str:
    """
    从雨课堂JSON文件中提取试题答案
    
    参数:
        json_file: JSON文件路径，默认为"雨课堂文档/exam_data.json"
        output_dir: 输出目录，默认为"雨课堂答案ID"
        
    返回:
        CSV文件的保存路径
    """
    # 如果没有提供JSON文件路径，使用默认路径
    if json_file is None:
        # 使用相对于当前脚本目录的上一级目录的路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        json_file = os.path.join(parent_dir, "雨课堂文档", "exam_data.json")
    
    # 确保文件存在
    if not os.path.exists(json_file):
        raise FileNotFoundError(f"找不到JSON文件: {json_file}")
    
    print(f"正在读取JSON文件: {json_file}")
    
    # 读取JSON文件
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 获取试卷ID
    exam_id = ""
    if "data" in data:
        if "exam_id" in data["data"]:
            exam_id = data["data"]["exam_id"]
        elif "id" in data["data"]:
            exam_id = data["data"]["id"]
    
    # 获取题目列表
    problems = []
    if "data" in data and "problems" in data["data"]:
        problems = data["data"]["problems"]
    
    # 创建输出目录
    if output_dir is None:
        output_dir = f"雨课堂答案{exam_id}" if exam_id else "雨课堂答案"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"创建输出目录: {output_dir}")
    
    # 准备CSV文件名
    output_file = os.path.join(output_dir, f"试卷答案_{exam_id}.csv")
    
    # 创建结果列表
    results = []
    
    # 遍历题目
    for index, problem in enumerate(problems, 1):
        problem_id = problem.get('ProblemID', problem.get('problem_id', ''))
        problem_type = problem.get('Type', '')
        options = problem.get('Options', [])
        
        # 构建选项字典
        option_dict = {}
        for i, opt in enumerate(options):
            key = chr(65 + i)  # A, B, C, D...
            value = opt.get('key', '')
            # 清除HTML标签
            value = value.replace('<p>', '').replace('</p>', '')
            option_dict[key] = value
        
        # 创建行数据
        row = {
            '题目顺序': index,
            '题目ID': problem_id,
            '题目类型': problem_type
        }
        
        # 添加选项
        for key, value in option_dict.items():
            row[f'选项{key}'] = value
        
        results.append(row)
    
    # 写入CSV文件
    if results:
        fieldnames = ['题目顺序', '题目ID', '题目类型']
        # 找出所有可能的选项键
        all_option_keys = set()
        for row in results:
            all_option_keys.update([k for k in row.keys() if k.startswith('选项')])
        
        # 按字母顺序排序选项
        option_fields = sorted(list(all_option_keys))
        fieldnames.extend(option_fields)
        
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        print(f"成功提取 {len(results)} 个问题的信息，已保存到文件: {output_file}")
        return output_file
    else:
        print("未能提取到任何题目信息")
        return None

def main():
    parser = argparse.ArgumentParser(description='从雨课堂JSON文件中提取题目信息并保存为CSV')
    parser.add_argument('-f', '--file', type=str, help='JSON文件路径 (默认: 雨课堂文档/exam_data.json)')
    parser.add_argument('-o', '--output', type=str, help='输出目录 (默认: 雨课堂答案ID)')
    
    args = parser.parse_args()
    
    try:
        extract_answers(args.file, args.output)
    except Exception as e:
        print(f"错误: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    main()