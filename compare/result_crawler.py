import requests
import json
import csv
import os
from typing import Dict, Any, List, Union, Optional

def fetch_json_data(url: str, headers: Dict[str, str] = None, cookies: Dict[str, str] = None) -> Dict[str, Any]:
    """
    从指定URL获取JSON数据
    
    参数:
        url: 请求URL
        headers: 可选的请求头
        cookies: 可选的cookie
    """
    try:
        response = requests.get(url, headers=headers, cookies=cookies)
        response.raise_for_status()  # 如果响应状态码不是200，将引发异常
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        raise
    except json.JSONDecodeError:
        print("无法解析JSON响应")
        raise

def extract_data(json_data: Dict[str, Any]) -> List[Dict[str, Union[str, int, float]]]:
    """
    从JSON数据中提取problem_id和answer信息
    
    参数:
        json_data: 从API获取的JSON数据
    
    返回:
        提取后的数据列表
    """
    results = []
    if "data" in json_data and "results" in json_data["data"]:
        for item in json_data["data"]["results"]:
            problem_id = item.get("problem_id", "")
            
            # 提取结果/答案
            answer = ""
            result = item.get("result", {})
            
            # 处理不同类型的结果数据
            if isinstance(result, list) and result:
                answer = ", ".join(str(x) for x in result)
            elif isinstance(result, dict):
                answer = json.dumps(result, ensure_ascii=False)
            else:
                answer = str(result)
                
            # 创建数据项
            extracted_item = {
                "题目ID": problem_id,
                "答案": answer
            }
            results.append(extracted_item)
    
    print(f"共提取了 {len(results)} 个题目的答案")
    return results

def save_to_csv(data: List[Dict[str, Any]], filename: str) -> None:
    """
    将数据保存到CSV文件
    
    参数:
        data: 要保存的数据列表
        filename: 输出文件名
    """
    if not data:
        print("没有数据可保存")
        return
    
    # 确保目录存在
    os.makedirs(os.path.dirname(os.path.abspath(filename)) if os.path.dirname(filename) else ".", exist_ok=True)
    
    fieldnames = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:  # 使用utf-8-sig确保Excel正确识别中文
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"已成功保存 {len(data)} 条记录到 {filename}")