import subprocess
import psycopg2
from psycopg2 import sql
import argparse
import os

#ты котик

def check_db_connection(dbname, user, password, host='localhost', port=5432):
    """Проверяет подключение к БД."""
    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        conn.close()
        print(f"Подключение к БД '{dbname}' успешно.")
        return True
    except psycopg2.Error as e:
        print(f"Ошибка подключения: {e}")
        return False


def backup_db(dbname, user, password, backup_file, host='localhost', port=5432):
    """Делает бэкап БД с помощью pg_dump."""
    if not check_db_connection(dbname, user, password, host, port):
        return

    env = os.environ.copy()
    env['PGPASSWORD'] = password  # Чтобы избежать ввода пароля в терминале

    command = [
        'pg_dump',
        '-h', host,
        '-p', str(port),
        '-U', user,
        '-F', 'c',  # Формат custom (бинарный, сжатый)
        '-b',  # Включая большие объекты
        '-v',  # Verbose
        '-f', backup_file,
        dbname
    ]

    try:
        subprocess.run(command, check=True, env=env)
        print(f"Бэкап сохранён в файл: {backup_file}")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка бэкапа: {e}")


def restore_db(dbname, user, password, backup_file, host='localhost', port=5432):
    """Восстанавливает БД из бэкапа с помощью pg_restore."""
    # Сначала создаём пустую БД, если она не существует
    try:
        conn = psycopg2.connect(dbname='postgres', user=user, password=password, host=host, port=port)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(dbname)))
        cur.close()
        conn.close()
        print(f"БД '{dbname}' создана.")
    except psycopg2.Error as e:
        if 'already exists' in str(e):
            print(f"БД '{dbname}' уже существует. Продолжаем восстановление.")
        else:
            print(f"Ошибка создания БД: {e}")
            return

    env = os.environ.copy()
    env['PGPASSWORD'] = password

    command = [
        'pg_restore',
        '-h', host,
        '-p', str(port),
        '-U', user,
        '-d', dbname,
        '-v',  # Verbose
        backup_file
    ]

    try:
        subprocess.run(command, check=True, env=env)
        print(f"Восстановление из '{backup_file}' завершено в БД '{dbname}'.")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка восстановления: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Утилита для бэкапа и восстановления PostgreSQL БД.")
    parser.add_argument('--action', choices=['backup', 'restore'], required=True, help="Действие: backup или restore")
    parser.add_argument('--dbname', required=True, help="Имя базы данных")
    parser.add_argument('--user', required=True, help="Пользователь БД")
    parser.add_argument('--password', required=True, help="Пароль БД")
    parser.add_argument('--host', default='localhost', help="Хост БД (по умолчанию: localhost)")
    parser.add_argument('--port', default=5432, type=int, help="Порт БД (по умолчанию: 5432)")
    parser.add_argument('--file', required=True,
                        help="Файл бэкапа (для backup — куда сохранить, для restore — откуда взять)")

    args = parser.parse_args()

    if args.action == 'backup':
        backup_db(args.dbname, args.user, args.password, args.file, args.host, args.port)
    elif args.action == 'restore':
        restore_db(args.dbname, args.user, args.password, args.file, args.host, args.port)