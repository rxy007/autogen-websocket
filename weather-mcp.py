from fastmcp import FastMCP
from typing import Any
import httpx
from urllib.parse import urljoin
from config import mcp_server_name, mcp_server_port, nws_api_base, user_agent

mcp = FastMCP(name=mcp_server_name)

async def make_nws_request(url: str) -> dict[str, Any] | None:
    """向 NWS API 发送请求，并进行适当的错误处理。"""
    headers = {
        "User-Agent": user_agent,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response
        except Exception as e:
            print(f"错误： {str(e)}")
            return None

def format_alert(feature: dict) -> str:
    """将警报 feature 格式化为可读的字符串。"""
    props = feature["properties"]
    return f"""
事件： {props.get('event', 'UnKnown')}
区域： {props.get('areaDesc', 'UnKnown')}
严重性： {props.get('severity', 'UnKnown')}
描述： {props.get('description', 'No description available')}
指示： {props.get('instruction', 'No specific instructions provided')}
"""

@mcp.tool()
async def get_alerts(state: str) -> str:
    """获取美国州的天气警报.

    Args:
        state: 两个字母的美国州代码(例如 CA、NY)
    """
    url = urljoin(nws_api_base, f"/alerts/active/area/{state}")
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "无法获取警报或未找到警报。"

    if not data["features"]:
        return "该州没有活跃的警报。"

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)


@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """获取某个位置的天气预报.

    Args:
        latitude: 纬度
        longitude: 经度
    """
    url = urljoin(nws_api_base, f"/points/{latitude},{longitude}")
    data = await make_nws_request(url)

    if not data:
        return "无法获取此位置的预报数据。"
    forecast_url = data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)
    if not forecast_data:
        return "无法获取详细预报。"

    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:
        forcast = f"""
{period['name']}:
温度: {period['temperature']} {period['temperatureUnit']}
风: {period['windSpeed']} {period['windDirection']}
预报: {period['detailedForecast']}
"""
        forecasts.append(forcast)

    return "\n---\n".join(forecasts)


if __name__ == '__main__':
    mcp.run(transport="sse", port=mcp_server_port, host='0.0.0.0')
    # mcp.run(transport="streamable-http", port=mcp_server_port, host='0.0.0.0')