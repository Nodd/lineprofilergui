# type: ignore
# ruff: noqa: F821

import time
import os
from pprint import pprint

import subdir.profiling_test_script2 as script2


@profile
def fact(n):
    result = 1
    for i in range(2, n // 4):
        result *= i
    result = 1
    # This is a comment
    for i in range(2, n // 16):
        result *= i
    result = 1

    if False:
        # This won't be run
        raise RuntimeError("What are you doing here ???")

    for i in range(2, n + 1):
        result *= i
    return result
    # This is after the end of the function.

    if False:
        # This won't be run
        raise RuntimeError("It's getting bad.")


@profile
def wont_run(n):
    # Don't try this at home!
    while True:
        time.sleep(1)


@profile
def sum_(
    n,
    this_very_long_argument_list,
    and_this_one,
    and_another_one,
    this_is_the_last_one_i_promise,
    ___i_m_sorry,
):
    """Docstring"""
    # Comment
    result = 0
    "string"

    for i in range(1, n + 1):
        result += i
    return result


if __name__ == "__main__":
    print(fact(120))
    print(sum_(120, 0, 0, 0, 0, 0))
    print(script2.fact2(120))
    print(script2.sum2(120))
    pprint(dict(os.environ))
