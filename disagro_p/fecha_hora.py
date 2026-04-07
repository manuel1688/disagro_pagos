import datetime 
from datetime import date
from typing import Optional
import pytz


def obtener_fecha_hora():
    """DEPRECATED: Use get_user_datetime() instead for timezone-aware operations."""
    current_time = datetime.datetime.now()
    return str(current_time.year) + "-" + str(current_time.month) + "-" + str(current_time.day) + " " + str(current_time.hour)+":"+str(current_time.minute)+":"+str(current_time.second)


def obtener_fecha():
    """DEPRECATED: Use get_user_date() instead for timezone-aware operations."""
    current_time = datetime.datetime.now()
    return str(current_time.year) + "-" + str(current_time.month) + "-" + str(current_time.day)


def obtener_hora():
    """DEPRECATED: Use get_user_time() instead for timezone-aware operations."""
    current_time = datetime.datetime.now()
    return str(current_time.hour)+":"+str(current_time.minute)+":"+str(current_time.second)


def parse_timezone_from_request(data: dict, fallback: str = 'America/Guatemala') -> str:
    """
    Extrae la zona horaria del payload del request.
    
    Args:
        data: Diccionario con los datos del request (puede ser json_data o form data parseado)
        fallback: Zona horaria por defecto si no se encuentra en el request
    
    Returns:
        String con la zona horaria en formato IANA (ej: 'America/Guatemala')
    """
    timezone_str = data.get('TIMEZONE', '').strip() if data else ''
    
    # Validar que la zona horaria sea válida
    if timezone_str:
        try:
            pytz.timezone(timezone_str)
            return timezone_str
        except pytz.exceptions.UnknownTimeZoneError:
            # Si la zona horaria no es válida, usar fallback
            pass
    
    return fallback


def get_user_datetime(timezone_str: str = 'America/Guatemala') -> datetime.datetime:
    """
    Obtiene la fecha y hora actual en la zona horaria especificada.
    
    Args:
        timezone_str: Zona horaria en formato IANA (ej: 'America/Guatemala', 'America/New_York')
    
    Returns:
        datetime con la fecha y hora actual en la zona horaria especificada (timezone-aware)
    """
    try:
        tz = pytz.timezone(timezone_str)
    except pytz.exceptions.UnknownTimeZoneError:
        # Si la zona horaria no es válida, usar Guatemala como fallback
        tz = pytz.timezone('America/Guatemala')
    
    # Obtener la hora UTC actual y convertir a la zona horaria del usuario
    utc_now = datetime.datetime.now(pytz.UTC)
    return utc_now.astimezone(tz)


def get_user_date(timezone_str: str = 'America/Guatemala') -> date:
    """
    Obtiene la fecha actual en la zona horaria especificada.
    
    Args:
        timezone_str: Zona horaria en formato IANA (ej: 'America/Guatemala', 'America/New_York')
    
    Returns:
        date con la fecha actual en la zona horaria especificada
    """
    user_datetime = get_user_datetime(timezone_str)
    return user_datetime.date()


def get_user_time(timezone_str: str = 'America/Guatemala') -> datetime.time:
    """
    Obtiene la hora actual en la zona horaria especificada.
    
    Args:
        timezone_str: Zona horaria en formato IANA (ej: 'America/Guatemala', 'America/New_York')
    
    Returns:
        time con la hora actual en la zona horaria especificada
    """
    user_datetime = get_user_datetime(timezone_str)
    return user_datetime.time()

