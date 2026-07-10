from skill_registry import SkillRegistry
import json


MOCK_FLIGHTS = [
    {"from": "北京", "to": "巴黎", "date": "2025-07-15", "price": 5200, "airline": "中国国际航空"},
    {"from": "上海", "to": "巴黎", "date": "2025-07-15", "price": 4800, "airline": "东方航空"},
]

MOCK_ATTRACTIONS = {
    "巴黎": ["埃菲尔铁塔", "卢浮宫", "凯旋门"],
    "东京": ["浅草寺", "东京塔", "秋叶原"],
}


def get_weather(city: str) -> str:
    weather = {"巴黎": "晴 22°C", "东京": "多云 28°C", "北京": "晴 31°C"}
    return weather.get(city, f"{city}: 气温适宜")

def search_flights(from_city: str, to_city: str, date: str) -> str:
    results = [f for f in MOCK_FLIGHTS if f["from"]==from_city and f["to"]==to_city and f["date"]==date]
    if not results:
        return "未找到航班"
    return json.dumps(results, ensure_ascii=False)

def search_attractions(city: str) -> str:
    return json.dumps(MOCK_ATTRACTIONS.get(city, []), ensure_ascii=False)

def create_step1_registry():
    registry = SkillRegistry()
    registry.register(
        {"name":"get_weather", "description":"查询城市天气",
         "parameters":{"type":"object","properties":{"city":{"type":"string"}},"required":["city"]}},
        get_weather)
    registry.register(
        {"name":"search_flights", "description":"查询航班，参数：from_city, to_city, date(YYYY-MM-DD)",
         "parameters":{"type":"object","properties":{"from_city":{"type":"string"},"to_city":{"type":"string"},"date":{"type":"string"}},"required":["from_city","to_city","date"]}},
        search_flights)
    registry.register(
        {"name":"search_attractions", "description":"查询城市景点",
         "parameters":{"type":"object","properties":{"city":{"type":"string"}},"required":["city"]}},
        search_attractions)
    return registry