from django.core.management.base import BaseCommand
from environs import Env


def main() -> None:
    """основная логика"""
    env = Env()
    env.read_env()

    token = env.str('TG_TOKEN')
    channel_id = env.str('BOT_ID')
    print(token, channel_id)


if __name__ == '__main__':
    """для тестов из скрипта"""
    main()


class Command(BaseCommand):
    """запускается из django manage"""
    help = 'Telegramm bot'

    def handle(self, *args, **options):
        main()
