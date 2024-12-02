#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
from pathlib import Path
from typing import Any

import pytest
from jsonschema import ValidationError

from ind_1 import (
    CustomArgumentParser,
    FileNotExistsError,
    Route,
    RouteExistsError,
    Routes,
    main,
)


def test_custom_argument_parser(capsys: pytest.CaptureFixture[Any]) -> None:
    parser = CustomArgumentParser("program")
    parser.add_argument("--version", action="version", version="%(prog)s 0.2.0")
    with pytest.raises(SystemExit) as excinfo:
        parser.parse_args(["--version"])

    captured = capsys.readouterr()
    assert captured.out == "program 0.2.0\n"
    assert excinfo.value.code == 0

    with pytest.raises(argparse.ArgumentError):
        parser.parse_args(["-k"])


def test_route_exists_error() -> None:
    error = RouteExistsError(Route("A", "B", 1))
    with pytest.raises(RouteExistsError):
        raise error

    assert str(error) == "Route(start='A', end='B', number=1) -> Route already exists"


def test_file_not_exists_error() -> None:
    error = FileNotExistsError(Path("file.json"))
    with pytest.raises(FileNotExistsError):
        raise error

    assert str(error) == "file.json -> File not exists"


def test_route() -> None:
    route = Route("A", "B", 1)
    assert route.start == "A"
    assert route.end == "B"
    assert route.number == 1


def test_routes(capsys: pytest.CaptureFixture[Any]) -> None:
    routes = Routes()
    print(routes)

    cature = capsys.readouterr()
    assert cature.out == "Список маршрутов пуст.\n"
    assert len(routes) == 0

    routes.add("A", "B", 1)
    assert len(routes) == 1
    assert len(routes) == len(routes.routes)
    routes.add("X", "B", 1)
    assert len(routes) == 2

    print(routes)

    cature = capsys.readouterr()
    assert (
        cature.out
        == """+------+--------------------------------+----------------------"""
        """+------------------+
|  No  |             Начало             |        Конец         |  Номер маршрута  |
+------+--------------------------------+----------------------+------------------+
|  1   | a                              | b                    |                1 |
|  2   | x                              | b                    |                1 |
+------+--------------------------------+----------------------+------------------+\n"""
    )

    routes_selected = routes.select("A")
    assert len(routes_selected) == 1
    assert routes_selected.routes[0] == Route("a", "b", 1)

    routes_selected = routes.select("B")
    assert len(routes_selected) == 2

    new_routes = Routes()
    new_routes.load(Path("json/fi.json"))
    assert len(new_routes) == 3

    assert len(new_routes.select("stav")) == 2

    new_routes.save(Path("json/f.json"))

    assert os.path.exists("json/f.json")

    os.remove("json/f.json")


def test_main() -> None:
    with pytest.raises(FileNotExistsError):
        main("list f.json".split())

    with pytest.raises(RouteExistsError):
        main("add -s bbb -e hhh -n 18 fe.json ".split())

    with pytest.raises(ValidationError):
        main("list fi_invalid.json".split())
