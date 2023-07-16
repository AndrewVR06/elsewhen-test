from enum import StrEnum
from functools import cache


class Metals(StrEnum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    CATASTROPHIC = "catastrophic"

    @staticmethod
    @cache
    def get_values():
        return list(Metals.__members__.values())
