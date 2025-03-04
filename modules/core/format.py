def format_number(value):
    """Formats a number to display as K (thousands) or M (millions)."""
    if value >= 1_000_000:  # Millions
        return f"{value / 1_000_000:.2f}M"  # Example: 1531352 → 1.53M
    elif value >= 1_000:  # Thousands
        return f"{value / 1_000:.0f}K"  # Example: 995000 → 995K
    return str(value)  # Below 1000, keep as-is
