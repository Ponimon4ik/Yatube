import datetime as dt

now = dt.datetime.today()
year_now = int(now.strftime("%Y"))


def year(request):
    """Добавляет переменную с текущим годом."""
    return {
        'year': year_now,
    }
