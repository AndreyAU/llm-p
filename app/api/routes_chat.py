from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import (
    get_auth_usecase,
    get_chat_usecase,
    get_current_user_id,
)
from app.core.errors import AppError, ExternalServiceError
from app.schemas.chat import (
    ChatHistoryDeleteResponse,
    ChatMessagePublic,
    ChatRequest,
    ChatResponse,
)
from app.usecases.auth import AuthUseCase
from app.usecases.chat import ChatUseCase

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    chat_usecase: ChatUseCase = Depends(get_chat_usecase),
) -> ChatResponse:
    try:
        answer = await chat_usecase.ask(
            user_id=user_id,
            prompt=request.prompt,
            system=request.system,
            max_history=request.max_history,
            temperature=request.temperature,
        )
    except ExternalServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=exc.message,
        ) from exc

    return ChatResponse(answer=answer)


@router.get("/history", response_model=list[ChatMessagePublic])
async def get_history(
    user_id: int = Depends(get_current_user_id),
    chat_usecase: ChatUseCase = Depends(get_chat_usecase),
) -> list[ChatMessagePublic]:
    try:
        messages = await chat_usecase.get_history(user_id)
        return [ChatMessagePublic.model_validate(message) for message in messages]
    except AppError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.message,
        ) from exc


@router.delete("/history", response_model=ChatHistoryDeleteResponse)
async def delete_history(
    user_id: int = Depends(get_current_user_id),
    chat_usecase: ChatUseCase = Depends(get_chat_usecase),
    auth_usecase: AuthUseCase = Depends(get_auth_usecase),
) -> ChatHistoryDeleteResponse:
    try:
        user = await auth_usecase.get_user(user_id)
        await chat_usecase.delete_history(user_id)
    except AppError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.message,
        ) from exc

    return ChatHistoryDeleteResponse(
        email=user.email,
        detail="Chat history deleted",
    )
