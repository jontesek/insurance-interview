def find_max_sum(numbers: list[int]) -> int:
    """Find maximum sum so that no two elements are adjacent.
    Uses dynamic programming approach.
    """
    # Contains max sum when previous number is included.
    included_sum = 0
    # Contains max sum when previous number is excluded.
    excluded_sum = 0
    # For every number check that if we add it, the sum will increase.
    for number in numbers:
        new_excluded = max(included_sum, excluded_sum)
        included_sum = excluded_sum + number
        excluded_sum = new_excluded

    return max(included_sum, excluded_sum)


def find_max_sum_rec(numbers: list[int]) -> int:
    """Find maximum sum so that no two elements are adjacent.
    Uses recursive approach.
    """
    return recursive(numbers, 0)


def recursive(numbers: list[int], index: int) -> int:
    if index >= len(numbers):
        return 0
    return max(
        numbers[index] + recursive(numbers, index + 2), recursive(numbers, index + 1)
    )


if __name__ == "__main__":
    input_data = [3, 2, 5, 10, 7]
    print(find_max_sum(input_data))
    # print(find_max_sum_rec(input_data))
