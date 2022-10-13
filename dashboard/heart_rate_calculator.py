def calculate_max_heart_rate(age: float) -> float:
    """Calculates maximum heart rate given age. 211, 208, 0.64 and 0.7 taken from formulas found in published papers"""
    if age <= 40:
        return 211 - (0.64 * age)
    else:
        return 208 - (0.7 * age)


def heart_rate_low(current_heart_rate: float, age: float) -> bool:
    """Returns true if current heart rate is too low"""
    max_heart_rate = calculate_max_heart_rate(age)
    lower_limit = 0.5 * max_heart_rate

    return current_heart_rate <= lower_limit and current_heart_rate != 0


def heart_rate_high(current_heart_rate: int, age: int) -> bool:
    """Returns true if current heart rate is too high"""
    max_heart_rate = calculate_max_heart_rate(age)
    upper_limit = 0.9 * max_heart_rate

    return current_heart_rate >= upper_limit


def heart_rate_ok(current_heart_rate: int, age: int) -> bool:
    return not (
        heart_rate_high(current_heart_rate, age)
        or heart_rate_low(current_heart_rate, age)
    )
