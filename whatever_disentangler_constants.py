import os

# Copied from https://docs.python.org/3/library/codecs.html#standard-encodings
STANDARD_ENCODINGS = open(os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'assets/standard-encodings.txt')
)).read()