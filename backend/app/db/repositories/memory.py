"""Memory entries database operations."""
from __future__ import annotations

from typing import Any

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import MemoryEntry


class MemoryRepository:
    """Repository for memory entries."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def store(
        self,
        user_id: str,
        key: str,
        value: Any,
        memory_type: str = "workflow",
        run_id: str | None = None,
    ) -> MemoryEntry:
        entry = MemoryEntry(
            user_id=user_id,
            run_id=run_id,
            memory_type=memory_type,
            key=key,
            value=value,
        )
        self.session.add(entry)
        await self.session.commit()
        await self.session.refresh(entry)
        return entry

    async def retrieve(
        self,
        user_id: str,
        key: str,
        memory_type: str | None = None,
    ) -> MemoryEntry | None:
        query = select(MemoryEntry).where(
            MemoryEntry.user_id == user_id,
            MemoryEntry.key == key,
        )
        if memory_type:
            query = query.where(MemoryEntry.memory_type == memory_type)
        query = query.order_by(MemoryEntry.created_at.desc())
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def delete_by_run(self, run_id: str) -> None:
        await self.session.execute(
            delete(MemoryEntry).where(MemoryEntry.run_id == run_id)
        )
        await self.session.commit()
