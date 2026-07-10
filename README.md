# 旅行规划 Agent

基于 LangGraph + DeepSeek 的单轮查询旅行助手，支持工具调用。

## 功能
- 查询城市天气（模拟）
- 搜索航班（模拟）
- 查询景点（模拟）

## 技术栈
- LangGraph
- LangChain + OpenAI 兼容接口
- DeepSeek API

## 运行方式
1. 克隆项目
2. 创建虚拟环境并安装依赖：`pip install langgraph langchain langchain-openai python-dotenv`
3. 复制 `.env.example` 为 `.env`，填入你的 `DEEPSEEK_API_KEY`
4. 运行 `python step1_travel_agent.py`