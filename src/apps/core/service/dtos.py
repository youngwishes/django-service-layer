import abc
from dataclasses import asdict


class BaseServiceDTO(abc.ABC):
    def asdict(self) -> dict:
        return asdict(self)
