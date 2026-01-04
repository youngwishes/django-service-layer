"""
Генератор тестовых запросов для наполнения Kibana логами.

Скрипт отправляет различные типы ошибочных запросов к API
для создания реалистичных логов в системе мониторинга.
"""

import os
import random
import time

import requests
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL")


class UserToken:
    FULL_VALID = os.getenv("FULL_VALID_USER_TOKEN")
    NOT_ENOUGH_BALANCE = os.getenv("NOT_ENOUGH_BALANCE_USER_TOKEN")


class ProductId:
    FULL_VALID = 1
    OUT_OF_STOCK = 2
    ARCHIVED = 3
    NOT_FOUND = 100


def make_request(token: str, product: int, count: int = 1) -> None:
    requests.post(
        API_URL,
        json={
            "id": product,
            "count": count,
        },
        headers={"Authorization": f"Token {token}"},
    )
    time.sleep(0.1)


def populate() -> None:
    for _ in range(random.randint(0, 15)):
        make_request(
            UserToken.FULL_VALID,
            ProductId.OUT_OF_STOCK,
        )

    for _ in range(random.randint(0, 15)):
        make_request(
            UserToken.FULL_VALID,
            ProductId.NOT_FOUND,
        )

    for _ in range(random.randint(0, 15)):
        make_request(
            UserToken.FULL_VALID,
            ProductId.ARCHIVED,
        )

    for _ in range(random.randint(0, 15)):
        make_request(
            UserToken.NOT_ENOUGH_BALANCE,
            ProductId.FULL_VALID,
        )


def main(iterations: int) -> None:
    for _ in range(iterations):
        populate()


if __name__ == "__main__":
    main(iterations=10)
