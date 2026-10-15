"""Currency utility functions."""
from __future__ import annotations


CURRENCY_SYMBOLS: dict[str, str] = {
    "INR": "₹",
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
}


def format_currency(amount: float, currency: str = "INR") -> str:
    """Format an amount with currency symbol."""
    symbol = CURRENCY_SYMBOLS.get(currency.upper(), currency)
    if currency.upper() == "INR":
        # Indian numbering system
        return f"{symbol}{_format_indian(amount)}"
    return f"{symbol}{amount:,.2f}"


def _format_indian(amount: float) -> str:
    """Format number in Indian numbering system (lakhs, crores)."""
    if amount < 0:
        return "-" + _format_indian(-amount)
    
    integer_part = int(amount)
    decimal_part = amount - integer_part
    
    s = str(integer_part)
    if len(s) <= 3:
        result = s
    else:
        result = s[-3:]
        s = s[:-3]
        while s:
            result = s[-2:] + "," + result
            s = s[:-2]
    
    if decimal_part > 0:
        result += f".{int(decimal_part * 100):02d}"
    
    return result
