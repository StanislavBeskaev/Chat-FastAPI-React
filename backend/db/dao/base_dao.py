from abc import ABC

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.db_config import get_session


class BaseDAO(ABC):
    """Базовый DAO для общения с базой"""
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session
