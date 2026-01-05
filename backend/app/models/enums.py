"""Enumerations for Phase 2D - Multi-Market Support"""

from enum import Enum


class ExchangeEnum(str, Enum):
    """Supported stock exchanges"""
    NYSE = "NYSE"
    NASDAQ = "NASDAQ"
    NSE = "NSE"
    BSE = "BSE"


class CountryEnum(str, Enum):
    """Supported countries"""
    US = "US"
    IN = "IN"


class CurrencyEnum(str, Enum):
    """Supported currencies"""
    USD = "USD"
    INR = "INR"


class MarketStatusEnum(str, Enum):
    """Market operational status"""
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    PRE_MARKET = "PRE_MARKET"
    AFTER_HOURS = "AFTER_HOURS"
