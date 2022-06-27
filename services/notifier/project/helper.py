from pytz import timezone, utc


def convert_timezone(value, tzfrom="UTC", tzto="Europe/Brussels", format="%Y-%m-%d %H:%M:%S.%f"):
    """Converts a given datetime into another given timezone datetime"""
    tz = timezone(tzto)
    u = timezone(tzfrom)
    value = u.localize(value, is_dst=None).astimezone(utc)
    local_dt = value.astimezone(tz)
    return local_dt.strftime(format)