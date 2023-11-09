

def clamp(value, minimum, maximum):
    if value <= minimum:
        return minimum
    if value >= maximum:
        return maximum
    return value
