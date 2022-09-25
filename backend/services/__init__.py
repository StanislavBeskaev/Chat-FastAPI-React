from abc import ABC

from fastapi import Depends

from backend.db.facade import get_db_facade
from backend.db.interface import DBFacadeInterface


class BaseService(ABC):
    """Базовый сервис"""
    def __init__(self, db_facade: DBFacadeInterface = Depends(get_db_facade)):
        self._db_facade = db_facade
