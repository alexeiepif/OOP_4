#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Решите следующую задачу: напишите программу, которая будет
# генерировать матрицу из случайных целых чисел.
# Пользователь может указать число строк и столбцов,
# а также диапазон целых чисел.
# Произведите обработку ошибок ввода пользователя.

import random
from typing import Generator


class Matrix:
    def __init__(self, rows: int, columns: int, start: int, end: int) -> None:
        self.rows = rows
        self.columns = columns
        self.start = start
        self.end = end
        self.matrix: list[list[int]] = []

    def generate_matrix(self) -> None:
        for name, value in self.items():
            if value <= 0:
                raise NumberNotPositiveError(name, value)

        if self.start > self.end:
            raise StartGreaterThanEndError(self.start, self.end)

        self.matrix = [
            [random.randint(self.start, self.end) for _ in range(self.columns)]
            for _ in range(self.rows)
        ]

    def items(self) -> Generator[tuple[str, int], None, None]:
        for name in ["rows", "columns"]:
            yield name, getattr(self, name)

    def __str__(self) -> str:
        if not self.matrix:
            return "Матрица пока не сгенерирована"
        string = ""
        for row in self.matrix:
            string += "|\t" + "\t".join(map(str, row)) + "\t|\n"
        return string


class StartGreaterThanEndError(Exception):
    def __init__(
        self,
        start: int,
        end: int,
        message: str = "Начало диапазона больше конца",
    ) -> None:
        self.start = start
        self.end = end
        self.message = message
        super(StartGreaterThanEndError, self).__init__(message)

    def __str__(self) -> str:
        return f"{self.message}: {self.start} > {self.end}"


class NumberNotPositiveError(Exception):
    def __init__(
        self,
        name: str,
        number: int,
        message: str = "Значение не является положительным",
    ):
        self.name = name
        self.number = number
        self.message = message
        super(NumberNotPositiveError, self).__init__(message)

    def __str__(self) -> str:
        return f"{self.message}: {self.name} = {self.number} (ожидалось > 0)"


def main() -> None:
    try:
        matrix = Matrix(
            int(input("Введите количество строк: ")),
            int(input("Введите количество столбцов: ")),
            int(input("Введите начало диапазона: ")),
            int(input("Введите конец диапазона: ")),
        )
        matrix.generate_matrix()
        print(matrix)

    except Exception as e:
        print("Ошибка: ", e)


if __name__ == "__main__":
    main()
