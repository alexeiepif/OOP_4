#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Выполнить индивидуальное задание 1 лабораторной работы 2.19,
# добавив возможность работы с исключениями и логгирование.
# Изучить возможности модуля logging. Добавить для предыдущего задания
# вывод в файлы лога даты и времени выполнения пользовательской команды
# с точностью до миллисекунды.

import argparse
import bisect
import json
import logging
import os
import sys
import traceback
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List, NoReturn

from jsonschema import ValidationError, validate


class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise argparse.ArgumentError(None, message)


# Класс пользовательского исключения в случае, если введенный маршрут
# уже существует.
class RouteExistsError(Exception):
    def __init__(
        self, route: "Route", message: str = "Route already exists"
    ) -> None:
        self.route = route
        self.message = message
        super(RouteExistsError, self).__init__(message)

    def __str__(self) -> str:
        return f"{self.route} -> {self.message}"


# Класс пользовательского исключения в случае, если для команд
# вывода маршрутов использовался несуществующий файл
class FileNotExistsError(Exception):
    def __init__(
        self, file_path: Path, message: str = "File not exists"
    ) -> None:
        self.file_path = file_path
        self.message = message
        super(FileNotExistsError, self).__init__(message)

    def __str__(self) -> str:
        return f"{self.file_path} -> {self.message}"


@dataclass(frozen=True)
class Route:
    start: str
    end: str
    number: int


@dataclass
class Routes:
    routes: List[Route] = field(default_factory=list)

    def add(self, start: str, end: str, number: int) -> None:
        """
        Добавить данные о маршруте.
        """
        route = Route(
            start.lower(),
            end.lower(),
            number,
        )
        if route not in self.routes:
            bisect.insort(
                self.routes,
                route,
                key=lambda item: item.number,
            )
        else:
            raise RouteExistsError(route)

    def __str__(self) -> str:
        """
        Отобразить список маршрутов.
        """
        if self.routes:
            table = []
            line = "+-{}-+-{}-+-{}-+-{}-+".format(
                "-" * 4, "-" * 30, "-" * 20, "-" * 16
            )
            table.append(line)
            table.append(
                "| {:^4} | {:^30} | {:^20} | {:^16} |".format(
                    "No", "Начало", "Конец", "Номер маршрута"
                )
            )
            table.append(line)
            for idx, route in enumerate(self.routes, 1):
                table.append(
                    "| {:^4} | {:<30} | {:<20} | {:>16} |".format(
                        idx, route.start, route.end, route.number
                    )
                )
            table.append(line)
            return "\n".join(table)
        else:
            return "Список маршрутов пуст."

    def __len__(self) -> int:
        return len(self.routes)

    def select(self, name_point: str) -> "Routes":
        """
        Выбрать маршруты с заданным пунктом отправления или прибытия.
        """
        selected: List[Route] = field(default_factory=list)
        for route in self.routes:
            if route.start == name_point or route.end == name_point:
                selected.append(route)

        return Routes(selected)

    def save(self, file_path: Path) -> None:
        """
        Сохранить все маршруты в файл JSON.
        """
        # Открыть файл с заданным именем для записи.
        with file_path.open("w") as file_out:
            data_with_type = [
                {"__type__": route.__class__.__name__, **asdict(route)}
                for route in self.routes
            ]
            # Записать данные из словаря в формат JSON и сохранить их
            # в открытый файл.
            json.dump(data_with_type, file_out, ensure_ascii=False, indent=4)

    def load(self, file_path: Path) -> None:
        """
        Загрузить все маршруты из файла JSON.
        """
        schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "__type__": {"type": "string", "enum": ["Route"]},
                    "start": {"type": "string"},
                    "end": {"type": "string"},
                    "number": {"type": "integer"},
                },
                "required": [
                    "__type__",
                    "start",
                    "end",
                    "number",
                ],
            },
        }
        # Открыть файл с заданным именем и прочитать его содержимое.
        with file_path.open("r") as file_in:
            data = json.load(file_in)  # Прочитать данные из файла

        validate(instance=data, schema=schema)
        for route in data:
            route.pop("__type__", None)
            self.routes.append(Route(**route))


def main(command_line: str | None = None) -> None:
    """
    Главная функция программы.
    """
    logging.basicConfig(
        filename="app.log",
        filemode="a",
        format="%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    file_parser = CustomArgumentParser(add_help=False)
    file_parser.add_argument(
        "--home",
        action="store_true",
        help="Save the file in the user's home directory",
    )
    file_parser.add_argument(
        "filename", action="store", help="The data file name"
    )
    parser = CustomArgumentParser("routes")
    parser.add_argument(
        "--version", action="version", version="%(prog)s 0.2.0"
    )
    subparsers = parser.add_subparsers(dest="command")
    add = subparsers.add_parser(
        "add", parents=[file_parser], help="Add a new route"
    )
    add.add_argument(
        "-s", "--start", action="store", required=True, help="The route start"
    )
    add.add_argument(
        "-e", "--end", action="store", required=True, help="The route endpoint"
    )
    add.add_argument(
        "-n",
        "--number",
        action="store",
        type=int,
        required=True,
        help="The number of route",
    )

    _ = subparsers.add_parser(
        "list", parents=[file_parser], help="Display all routes"
    )

    select = subparsers.add_parser(
        "select", parents=[file_parser], help="Select the routes"
    )
    select.add_argument(
        "-p",
        "--point",
        action="store",
        required=True,
        help="Routes starting or ending at this point",
    )

    args = parser.parse_args(command_line)

    # Загрузить всех работников из файла, если файл существует.
    is_dirty = False
    routes = Routes()
    if args.home:
        filepath: Path = Path.home() / args.filename
    else:
        filepath = Path(args.filename)

    if os.path.exists(filepath):
        routes.load(filepath)
        logging.info(f"Загружены маршруты из файла {filepath}")
    elif args.command.lower() in ("list", "select"):
        raise FileNotExistsError(
            filepath,
            f'Файл не найден, для команды "{args.command.lower()}" '
            "необходим существующий файл",
        )
    else:
        logging.info(
            f"Файл {filepath} не найден, будет создан при сохранении."
        )

    match args.command.lower():
        case "add":
            routes.add(args.start, args.end, args.number)
            is_dirty = True
            logging.info(
                f"Добавлен маршрут: {args.start} -> {args.end} ({args.number})"
            )

        case "list":
            print(routes)
            logging.info("Выведены все маршруты")

        case "select":
            name_point = args.point.lower()
            selected = routes.select(name_point)
            print(selected)
            if selected:
                logging.info(
                    f"Найдено {len(selected)} маршрутов, "
                    f"начинающихся или заканчивающихся в точке {name_point}"
                )
            else:
                logging.warning(
                    f"Найдено 0 маршрутов, "
                    f"начинающихся или заканчивающихся в точке {name_point}"
                )

    if is_dirty:
        routes.save(filepath)
        logging.info(f"Сохранены маршруты в файл {filepath}")


if __name__ == "__main__":
    try:
        main()
    except ValidationError as exc:
        logging.error(f"Ошибка валидации: {exc}")
        print(f"Ошибка валидации: {exc.message}", file=sys.stderr)
    except argparse.ArgumentError as exc:
        logging.error(f"Ошибка аргумента командной строки: {exc}")
        print(f"Ошибка аргумента командной строки: {exc}", file=sys.stderr)
    except Exception as exc:
        logging.error(f"Ошибка:\n{traceback.format_exc()}")
        print(exc, file=sys.stderr)
