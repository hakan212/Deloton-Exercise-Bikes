def calculate_max_heart_rate (age: int):
## Calculates maximum heart rate given age
    if age <=40:
        return 211 - (0.64 * age)
    else:
        return 208 - (0.7 * age)

def check_if_heart_rate_abnormal (current_heart_rate: int, max_heart_rate:int):
## Returns true if current heart rate is abnormal
    upper_limit = 0.9 * max_heart_rate
    lower_limit = 0.5 * max_heart_rate

    if lower_limit <= current_heart_rate <= max_heart_rate:
        return False
    else:
        return True