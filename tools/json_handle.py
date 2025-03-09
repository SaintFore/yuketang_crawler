import json
import re
import os
from html import unescape

# JSON文件路径
json_file = "雨课堂文档/exam_data.json"

def clean_html(text):
    """清理HTML标签并保留基本格式"""
    # 移除段落标签
    text = re.sub(r'</?p>', '', text)
    # 移除其他HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    # 解码HTML实体
    text = unescape(text)
    # 清理多余的空白符
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_problems(json_file,reorder_options=False):
    """从JSON文件中提取问题"""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    title = data['data']['title']
    problems = data['data']['problems']
    
    output_file = f"{title}.md"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\n\n")
        
        for i, problem in enumerate(problems, 1):
            problem_type = problem['Type']
            type_text = problem['TypeText']
            body = clean_html(problem['Body'])
            
            f.write(f"## {i}. {body}\n\n")
            f.write(f"**题型**: {type_text}\n\n")
            
            # 处理不同类型的题目
            if problem_type in ['SingleChoice', 'MultipleChoice']:
                f.write("**选项**:\n\n")
                
                if reorder_options:
                    # 按照ABCD顺序重新排列选项
                    option_keys = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
                    options = problem['Options']
                    for j, option in enumerate(options):
                        if j < len(option_keys):
                            key = option_keys[j]
                            value = clean_html(option['value'])
                            f.write(f"- {key}: {value}\n")
                else:
                    # 使用原始key
                    for option in problem['Options']:
                        key = option['key']
                        value = clean_html(option['value'])
                        f.write(f"- {key}: {value}\n")
            
            elif problem_type == 'FillBlank':
                f.write("**填空题**\n\n")
            
            elif problem_type == 'Judgement':
                f.write("**选项**:\n\n")
                f.write("- 正确\n")
                f.write("- 错误\n")
            
            f.write("\n---\n\n")
    
    print(f"成功提取 {len(problems)} 个问题，已保存到文件: {output_file}")

if __name__ == "__main__":
    # 获取JSON文件路径，默认为当前目录下的show_paper.json
    while True:
        whether_order = input("是否需要处理题目顺序？(y/n): ").strip().lower()
        if whether_order in ['y', 'n']:
            break
        print("请输入 'y' 或 'n'")
    
    reorder_options = (whether_order == 'y')


    
    if os.path.exists(json_file):
        extract_problems(json_file, reorder_options)
    else:
        print(f"错误: 找不到文件 '{json_file}'")