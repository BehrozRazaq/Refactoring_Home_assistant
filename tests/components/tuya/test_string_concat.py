import random
import string
import pytest


# Functions to be compared in test ( new_string_concat(...) and old_string_concat(...) )
def new_string_concat(str1, str2, str3):
    result = ''.join(filter(None, map(str, [str1, str2, str3])))
    return result


def old_string_concat(str1, str2, str3):
    result = f"{str1}{str2}{str3 or ''}"
    return result


# Generates random string of random length
def generate_random_string(min_length, max_length):
    characters = string.ascii_letters + string.digits + string.punctuation
    random_length = random.randint(min_length, max_length)
    random_string = ''.join(random.choice(characters) for _ in range(random_length))
    return random_string


# Defines test cases to cover different inputs
@pytest.mark.parametrize("input1, input2, input3", [
    # Test case 1: only None
    (None, None, None),
    # Test case 2: only empty
    ('', '', ''),
    # Test case 3: only random
    (generate_random_string(1, 15), generate_random_string(1, 15), generate_random_string(1, 15)),
    # Test case 4: combination
    (None, '', generate_random_string(1, 15)),
    # With int involved:
    # Test case 5: only int
    (random.randint(-100, 100), random.randint(-100, 100), random.randint(-100, 100)),
    # Test case 6: combination with int
    (random.randint(-100, 100), None, ''),
    # Test case 7: combination with int
    (random.randint(-100, 100), None, generate_random_string(1, 15)),
    # Test case 8: combination with int
    (random.randint(-100, 100), '', generate_random_string(1, 15)),


])
def test_string_concat_same(input1, input2, input3):
    expected_string = old_string_concat(input1, input2, input3)
    actual_string = new_string_concat(input1, input2, input3)

    assert actual_string == expected_string
