from django import template

register = template.Library()

@register.filter
def currency_format(value):
    """
    Форматирует число как валюту: пробелы для тысяч, запятая для копеек
    Всегда показывает 2 знака после запятой
    100000 -> 100 000,00 ₽
    100000.5 -> 100 000,50 ₽
    400400.00 -> 400 400,00 ₽
    """
    if value is None or value == '':
        return '0,00 ₽'
    
    try:
        # Преобразуем в float и округляем до 2 знаков
        value = float(value)
        value = round(value, 2)
        
        # Разделяем на рубли и копейки
        total_cents = int(value * 100)
        rubles = total_cents // 100
        kopecks = total_cents % 100
        
        # Форматируем рубли с пробелами между тысячами
        formatted_rubles = '{:,}'.format(rubles).replace(',', ' ')
        
        # Всегда показываем 2 знака копеек
        return f"{formatted_rubles},{kopecks:02d} ₽"
            
    except (ValueError, TypeError):
        return str(value)

@register.filter
def currency_format_strict(value):
    """
    Тот же фильтр, но всегда показывает копейки
    """
    return currency_format(value)