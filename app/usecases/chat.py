from app.db.models import ChatMessage
from app.repositories.chat_messages import ChatMessageRepository
from app.services.openrouter_client import OpenRouterClient


class ChatUseCase:
    def __init__(
        self,
        chat_repo: ChatMessageRepository,
        openrouter_client: OpenRouterClient,
    ):
        self._chat_repo = chat_repo
        self._openrouter_client = openrouter_client

    async def ask(
        self,
        user_id: int,
        prompt: str,
        system: str | None,
        max_history: int,
        temperature: float,
    ) -> str:
        messages: list[dict[str, str]] = []

        if system:
            messages.append({"role": "system", "content": system})

        history = await self._chat_repo.get_last_messages(
            user_id=user_id,
            limit=max_history,
        )

        for message in history:
            messages.append(
                {
                    "role": message.role,
                    "content": message.content,
                },
            )

        messages.append({"role": "user", "content": prompt})

        await self._chat_repo.add(
            user_id=user_id,
            role="user",
            content=prompt,
        )

        answer = await self._openrouter_client.chat_completion(
            messages=messages,
            temperature=temperature,
        )

        await self._chat_repo.add(
            user_id=user_id,
            role="assistant",
            content=answer,
        )

        return answer

    async def get_history(self, user_id: int) -> list[ChatMessage]:
        return await self._chat_repo.get_last_messages(
            user_id=user_id,
            limit=100,
        )

    async def delete_history(self, user_id: int) -> None:
        await self._chat_repo.delete_all(user_id)
