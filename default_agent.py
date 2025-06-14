class DefaultAgentConfig(BaseModel):
    """Declarative configuration for the DefaultAgent."""

    name: str
    description: str = "default agent"

class DefaultAgent(BaseChatAgent, Component[DefaultAgentConfig]):
    component_type = "agent"
    component_provider_override = "DefaultAgent"
    component_config_schema = DefaultAgentConfig

    def __init__(
        self,
        name: str,
        *,
        description: str = "default agent"
    ) -> None:
        """Initialize the UserProxyAgent."""
        super().__init__(name=name, description=description)

    async def on_messages(self, messages: Sequence[BaseChatMessage], cancellation_token: CancellationToken) -> Response:
        async for message in self.on_messages_stream(messages, cancellation_token):
            if isinstance(message, Response):
                return message
        raise AssertionError("The stream should have returned the final result.")

    async def on_messages_stream(
        self, messages: Sequence[BaseChatMessage], cancellation_token: CancellationToken
    ) -> AsyncGenerator[BaseAgentEvent | BaseChatMessage | Response, None]:
        """Handle incoming messages by requesting user input."""
        try:
            yield Response(chat_message=TextMessage(content="暂不支持此类问题", source=self.name))

        except asyncio.CancelledError:
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to get user input: {str(e)}") from e

    async def on_reset(self, cancellation_token: Optional[CancellationToken] = None) -> None:
        """Reset agent state."""
        pass
