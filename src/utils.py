from datetime import datetime, timedelta


def time(delta=+3) -> str:
    local_time = datetime.now()
    moscow_time = local_time + timedelta(hours=delta)
    return str(moscow_time)[:-4]
