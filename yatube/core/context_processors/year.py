from django.utils import timezone


def year(request):
    """Выводит текущий год."""
    return {
        'year': int(timezone.now().strftime('%Y'))
    }
