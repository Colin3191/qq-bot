"""会话管理 - 维护每个聊天的对话历史"""

from collections import OrderedDict


class SessionManager:
    """简单的内存会话管理器"""

    def __init__(self, max_history: int = 20, max_sessions: int = 500):
        self._sessions: OrderedDict[str, list[dict]] = OrderedDict()
        self.max_history = max_history
        self.max_sessions = max_sessions

    def get_history(self, session_key: str) -> list[dict]:
        """获取会话历史"""
        return list(self._sessions.get(session_key, []))

    def add_message(self, session_key: str, role: str, content: str) -> None:
        """添加一条消息到会话"""
        if session_key not in self._sessions:
            # 淘汰最旧的会话
            if len(self._sessions) >= self.max_sessions:
                self._sessions.popitem(last=False)
            self._sessions[session_key] = []

        self._sessions[session_key].append({"role": role, "content": content})

        # 保留最近的 N 条消息
        if len(self._sessions[session_key]) > self.max_history:
            self._sessions[session_key] = self._sessions[session_key][-self.max_history:]

        # 移到末尾（LRU）
        self._sessions.move_to_end(session_key)

    def clear(self, session_key: str) -> None:
        """清空指定会话"""
        self._sessions.pop(session_key, None)
