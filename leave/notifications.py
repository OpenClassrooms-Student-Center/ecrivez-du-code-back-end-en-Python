import unicodedata

from django.core.mail import send_mail

from .models import Employee


class NotificationService:
    """Envoie les notifications par e-mail."""

    def __init__(self) -> None:
        self.failed: list[tuple[Employee, str]] = []

    def notify(self, employee: Employee, message: str) -> None:
        try:
            send_mail(
                subject="Hamac : votre demande de congés",
                message=message,
                from_email=None,
                recipient_list=[self._address(employee)],
            )
        except OSError:
            self.failed.append((employee, message))

    def send_weekly_summary(self, managers: list[Employee]) -> None:
        for manager in managers:
            send_mail(
                subject="Hamac : récapitulatif hebdomadaire",
                message="Voici les demandes de congés de la semaine.",
                from_email=None,
                recipient_list=[self._address(manager)],
            )

    def retry_failed_notifications(self) -> None:
        pending, self.failed = self.failed, []
        for employee, message in pending:
            self.notify(employee, message)

    @staticmethod
    def _address(employee: Employee) -> str:
        name = f"{employee.first_name}.{employee.last_name}".lower()
        ascii_name = (
            unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
        )
        return f"{ascii_name}@example.com"
