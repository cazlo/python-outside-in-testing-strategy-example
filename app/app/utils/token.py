from datetime import timedelta
from typing import List
from uuid import UUID
from redis.asyncio import Redis
from app.models.user_model import User
from app.schemas.common_schema import TokenType


async def add_token_to_redis(
    redis_client: Redis,
    user: User,
    token: str,
    token_type: TokenType,
    expire_time: int | None = None,
):
    token_key = f"user:{user.id}:{token_type}"
    await redis_client.sadd(token_key, token)
    await redis_client.expire(token_key, timedelta(minutes=expire_time))


async def is_valid_token(
    redis_client: Redis, user_id: UUID, token_type: TokenType, token: str
):
    token_key = f"user:{user_id}:{token_type}"
    is_valid = await redis_client.sismember(token_key, token)
    return is_valid


async def get_valid_tokens(redis_client: Redis, user_id: UUID, token_type: TokenType):
    token_key = f"user:{user_id}:{token_type}"
    valid_tokens = await redis_client.smembers(token_key)
    return valid_tokens


async def delete_tokens(redis_client: Redis, user: User, token_types: List[TokenType]):
    token_keys = [f"user:{user.id}:{token_type}" for token_type in token_types]
    await redis_client.delete(*token_keys)
