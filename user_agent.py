from autogen_agentchat.agents import UserProxyAgent
import asyncio
from inspect import iscoroutinefunction
from typing import Optional, cast

from autogen_agentchat.agents._user_proxy_agent import InputFuncType, cancellable_input, AsyncInputFunc, SyncInputFunc
from autogen_core import CancellationToken


class UserAgentC(UserProxyAgent):
    def __init__(
        self,
        name: str,
        *,
        description: str = "A human user",
        input_func: Optional[InputFuncType] = None,
        output_func = None,
    ) -> None:
        """Initialize the UserProxyAgent."""
        super().__init__(name=name, description=description)
        self.input_func = input_func or cancellable_input
        self.output_func = output_func
        self._is_async = iscoroutinefunction(self.input_func)

    async def _get_input(self, prompt: str, cancellation_token: Optional[CancellationToken]) -> str:
        """Handle input based on function signature."""
        try:
            if self._is_async:
                # Cast to AsyncInputFunc for proper typing
                async_func = cast(AsyncInputFunc, self.input_func)
                await self.output_func(prompt)
                return await async_func()
            else:
                # Cast to SyncInputFunc for proper typing
                sync_func = cast(SyncInputFunc, self.input_func)
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, sync_func, prompt)

        except asyncio.CancelledError:
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to get user input: {str(e)}") from e