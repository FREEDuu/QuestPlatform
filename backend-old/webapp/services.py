from django.utils import timezone
from datetime import datetime, date

def reformat_date(input_date):
    if isinstance(input_date, str):
        input_date = datetime.strptime(input_date, '%d-%m-%Y %H:%M') # Esempio: 31-01-2024 15:23

    if isinstance(input_date, date):
        iso_date = timezone.datetime.strftime(input_date, '%Y-%m-%dT%H:%M:%S')
        print(iso_date)
        return iso_date
    else:
        raise ValueError("Tipo di input non supportato per formattazione data")
