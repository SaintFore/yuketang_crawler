from mitmproxy import http
import os
import json
import sys

# 从环境变量获取试卷ID
id = os.environ.get("EXAM_ID", "")

# # 如果通过命令行参数传入，则优先使用命令行参数
# if len(sys.argv) > 1:
#     id = sys.argv[1]

# 尝试从标准输入读取（如果环境变量和命令行参数都没有设置）
if not id:
    try:
        print("请输入雨课堂试卷id: ", end="", flush=True)
        id = input().strip()
    except:
        pass

if not id:
    print("未输入试卷id，退出程序")
    exit()

# 目标URL
TARGET_URL = "examination.xuetangx.com/exam_room/show_paper?exam_id=" + id


# 打印当前使用的试卷ID
print(f"[配置] 当前使用的试卷ID: {id}")

class TargetCapture:
    def __init__(self):
        self.count = 0
        # 确保存储目录存在
        self.save_dir = "雨课堂文档"
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
            
    def response(self, flow: http.HTTPFlow) -> None:
        # 检查是否匹配目标URL
        if TARGET_URL in flow.request.pretty_url:
            # 捕获请求的数量
            self.count += 1

            # 保存的文件名
            json_name = "空"
            
            print(f"[捕获] 已截获目标请求 #{self.count}: {flow.request.pretty_url}")
            # 检查并保存JSON响应
            try:
                json_data = json.loads(flow.response.content.decode('utf-8'))
                # # 从JSON数据中获取试卷标题
                # json_name = json_data['data']['title']
                json_name = "exam_data"
                json_path = os.path.join(self.save_dir, f"{json_name}.json")
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
                print(f"[保存] JSON数据已保存至: {json_path}")
            except json.JSONDecodeError:
                print("[错误] 响应内容不是有效的JSON格式")
                # 保存原始内容以备检查
                raw_path = os.path.join(self.save_dir, f"exam_raw_{json_name}.txt")
                with open(raw_path, "wb") as f:
                    f.write(flow.response.content)
                print(f"[保存] 原始响应已保存至: {raw_path}")
            
            print("-" * 50)

# mitmproxy的入口点
addons = [TargetCapture()]