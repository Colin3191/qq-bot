# QQ 聊天机器人

基于智谱 GLM 大模型的 QQ 聊天机器人。

## 快速开始

1. 创建虚拟环境并安装依赖：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

2. 复制配置文件并填写你的密钥：

```bash
cp config.example.json config.json
```

需要填写：
- `qq.app_id` / `qq.secret` — 从 [QQ 开放平台](https://q.qq.com) 获取
- `zhipu.api_key` — 从 [智谱开放平台](https://open.bigmodel.cn) 获取

3. 启动：

```bash
python -m qq_bot.main
```

## 功能

- 支持私聊（C2C）和群聊（@机器人）
- 多轮对话记忆（默认保留最近 20 条）
- 发送 `/clear` 或 `清空记录` 可重置对话
- 断线自动重连
- 用户白名单控制（`allow_from` 设为 `["*"]` 允许所有人）
