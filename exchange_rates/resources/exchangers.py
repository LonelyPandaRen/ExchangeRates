from enum import StrEnum, unique


@unique
class Exchangers(StrEnum):
    BINANCE = "binance"
    COIN_GECKO = "coin_gecko"
