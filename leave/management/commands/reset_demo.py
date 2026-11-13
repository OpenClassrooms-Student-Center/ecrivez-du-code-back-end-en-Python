import calendar
from datetime import date, timedelta

from django.core.management import call_command
from django.core.management.base import BaseCommand

from leave.models import Employee


def months_before(day: date, months: int) -> date:
    month_index = day.year * 12 + day.month - 1 - months
    year, month = divmod(month_index, 12)
    month += 1
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, min(day.day, last_day))


class Command(BaseCommand):
    help = "Vide la base, puis charge le jeu de données de démonstration."

    def handle(self, *args, **options):
        call_command("flush", interactive=False, verbosity=0)
        call_command("loaddata", "demo", verbosity=0)

        # Leïla Haddad (CDD) : entrée il y a 7 mois et 5 jours,
        # quelle que soit la date du jour.
        today = date.today()
        Employee.objects.filter(pk=4).update(
            hire_date=months_before(today, 7) - timedelta(days=5)
        )

        # Zoé Mendes (stage) : arrive dans 7 jours, quelle que soit la date du jour.
        Employee.objects.filter(pk=6).update(hire_date=date.today() + timedelta(days=7))

        self.stdout.write(self.style.SUCCESS("Jeu de démonstration chargé."))
