import time
from typing import cast

from autogen_agentchat.agents import UserProxyAgent, AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination, SourceMatchTermination
from autogen_agentchat.messages import MultiModalMessage
from autogen_agentchat.teams import SelectorGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import SseServerParams, SseMcpToolAdapter
from fastapi import WebSocket
from config import mcp_server_port

from config import model_info, model_api_key, model_base_url, model_name
from default_agent import DefaultAgent
from user_agent import UserAgentC

model_client = OpenAIChatCompletionClient(
    model=model_name,
    base_url=model_base_url,
    api_key=model_api_key,
    model_info=model_info
)

weather_sever = SseServerParams(
    url=f"http://127.0.0.1:{mcp_server_port}/sse"
)

async def run_agent(task, ws: WebSocket = None):
    if ws:
        user_agent_c = UserAgentC(name="user_agent", description="提示用户输入必要信息", input_func=ws.receive_text,
                                  output_func=ws.send_text)
    else:
        user_agent_c = UserProxyAgent(name="user_agent", description="提示用户输入必要信息")

    alert_agent = AssistantAgent(
        name="alert_agent",
        model_client=model_client,
        tools=[await SseMcpToolAdapter.from_server_params(weather_sever, "get_alerts")],
        reflect_on_tool_use=True,
        system_message="""你是一个天气预警专家，通过用户提供的州信息，通过查询工具，获取预警信息。
        最终总结输出并在之后输出"Termination"。"""
    )

    forecast_agent = AssistantAgent(
        name="forecast_agent",
        model_client=model_client,
        tools=[await SseMcpToolAdapter.from_server_params(weather_sever, "get_forecast")],
        reflect_on_tool_use=True,
        system_message="""你是一个天气预报员,通过用户提供位置信息查询工具，获取天气信息。
        最终总结输出并在之后输出"Termination"。"""
    )

    chat_agent = AssistantAgent(
        name="chat_agent",
        model_client=model_client,
        system_message="""你是一个聊天机器人，和用户进行闲聊"""
    )

    default_agent = DefaultAgent(
        name="default_agent",

    )

    text_term = TextMentionTermination("Termination")
    max_message_term = MaxMessageTermination(25)
    source_term = SourceMatchTermination(sources=["default_agent"])
    term = text_term|max_message_term|source_term

    team = SelectorGroupChat(
        [chat_agent, user_agent_c, forecast_agent, alert_agent],
        model_client=model_client,
        termination_condition=term,
        model_client_streaming=True,
        allow_repeated_speaker=True
    )
    steam = team.run_stream(task=task)
    streaming_chunks = []
    async message in steam:
    if isinstance(message, TaskResult):
        pass

    elif isinstance(message, Response):
        duration = time.time() - start_time

        # Print final response.
        if isinstance(message.chat_message, MultiModalMessage):
            final_content = message.chat_message.to_text(iterm=render_image_iterm)
        else:
            final_content = message.chat_message.to_text()
        output = f"{'-' * 10} {message.chat_message.source} {'-' * 10}\n{final_content}\n"
        await aprint(output, end="", flush=True)

        # mypy ignore
        last_processed = message  # type: ignore
    # We don't want to print UserInputRequestedEvent messages, we just use them to signal the user input event.
    elif isinstance(message, UserInputRequestedEvent):
        pass
    else:
        # Cast required for mypy to be happy
        message = cast(BaseAgentEvent | BaseChatMessage, message)  # type: ignore
        if not streaming_chunks:
            # Print message sender.
            await aprint(
                f"{'-' * 10} {message.__class__.__name__} ({message.source}) {'-' * 10}", end="\n", flush=True
            )
        if isinstance(message, ModelClientStreamingChunkEvent):
            await aprint(message.to_text(), end="", flush=True)
            streaming_chunks.append(message.content)
        else:
            if streaming_chunks:
                streaming_chunks.clear()
                # Chunked messages are already printed, so we just print a newline.
                await aprint("", end="\n", flush=True)
            elif isinstance(message, MultiModalMessage):
                await aprint(message.to_text(iterm=render_image_iterm), end="\n", flush=True)
            else:
                await aprint(message.to_text(), end="\n", flush=True)