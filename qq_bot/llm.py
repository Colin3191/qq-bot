"""智谱 GLM 大模型接入（使用 OpenAI 兼容接口）"""

from openai import AsyncOpenAI
from loguru import logger

from qq_bot.config import ZhipuConfig


class ZhipuLLM:
    """智谱 AI 聊天客户端"""

    def __init__(self, config: ZhipuConfig):
        self.config = config
        self.client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.api_base,
        )

    async def chat(self, messages: list[dict]) -> str:
        """发送聊天请求，返回回复文本"""
        try:
            resp = await self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
            )
            return resp.choices[0].message.content or ""
        except Exception as e:
            logger.error("智谱 API 调用失败: {}", e)
            return "抱歉，我暂时无法回复，请稍后再试。"
