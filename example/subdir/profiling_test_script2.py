# type: ignore
# ruff: noqa: F821


@profile
def fact2(n):
    result = 1
    for i in range(2, n + 1):
        result *= i * 2
    return result


def sum2(n):
    result = 0
    for i in range(1, n + 1):
        result += i * 2
    return result


if __name__ == "__main__":
    print(fact2(120))
    print(sum2(120))
