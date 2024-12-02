#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Решите следующую задачу: напишите программу, которая запрашивает ввод
# двух значений. Если хотя бы одно из них не является числом, то должна
# выполняться конкатенация, т. е. соединение, строк. В остальных случаях
# введенные числа суммируются.


def main() -> None:
    result: int | str
    try:
        a = input("Введите первое число: ")
        b = input("Введите второе число: ")
        c = int(a)
        d = int(b)
        result = c + d
    except ValueError:
        result = f"{a}{b}"
    except Exception as e:
        result = "Непредвиденная ошибка: " + str(e)
    finally:
        print(f"Результат: {result}")


if __name__ == "__main__":
    main()
