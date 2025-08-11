"""Repository implementations for the notification service."""

from .base_repository import BaseRepository, InMemoryRepository

__all__ = [
    'BaseRepository',
    'InMemoryRepository'
]