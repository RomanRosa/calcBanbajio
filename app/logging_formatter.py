# app/logging_formatter.py
import logging
import datetime
import pytz

class MexicoCityFormatter(logging.Formatter):
    """
    Formateador de logs que utiliza la zona horaria 'America/Mexico_City'.
    """
    def converter(self, timestamp):
        tz = pytz.timezone("America/Mexico_City")
        dt = datetime.datetime.fromtimestamp(timestamp, tz)
        return dt.timetuple()
