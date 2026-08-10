"""CP3 — Cost guard: chặn chi phí trước khi hóa đơn chặn bạn.

Rate limit giới hạn *số lượng* request. Cost guard giới hạn *số tiền*: một
user gửi 10 request/phút nhưng mỗi request 50k token vẫn đốt sạch ngân sách.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status

# Giữ dữ liệu chi tiêu thêm ~40 ngày để còn đối soát sang tháng sau
KEY_TTL_SECONDS = 40 * 24 * 3600


class CostGuard:
    def __init__(self, client, monthly_budget_usd: float) -> None:
        self.client = client
        self.budget = monthly_budget_usd

    @staticmethod
    def current_month() -> str:
        """CHO SẴN — nhãn tháng hiện tại dạng '2026-08' (UTC)."""
        return datetime.now(timezone.utc).strftime("%Y-%m")

    @classmethod
    def _key(cls, user_id: str, month: str | None = None) -> str:
        """CHO SẴN — khóa Redis theo từng user, từng tháng."""
        return f"cost:{user_id}:{month or cls.current_month()}"

    def spent(self, user_id: str, month: str | None = None) -> float:
        val = self.client.get(self._key(user_id, month))
        return float(val) if val is not None else 0.0

    def check(
        self,
        user_id: str,
        estimated_cost: float = 0.0,
        month: str | None = None,
    ) -> None:
        if self.spent(user_id, month) + estimated_cost > self.budget:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="monthly budget exceeded",
            )

    def record(self, user_id: str, cost: float, month: str | None = None) -> float:
        key = self._key(user_id, month)
        total = self.client.incrbyfloat(key, cost)
        self.client.expire(key, KEY_TTL_SECONDS)
        return float(total)
