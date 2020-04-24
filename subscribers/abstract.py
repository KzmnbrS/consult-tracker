from __future__ import annotations
from abc import ABC, abstractmethod


class Subscribers(ABC):

    @abstractmethod
    async def list(self, user: int) -> [int] or None:
        """Returns subscriber list of the `user` or `None` if the
        `user` was not found."""

    @abstractmethod
    async def push(self, subscriber: int, user: int) -> bool:
        """Appends the `subscriber` to the `user`s subscriber list.
        If the `user` doesn't have one, it will be created.

        Returns:
            bool: `True` for success, `False` otherwise (e.g. the
                  `subscriber` was already on the list).
        """

    @abstractmethod
    async def remove(self, subscriber: int, user: int) -> bool:
        """Removes the `subscriber` from the `user`s subscriber list.

        Returns:
            bool: `True` for success, `False` otherwise (e.g. the
                  `subscriber` wasn't subscribed to the `user` or
                  the `user` was not found).
        """
