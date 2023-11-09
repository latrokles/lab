from datetime import datetime

YYYY_MM_DD__hhmm_format = "%Y-%m-%d %H:%M %Z"


def local_now_as_YYYY_mm_dd__HHMM():
    return (
        datetime
        .now()
        .astimezone()
        .strftime(YYYY_MM_DD__hhmm_format)
    )


def local_today_as_YYYY_mm_dd():
    return (
        datetime
        .now()
        .astimezone()
        .strftime('%Y-%m-%d')
    )
