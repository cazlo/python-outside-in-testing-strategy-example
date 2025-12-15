from typing import Any, Dict, Generic, Optional, Type, TypeVar, Union
from uuid import UUID
from fastapi import HTTPException, status
from sqlmodel import SQLModel

ModelType = TypeVar("ModelType", bound=SQLModel)


class IdNotFoundException(HTTPException, Generic[ModelType]):
    def __init__(
        self,
        model: Type[ModelType],
        id: Optional[Union[UUID, str]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        if id:
            super().__init__(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Unable to find the {model.__name__} with id {id}.",
                headers=headers,
            )
            return

        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model.__name__} id not found.",
            headers=headers,
        )
