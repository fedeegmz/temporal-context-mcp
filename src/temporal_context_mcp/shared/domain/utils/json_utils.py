import json
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def load_models_from_json_file[T](file_path: str, model_class: type[T]) -> list[T]:
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)
        return [model_class.model_validate(item) for item in data]


def save_models_to_json_file(file_path: str, data: list[BaseModel]) -> None:
    json_data = [model.model_dump(mode="json") for model in data]
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False, default=str)
