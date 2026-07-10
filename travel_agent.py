import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing import TypedDict, Annotated, Sequence
from travel_skills import create_step1_registry

load_dotenv()

llm = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
    openai_api_base="https://api.deepseek.com/v1",
    temperature=0,
)

registry = create_step1_registry()
tools = registry.get_tool_list()
llm_with_tools = llm.bind_tools(tools)

class State(TypedDict):
    messages: Annotated[Sequence, add_messages]

def agent(state: State):
    system_prompt = SystemMessage(content="你是旅行助手，可以使用工具查询天气、航班、景点。")
    response = llm_with_tools.invoke([system_prompt] + list(state["messages"]))
    return {"messages": [response]}

def tool_executor(state: State):
    last_msg = state["messages"][-1]
    tool_msgs = []
    for tc in last_msg.tool_calls:
        tool = registry.get_tool_by_name(tc["name"])
        result = tool.invoke(tc["args"]) if tool else "工具不存在"
        tool_msgs.append(ToolMessage(content=result, tool_call_id=tc["id"]))
    return {"messages": tool_msgs}

def route(state: State):
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return END

workflow = StateGraph(State)
workflow.add_node("agent", agent)
workflow.add_node("tools", tool_executor)
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", route, {"tools":"tools", END:END})
workflow.add_edge("tools", "agent")

graph = workflow.compile()

if __name__ == "__main__":
    while True:
        user = input("你: ")
        if user in ("exit","quit"): break
        state = {"messages": [HumanMessage(content=user)]}
        for event in graph.stream(state):
            for node, s in event.items():
                if node=="agent":
                    msg = s["messages"][-1]
                    if hasattr(msg,"tool_calls") and msg.tool_calls:
                        print(f"[调用工具] {[t['name'] for t in msg.tool_calls]}")
                    else:
                        print(f"助手: {msg.content}")