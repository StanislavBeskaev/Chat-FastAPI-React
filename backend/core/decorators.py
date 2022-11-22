from functools import wraps
from typing import Callable, Type, TypeVar

Model = TypeVar("Model")
Result = Model | list[Model] | None


def model_result(model: Type[Model]) -> Callable[[Callable[..., Result]], Callable[..., Result]]:
    """
    Декоратор для преобразования результата функции в объект/объекты модели
    pydantic(для модели должен быть включён orm_mode):
        - Если результат функции None, то None
        - Если результат функции список, то преобразование к списку объектов указанной модели
        - Иначе преобразование к объекту указанной модели
    """

    @wraps(model)
    def decorator(function: Callable[..., Result]):
        @wraps(function)
        def wrapper(*args, **kwargs) -> Result:
            result = function(*args, **kwargs)
            if result is None:
                return result

            if isinstance(result, list):
                return [model.from_orm(obj) for obj in result]

            return model.from_orm(result)

        return wrapper

    return decorator
