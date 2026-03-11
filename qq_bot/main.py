"""入口"""

import asyncio
import sys

from loguru import logger

from qq_bot.config import load_config
from qq_bot.bot import QQBot


def main():
    logger.remove()
    logger.add(sys.stderr, level="INFO")

    config = load_config()
    bot = QQBot(config)

    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        logger.info("机器人已停止")


if __name__ == "__main__":
    main()
