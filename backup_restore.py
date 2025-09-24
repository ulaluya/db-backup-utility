import argparse
import os
import shutil
from datetime import datetime


def backup_db(db_path, backup_file):
    if not os.path.exists(db_path):
        print(f"Ошибка: база данных {db_path} не существует.")
        return

    backup_dir = os.path.dirname(backup_file) or "."
    os.makedirs(backup_dir, exist_ok=True)

    shutil.copy2(db_path, backup_file)
    print(f"Бэкап сохранён в файл: {backup_file}")


def restore_db(db_path, backup_file):
    if not os.path.exists(backup_file):
        print(f"Ошибка: файл бэкапа {backup_file} не существует.")
        return

    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Существующая база {db_path} удалена.")

    shutil.copy2(backup_file, db_path)
    print(f"Восстановление из {backup_file} завершено в {db_path}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Утилита для бэкапа и восстановления SQLite базы данных.")
    parser.add_argument('--action', choices=['backup', 'restore'], required=True, help="Действие: backup или restore")
    parser.add_argument('--dbpath', required=True, help="Путь к файлу базы данных SQLite (например, database.db)")
    parser.add_argument('--file', required=True,
                        help="Файл бэкапа (для backup — куда сохранить, для restore — откуда взять)")

    args = parser.parse_args()

    if args.action == 'backup':
        backup_db(args.dbpath, args.file)
    elif args.action == 'restore':
        restore_db(args.dbpath, args.file)
