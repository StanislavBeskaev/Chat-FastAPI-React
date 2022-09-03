from dataclasses import dataclass


class DocResponseExample:
    """Пример ответа API для документации"""

    def __init__(self, description: str, example: dict | list):
        self._description = description
        self._example = example

    def to_openapi(self) -> dict:
        """Преобразование к формату openapi/swagger для отображения в документации"""
        openapi_response_example = {
            "description": self._description,
            "content": {
                "application/json": {
                    "example": self._example
                }
            }
        }

        return openapi_response_example


@dataclass
class StatusCodeDocResponseExample:
    """Пример ответа API по статус коду"""
    status_code: int
    response_example: DocResponseExample


class DocResponses:
    """Ответы API для документации"""

    def __init__(self, responses: list[StatusCodeDocResponseExample]):
        self._responses = responses

    def to_openapi(self) -> dict[int, dict]:
        """Преобразование к формату openapi/swagger для отображения в документации"""
        openapi_responses = {
            status_code_response.status_code: status_code_response.response_example.to_openapi()
            for status_code_response in self._responses
        }

        return openapi_responses
