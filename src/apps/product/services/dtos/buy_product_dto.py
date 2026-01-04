from dataclasses import dataclass

from apps.core.service import BaseServiceDTO


@dataclass(kw_only=True, frozen=True, slots=True)
class BuyProductIn(BaseServiceDTO):
    id: int
    count: int


@dataclass(kw_only=True, frozen=True, slots=True)
class BuyProductOut(BaseServiceDTO):
    product: int
    count: int
    balance: float
