from enum import StrEnum, unique


@unique
class Directions(StrEnum):
    BTC_USD = "BTC-USD"
    ETH_USD = "ETH-USD"
