from mitmproxy import http
import os
import json
from datetime import datetime

# 雨课堂试卷id
id = ""
id = input("请输入雨课堂试卷id: ")
if not id:
    print("未输入试卷id，退出程序")
    exit()

# 目标URL
TARGET_URL = "examination.xuetangx.com/exam_room/show_paper?exam_id=" + id

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
            # 生成时间戳用于文件命名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.count += 1
            
            print(f"[捕获] 已截获目标请求 #{self.count}: {flow.request.pretty_url}")
            
            # 检查并保存JSON响应
            try:
                json_data = json.loads(flow.response.content.decode('utf-8'))
                json_path = os.path.join(self.save_dir, f"exam_data_{timestamp}.json")
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
                print(f"[保存] JSON数据已保存至: {json_path}")
            except json.JSONDecodeError:
                print("[错误] 响应内容不是有效的JSON格式")
                # 保存原始内容以备检查
                raw_path = os.path.join(self.save_dir, f"exam_raw_{timestamp}.txt")
                with open(raw_path, "wb") as f:
                    f.write(flow.response.content)
                print(f"[保存] 原始响应已保存至: {raw_path}")
            
            print("-" * 50)

# mitmproxy的入口点
addons = [TargetCapture()]