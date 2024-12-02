#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any

import pytest

from task_2 import Matrix, NumberNotPositiveError, StartGreaterThanEndError, main


def test_matrix(capsys: pytest.CaptureFixture[Any]) -> None:
    matrix = Matrix(2, 3, 1, 5)
    matrix.generate_matrix()

    assert len(matrix.matrix) == 2
    for row in matrix.matrix:
        assert len(row) == 3
        for elem in row:
            assert elem >= 1 and elem <= 5

    for i in matrix.items():
        assert i == ("rows", 2) or i == ("columns", 3)

    print(matrix)

    capture = capsys.readouterr()
    assert capture.out != "Матрица пока не сгенерирована\n"

    new_matrix = Matrix(2, 3, 1, 5)

    print(new_matrix)

    capture = capsys.readouterr()
    assert capture.out == "Матрица пока не сгенерирована\n"

    fatall_matrix = Matrix(2, 0, -1, 5)

    with pytest.raises(NumberNotPositiveError):
        fatall_matrix.generate_matrix()

    fatall_matrix = Matrix(2, 3, 10, 5)

    with pytest.raises(StartGreaterThanEndError):
        fatall_matrix.generate_matrix()


def test_start_greater_than_end(capsys: pytest.CaptureFixture[Any]) -> None:
    error = StartGreaterThanEndError(10, 5)

    assert str(error) == "Начало диапазона больше конца: 10 > 5"


def test_number_not_positive(capsys: pytest.CaptureFixture[Any]) -> None:
    error = NumberNotPositiveError("name", 0)

    assert str(error) == "Значение не является положительным: name = 0 (ожидалось > 0)"

    error = NumberNotPositiveError("name", -1)

    assert str(error) == "Значение не является положительным: name = -1 (ожидалось > 0)"


def test_main(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[Any]
) -> None:
    inputs = iter(["2", "3", "1", "5"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    try:
        main()
    except Exception as e:
        pytest.fail(f"Программа завершилась с ошибкой: {e}")

    captured = capsys.readouterr()
    assert captured.out != "Матрица пока не сгенерирована\n"

    inputs = iter(["2", "3", "10", "5"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    main()

    captured = capsys.readouterr()
    assert captured.out == "Ошибка:  Начало диапазона больше конца: 10 > 5\n"

    inputs = iter(["-9", "3", "-1", "5"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    main()

    captured = capsys.readouterr()
    assert (
        captured.out
        == "Ошибка:  Значение не является положительным: rows = -9 (ожидалось > 0)\n"
    )
