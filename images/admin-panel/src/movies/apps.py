from django.apps import AppConfig


class MoviesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'movies'

    def ready(self) -> None:
        """
        Метод вызывается при готовности приложения.
        Здесь регистрируем сигналы.
        """
        import movies.signals  # noqa
