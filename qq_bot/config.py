"""配置管理"""

import json
import sys
from pathlib import Path

from pydantic import BaseModel, Field
from loguru import logger


class QQConfig(BaseModel):
    """QQ 机器人配置"""
    app_id: str = ""
    secret: str = ""
    allow_from: list[str] = Field(default_factory=lambda: ["*"])


class ZhipuConfig(BaseModel):
    """智谱 AI 配置"""
    api_key: str = ""
    model: str = "glm-4-flash"
    api_base: str = "https://open.bigmodel.cn/api/paas/v4"
    max_tokens: int = 4096
    temperature: float = 0.7
    system_prompt: str = "你是一个友好的 QQ 聊天机器人。"


class AppConfig(BaseModel):
    """应用配置"""
    qq: QQConfig = Field(default_factory=QQConfig)
    zhipu: ZhipuConfig = Field(default_factory=ZhipuConfig)
    max_history: int = 20  # 每个会话保留的最大历史消息数


from typing import Optional

CONFIG_PATH = Path("config.json")


def load_config(path: Optional[Path] = None) -> AppConfig:
    """加载配置文件"""
    p = path or CONFIG_PATH
    if not p.exists():
        logger.warning("配置文件 {} 不存在，使用默认配置", p)
        return AppConfig()
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return AppConfig(**data)
    except Exception as e:
        logger.error("加载配置失败: {}", e)
        sys.exit(1)
