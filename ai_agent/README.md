# 本地跨会话AI Agent 模板

## 功能简介
- 使用 DeepSeek API 作为大模型后端
- 支持本地文件存储的跨会话记忆
- 简单桌面 UI（PySimpleGUI，跨平台）
- 结构清晰，便于后续插件扩展

## 目录结构
```
ai_agent/
  main.py                # 程序入口
  requirements.txt       # 依赖
  README.md              # 说明文档
  agent/
    __init__.py
    memory.py            # 记忆管理
    tools.py             # 预留工具扩展
    plugins/             # 预留插件目录
  ui/
    app.py               # UI 代码
  data/
    history.json         # 对话历史
```

## 运行方法
1. 安装依赖：`pip install -r requirements.txt`
2. 配置 DeepSeek API Key（可在 main.py 或 .env 文件中设置）
3. 运行：`python main.py`

## 后续扩展
- 支持更多插件（如文件操作、日历、Web搜索等）
- 支持多窗口/多会话
- 支持本地大模型
