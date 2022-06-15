from datetime import datetime
from django.utils import timezone


def year(request):
    dt = datetime.now().year
    now = timezone.now()
    return {
        'year': dt,
        'now': now
    }
