# QQ 聊天机器人

基于智谱 GLM 大模型的 QQ 聊天机器人。

## 配置

复制配置文件并填写密钥：

```bash
cp config.example.json config.json
```

需要填写：
- `qq.app_id` / `qq.secret` — 从 [QQ 开放平台](https://q.qq.com) 获取
- `zhipu.api_key` — 从 [智谱开放平台](https://open.bigmodel.cn) 获取

## 启动方式

### Docker（推荐）

服务器上只需安装 Docker，无需 Python 环境：

```bash
docker build -t qq-bot .
docker run -d --name qq-bot --restart unless-stopped \
  -v $(pwd)/config.json:/app/config.json \
  qq-bot
```

常用操作：

```bash
docker logs -f qq-bot     # 查看日志
docker restart qq-bot     # 重启
docker stop qq-bot        # 停止
```

更新代码后重新部署：

```bash
docker stop qq-bot && docker rm qq-bot
docker build -t qq-bot .
docker run -d --name qq-bot --restart unless-stopped \
  -v $(pwd)/config.json:/app/config.json \
  qq-bot
```

### 本地运行

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python -m qq_bot.main
```

### systemd 服务

适合不用 Docker、希望开机自启的场景：

```bash
cp qq-bot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable qq-bot
systemctl start qq-bot
```

查看日志：`journalctl -u qq-bot -f`

## 功能

- 支持私聊（C2C）和群聊（@机器人）
- 多轮对话记忆（默认保留最近 20 条）
- 发送 `/clear` 或 `清空记录` 可重置对话
- 断线自动重连
- 用户白名单控制（`allow_from` 设为 `["*"]` 允许所有人）
