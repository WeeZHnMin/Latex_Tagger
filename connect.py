from openai import OpenAI
import base64
from PyQt5.QtCore import QBuffer, QIODevice, pyqtSignal, QObject

class Access(QObject):
    return_str = pyqtSignal(str)
    error_occurred = pyqtSignal(str)  # 新增错误信号

    def __init__(self, api, model):
        super().__init__()
        self.api_key = api
        self.selected_model = model

    def access_test(self, prompt):
        if 'qwen' in self.selected_model:
            cur_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        elif 'moon' in self.selected_model:
            cur_url = "https://api.moonshot.cn/v1"
        else:
            cur_url = "https://ark.cn-beijing.volces.com/api/v3"
        
        try:
            client = OpenAI(
                api_key=self.api_key,
                base_url=cur_url,
            )
            response = client.chat.completions.create(
                model=self.selected_model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                stream=True
            )
            # 处理流式响应
            output = ""
            for chunk in response:
                if chunk.choices:  # 检查是否有 choices
                    delta = chunk.choices[0].delta  # 获取 delta 对象
                    if delta.content:  # 检查是否有内容
                        content = delta.content
                        output += content  # 累加流中的内容
                        self.return_str.emit(output)  # 实时发射信号

        except Exception as e:
            self.error_occurred.emit(str(e))  # 发出错误信号

    def pixmap_to_base64(self, pixmap):
        image = pixmap.toImage()
        buffer = QBuffer()
        buffer.open(QIODevice.ReadWrite)
        image.save(buffer, "JPEG")  # 使用 JPEG 格式
        byte_data = buffer.data()
        base64_data = base64.b64encode(byte_data).decode('utf-8')
        return f"data:image/jpeg;base64,{base64_data}"  # 添加 MIME 类型前缀

    def access(self, pixmap, prompt):
        if 'qwen' in self.selected_model:
            cur_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        elif 'moon' in self.selected_model:
            cur_url = "https://api.moonshot.cn/v1"
        else:
            cur_url = "https://ark.cn-beijing.volces.com/api/v3"
        try:
            image_data = self.pixmap_to_base64(pixmap)
            client = OpenAI(
                api_key=self.api_key,
                base_url=cur_url,
            )
            response = client.chat.completions.create(
                model=self.selected_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_data  # 直接使用完整的 Base64 数据
                                }
                            },
                        ],
                    }
                ],
                stream=True
            )
            # 处理流式响应
            output = ""
            for chunk in response:
                if chunk.choices:  # 检查是否有 choices
                    delta = chunk.choices[0].delta  # 获取 delta 对象
                    if delta.content:  # 检查是否有内容
                        content = delta.content
                        output += content  # 累加流中的内容
                        self.return_str.emit(output)  # 实时发射信号

        except Exception as e:
            self.error_occurred.emit(str(e))  # 发出错误信号
    