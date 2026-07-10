import json
from typing import Any, Callable, Dict
from jsonschema import validate, ValidationError
from langchain.tools import BaseTool


SKILL_SCHEMA = {
    "type": "object",
    "required": ["name", "description", "parameters"],
    "properties": {
        "name": {"type": "string"},
        "description": {"type": "string"},
        "parameters": {"type": "object"} 
    }
}

class Skill(BaseTool):
    name: str
    description: str
    args_schema: dict  
    func: Callable     

    def _run(self, **kwargs) -> str:
        try:
            validate(instance=kwargs, schema=self.args_schema)
        except ValidationError as e:
            return f"Parameter validation error: {e.message}"
        return self.func(**kwargs)

class SkillRegistry:
    def __init__(self):
        self._skills = {}
    
    def register(self, skill_meta, func):
        validate(instance=skill_meta, schema=SKILL_SCHEMA)
        skill = Skill(
            name=skill_meta["name"],
            description=skill_meta["description"],
            args_schema=skill_meta["parameters"],
            func=func
        )
        self._skills[skill.name] = skill
    
    def get_tool_list(self):
        return list(self._skills.values())
    
    def get_tool_by_name(self, name):
        return self._skills.get(name)

# ---------- 示例用法 ----------
if __name__ == "__main__":
    registry = SkillRegistry()
    
    # 注册一个天气 Skill
    weather_meta = {
        "name": "get_weather",
        "description": "Get current weather for a city",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"}
            },
            "required": ["city"]
        }
    }
    def weather_func(city: str) -> str:
        return f"{city}: Cloudy, 15°C"
    registry.register(weather_meta, weather_func)
    
    # 注册一个代码执行 Skill
    code_meta = {
        "name": "execute_python",
        "description": "Execute Python code in a sandbox and return output",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python code to execute"}
            },
            "required": ["code"]
        }
    }
    def code_func(code: str) -> str:
        # 阶段4会替换为 Docker 沙箱执行
        return "Code execution not yet implemented."
    registry.register(code_meta, code_func)
    
    # 现在可以在 Agent 中使用 registry.get_tool_list() 来动态绑定了
    from langchain.agents import AgentExecutor, create_openai_tools_agent
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    
    llm = ChatOpenAI(
        model="deepseek-chat",
        openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
        openai_api_base="https://api.deepseek.com/v1",
        temperature=0,
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an assistant that can use skills."),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    agent = create_openai_tools_agent(llm, registry.get_tool_list(), prompt)
    executor = AgentExecutor(agent=agent, tools=registry.get_tool_list(), verbose=True)
    result = executor.invoke({"input": "查一下北京的天气"})
    print(result["output"])