

def clamp(value, minimum, maximum):
    if value <= minimum:
        return minimum
    if value >= maximum:
        return maximum
    return value


def if_else(cond, iftrue, iffalse):
    if cond:
        return iftrue
    return iffalse
