"""QQ 机器人核心 - 使用 botpy SDK 连接 QQ"""

import asyncio
from collections import deque
from typing import TYPE_CHECKING

from loguru import logger

from qq_bot.config import AppConfig
from qq_bot.llm import ZhipuLLM
from qq_bot.session import SessionManager

try:
    import botpy
    from botpy.message import C2CMessage, GroupMessage
except ImportError:
    raise ImportError("请安装 qq-botpy: pip install qq-botpy")

if TYPE_CHECKING:
    from botpy.message import C2CMessage, GroupMessage


class QQBot:
    """QQ 聊天机器人"""

    def __init__(self, config: AppConfig):
        self.config = config
        self.llm = ZhipuLLM(config.zhipu)
        self.sessions = SessionManager(max_history=config.max_history)
        self._processed_ids: deque = deque(maxlen=1000)
        self._msg_seq: int = 0
        from typing import Optional
        self._client: Optional[botpy.Client] = None

    def _is_allowed(self, user_id: str) -> bool:
        """检查用户是否在白名单中"""
        allow = self.config.qq.allow_from
        if not allow:
            return False
        if "*" in allow:
            return True
        return user_id in allow

    def _make_client(self) -> "botpy.Client":
        """创建 botpy Client 子类，绑定消息回调"""
        bot = self
        intents = botpy.Intents(public_messages=True, direct_message=True)

        class _Client(botpy.Client):
            def __init__(self):
                super().__init__(intents=intents, ext_handlers=False)

            async def on_ready(self):
                logger.info("QQ 机器人已上线: {}", self.robot.name)

            async def on_c2c_message_create(self, message: "C2CMessage"):
                await bot._on_message(message, is_group=False)

            async def on_group_at_message_create(self, message: "GroupMessage"):
                await bot._on_message(message, is_group=True)

        return _Client()

    async def _on_message(self, data: "C2CMessage | GroupMessage", is_group: bool) -> None:
        """处理收到的消息"""
        try:
            # 消息去重
            if data.id in self._processed_ids:
                return
            self._processed_ids.append(data.id)

            content = (data.content or "").strip()
            if not content:
                return

            if is_group:
                chat_id = data.group_openid
                user_id = data.author.member_openid
            else:
                chat_id = str(getattr(data.author, "user_openid", "unknown"))
                user_id = chat_id

            if not self._is_allowed(user_id):
                logger.warning("用户 {} 不在白名单中", user_id)
                return

            # 特殊命令
            if content in ("/clear", "/reset", "清空记录"):
                self.sessions.clear(chat_id)
                await self._send(chat_id, "对话已清空 ✨", data.id, is_group)
                return

            # 构建消息列表
            session_key = f"{'group' if is_group else 'c2c'}:{chat_id}"
            self.sessions.add_message(session_key, "user", content)

            messages = [{"role": "system", "content": self.config.zhipu.system_prompt}]
            messages.extend(self.sessions.get_history(session_key))

            # 调用 LLM
            reply = await self.llm.chat(messages)
            self.sessions.add_message(session_key, "assistant", reply)

            await self._send(chat_id, reply, data.id, is_group)

        except Exception:
            logger.exception("处理消息时出错")

    async def _send(self, chat_id: str, text: str, msg_id: str, is_group: bool) -> None:
        """发送消息"""
        if not self._client:
            return
        self._msg_seq += 1
        try:
            if is_group:
                await self._client.api.post_group_message(
                    group_openid=chat_id,
                    msg_type=0,
                    content=text,
                    msg_id=msg_id,
                    msg_seq=self._msg_seq,
                )
            else:
                await self._client.api.post_c2c_message(
                    openid=chat_id,
                    msg_type=0,
                    content=text,
                    msg_id=msg_id,
                    msg_seq=self._msg_seq,
                )
        except Exception as e:
            logger.error("发送消息失败: {}", e)

    async def run(self) -> None:
        """启动机器人"""
        if not self.config.qq.app_id or not self.config.qq.secret:
            logger.error("请在 config.json 中配置 qq.app_id 和 qq.secret")
            return

        if not self.config.zhipu.api_key:
            logger.error("请在 config.json 中配置 zhipu.api_key")
            return

        self._client = self._make_client()
        logger.info("正在启动 QQ 机器人...")

        while True:
            try:
                await self._client.start(
                    appid=self.config.qq.app_id,
                    secret=self.config.qq.secret,
                )
            except Exception as e:
                logger.warning("QQ 连接断开: {}", e)
            logger.info("5 秒后重连...")
            await asyncio.sleep(5)
