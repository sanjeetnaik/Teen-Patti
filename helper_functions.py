# Import Statements

import random  ## Used for generating random string
import string  ## Used for generating random string


# Random String generation code

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_letters
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str