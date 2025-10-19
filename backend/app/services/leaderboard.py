from typing import List, Dict, Optional
import redis.asyncio as redis
from fastapi import Depends
import json

from app.core.config import settings


class Leaderboard:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        
        # Overall leaderboard -> ZSET (sorted set)
        self.LEADERBOARD_KEY = "leaderboard:{competition_id}"
        
        # PNL for each security -> HSET (hash set)
        self.USER_PNL_KEY = "user_pnl:{competition_id}:{user_id}"
        
        # Holdings for each security -> HSET (hash set)
        self.USER_HOLDINGS_KEY = "user_holdings:{competition_id}:{user_id}"

    # First key function (should be updated by price engine)
    async def update_user_pnl(
        self,
        competition_id: str,
        user_id: str,
        security_id: str,
        pnl: float
    ) -> None:
        pnl_key = self.USER_PNL_KEY.format(competition_id=competition_id, user_id=user_id)
        
        # 1. get users holding of that particular security
        holdings = self.get_user_holding(competition_id, user_id, security_id)
        
        # 2. set PNL based on individual security PNL * user's holding
        total_pnl_for_security = holdings * pnl
        await self.redis.hset(pnl_key, security_id, total_pnl_for_security)
        
        # 3. recalculate total PNL per user and update ZSET
        total_pnl = await self._calculate_total_pnl(pnl_key)
        leaderboard_key = self.LEADERBOARD_KEY.format(competition_id=competition_id)
        await self.redis.zadd(leaderboard_key, {user_id: total_pnl})

    # Second key function (updated by request from FE)
    async def update_user_holding(
        self,
        competition_id: str,
        user_id: str,
        security_id: str,
        quantity: float
    ) -> None:
        holdings_key = self.USER_HOLDINGS_KEY.format(competition_id=competition_id, user_id=user_id)
        if quantity == 0:
            await self.redis.hdel(holdings_key, security_id)
        else:
            await self.redis.hset(holdings_key, security_id, quantity)
    
    # Third key function (should be requested by FE)
    async def get_leaderboard(
        self,
        competition_id: str,
        limit: int = 100
    ) -> List[Dict[str, float]]:
        leaderboard_key = self.LEADERBOARD_KEY.format(competition_id=competition_id)
        
        # ZREVRANGE to get descending based on scores
        leaderboard = await self.redis.zrevrange(
            leaderboard_key, 0, limit - 1, withscores=True
        )
        return [
            {"user_id": user_id.decode(), "pnl": float(score)}
            for user_id, score in leaderboard
        ]

    async def get_user_rank(
        self,
        competition_id: str,
        user_id: str
    ) -> Optional[int]:
        leaderboard_key = self.LEADERBOARD_KEY.format(competition_id=competition_id)
        rank = await self.redis.zrevrank(leaderboard_key, user_id)
        return rank + 1 if rank is not None else None

    async def _calculate_total_pnl(self, pnl_key: str) -> float:
        pnl_values = await self.redis.hvals(pnl_key)
        return sum(float(value) for value in pnl_values) if pnl_values else 0.0


    async def get_user_holdings(
        self,
        competition_id: str,
        user_id: str
    ) -> Dict[str, float]:
        holdings_key = self.USER_HOLDINGS_KEY.format(competition_id=competition_id, user_id=user_id)
        holdings = await self.redis.hgetall(holdings_key)
        return {k.decode(): float(v) for k, v in holdings.items()}

    async def get_user_holding(
        self,
        competition_id: str,
        user_id: str,
        security_id: str
    ) -> float:
        holdings_key = self.USER_HOLDINGS_KEY.format(competition_id=competition_id, user_id=user_id)
        value = await self.redis.hget(holdings_key, security_id)
        return float(value) if value else 0.0

    # Used later
    async def clear_competition_data(self, competition_id: str) -> None:
        leaderboard_key = self.LEADERBOARD_KEY.format(competition_id=competition_id)
        await self.redis.delete(leaderboard_key)
        pattern_pnl = self.USER_PNL_KEY.format(competition_id=competition_id, user_id="*")
        await self._delete_matching_keys(pattern_pnl)
        pattern_holdings = self.USER_HOLDINGS_KEY.format(competition_id=competition_id, user_id="*")
        await self._delete_matching_keys(pattern_holdings)

    # Used later
    async def _delete_matching_keys(self, pattern: str) -> None:
        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                await self.redis.delete(*keys)
            if cursor == 0:
                break
