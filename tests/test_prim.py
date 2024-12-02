#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from typing import Any

import pytest

from prim import IllegalYearError, Staff, Worker


def test_worker() -> None:
    worker = Worker(name="Иван", post="студент", year=2022)
    assert worker.name == "Иван"
    assert worker.post == "студент"
    assert worker.year == 2022


def test_staff(capsys: pytest.CaptureFixture[Any]) -> None:
    staff = Staff()

    assert len(staff.workers) == 0

    staff.add("Иван", "студент", 2022)

    assert len(staff.workers) == 1
    assert isinstance(staff.workers[0], Worker)
    assert staff.workers[0] == Worker(name="Иван", post="студент", year=2022)

    staff.add("Петр", "студент", 2022)

    assert len(staff.workers) == 2

    print(staff)
    captured = capsys.readouterr()
    assert (
        captured.out == """+------+--------------------------------+---------"""
        """-------------+----------+
|  No  |             Ф.И.О.             |      Должность       |   Год    |
+------+--------------------------------+----------------------+----------+
|    1 | Иван                           | студент              |     2022 |
|    2 | Петр                           | студент              |     2022 |
+------+--------------------------------+----------------------+----------+
"""
    )

    staff.load("XML/file.xml")

    assert len(staff.workers) == 2

    print(staff)
    captured = capsys.readouterr()
    assert (
        captured.out
        == """+------+--------------------------------+----------------------"""
        """+----------+
|  No  |             Ф.И.О.             |      Должность       |   Год    |
+------+--------------------------------+----------------------+----------+
|    1 | Епифанов А.А.                  | студент              |     2022 |
|    2 | Петров П.П.                    | Студент              |     2019 |
+------+--------------------------------+----------------------+----------+
"""
    )

    assert list(map(lambda worker: worker.name, staff.select(2))) == [
        "Епифанов А.А.",
        "Петров П.П.",
    ]
    assert list(map(lambda worker: worker.name, staff.select(3))) == ["Петров П.П."]

    staff.save("XML/new_file.xml")

    assert os.path.exists("XML/new_file.xml")

    new_staff = Staff()
    new_staff.load("XML/new_file.xml")

    assert new_staff.workers == staff.workers

    os.remove("XML/new_file.xml")

    with pytest.raises(IllegalYearError):
        staff.add("Иван", "студент", -1)

    with pytest.raises(IllegalYearError):
        staff.add("Иван", "студент", 3000)


def test_illegal_year(capsys: pytest.CaptureFixture[Any]) -> None:
    error = IllegalYearError(2029)

    assert str(error) == "2029 -> Illegal year number"
