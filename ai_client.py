SYSTEM_PROMPT = """你是罗小黑，10岁猫妖，外冷内热，话少奶音，可猫可人。
性格单纯直接，不懂复杂成语，会一本正经地天真。
尾巴叫黑咻，比本人诚实，会偷偷蹭人或钻进衣服。
特殊状态：沾酒就醉（醉了黑咻满天飞）。

能力：
1. 读取分析文件（文本、PDF、图片里的文字）
2. 百科全书——可以回答各种知识问题

说话规则：
- 用短句，语气平淡认真，不说废话
- 不要每次回答都加动作描写（偶尔加一句尾巴的反应即可）
- 不知道就说不知道，不编
- 回答完一个问题后不要自动追问或重复 """


class AiClient:
    def __init__(self, config: dict):
        self.client = None
        self._endpoint = config['api_endpoint']
        self._api_key = config['api_key']
        self.model = config['model']

    def _ensure_client(self) -> bool:
        if self.client is not None:
            return True
        if not self._api_key:
            return False
        from openai import OpenAI
        self.client = OpenAI(
            base_url=self._endpoint,
            api_key=self._api_key,
        )
        return True

    def _build_messages(self, history: list) -> list:
        messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
        messages.extend(history)
        return messages

    def stream_chat(self, history: list):
        if not self._ensure_client():
            yield '请先在 API 配置中设置 API Key'
            return
        messages = self._build_messages(history)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True,
        )
        for chunk in response:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                yield delta.content
