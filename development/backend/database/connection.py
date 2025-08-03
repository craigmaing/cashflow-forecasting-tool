"""
Database Connection Management
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
import asyncpg
from asyncpg import Pool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from config import settings

logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    """Base class for all models"""
    pass

class Database:
    """Database management class"""
    
    _pool: Optional[Pool] = None
    _engine = None
    _session_factory = None
    
    @classmethod
    async def connect(cls):
        """Initialize database connections"""
        try:
            # Create asyncpg connection pool
            cls._pool = await asyncpg.create_pool(
                settings.DATABASE_URL,
                min_size=5,
                max_size=settings.DATABASE_POOL_SIZE,
                command_timeout=60
            )
            
            # Create SQLAlchemy async engine
            cls._engine = create_async_engine(
                settings.DATABASE_URL,
                pool_size=settings.DATABASE_POOL_SIZE,
                max_overflow=settings.DATABASE_MAX_OVERFLOW,
                echo=settings.DEBUG
            )
            
            # Create session factory
            cls._session_factory = async_sessionmaker(
                cls._engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            logger.info("Database connections initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            raise
    
    @classmethod
    async def disconnect(cls):
        """Close database connections"""
        try:
            if cls._pool:
                await cls._pool.close()
                cls._pool = None
            
            if cls._engine:
                await cls._engine.dispose()
                cls._engine = None
            
            cls._session_factory = None
            logger.info("Database connections closed")
            
        except Exception as e:
            logger.error(f"Error closing database connections: {str(e)}")
    
    @classmethod
    async def health_check(cls) -> bool:
        """Check database health"""
        try:
            if not cls._pool:
                return False
            
            async with cls._pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True
            
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False
    
    @classmethod
    @asynccontextmanager
    async def get_session(cls):
        """Get database session"""
        if not cls._session_factory:
            raise RuntimeError("Database not initialized")
        
        async with cls._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    @classmethod
    async def execute_raw(cls, query: str, params: Dict[str, Any] = None) -> Any:
        """Execute raw SQL query"""
        if not cls._pool:
            raise RuntimeError("Database not initialized")
        
        async with cls._pool.acquire() as conn:
            if params:
                return await conn.fetch(query, *params.values())
            return await conn.fetch(query)
    
    @classmethod
    def get_timestamp(cls) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
