import enum


class ProductStatusEnum(enum.IntEnum):
    AVAILABLE = 1
    ARCHIVED = 2

    @classmethod
    def choices(cls) -> list[tuple[int, str]]:
        return [
            (cls.AVAILABLE, "Доступен для продажи"),
            (cls.ARCHIVED, "Архивный товар"),
        ]
