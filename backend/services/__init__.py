from abc import ABC

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.database import get_session


class BaseService(ABC):
    """Базовый сервис"""
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session
