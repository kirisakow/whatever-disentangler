import argparse
import sys

import whatever_disentangler as wd

#
# Get user-defined params
#
parser = argparse.ArgumentParser(description="""`whatever_disentangler` is a brute-force disentangler for legacy encodings. At the core, what it does is: `str_to_fix.encode(encoding_from).decode(encoding_to)` with `encoding_from` and `encoding_to` being one or more of all the encodings supported by Python (see https://docs.python.org/3/library/codecs.html#standard-encodings for details), only skipping the cases where `encoding_from` is `encoding_to`.""")

parser.add_argument('str_to_fix', default=None, type=str, help="(required) Garbled string to fix. If the string contains spaces, enclose it in quotation marks.")

parser.add_argument('--encoding-from', default=None, type=str, nargs='+', help="(optional, default: all supported encodings) Set one or more of the encodings supported by Python that you suspect to be the one(s) from which the garbled `str_to_fix`. See https://docs.python.org/3/library/codecs.html#standard-encodings for details.")

parser.add_argument('--encoding-to', default=None, type=str, nargs='+', help="(optional, default: all supported encodings) One or more of the encodings supported by Python. See https://docs.python.org/3/library/codecs.html#standard-encodings for details.")

parser.add_argument('--expected-str', default=None, type=str, help="(optional) What you expect the fixed string to look like. Adding this option narrows down the number of returned possibilities to those for which the result of `str_to_fix.encode(encoding_from).decode(encoding_to)` mathes `expected_str`")

parser.add_argument('--recursivity-depth', default=1, type=int, help="(optional, default: %(default)s) If you are not satisfied with the result with every possible encoding (or your selection of encodings), set this option to 2, which will result in that every possible already decoded result will be treated as if it were `str_to_fix` and taken to another tour of every possible encoding (or your selection of encodings). This will result in more output, slower run time and, possibly, a crash (with `RecursionError: maximum recursion depth exceeded` or a `MemoryError: Stack overflow`), therefore use with caution for values 3 or higher.")

args = parser.parse_args()
if (str_to_fix := args.str_to_fix).strip() == '':
    sys.exit(parser.print_help())

disentangler = wd.Disentangler()
result_as_generator = disentangler.disentangle(
    str_to_fix=str_to_fix,
    encoding_from=args.encoding_from,
    encoding_to=args.encoding_to,
    expected_str=args.expected_str,
    recursivity_depth=args.recursivity_depth
)
try:
    disentangler.flatten_legibly(result_as_generator)
except KeyboardInterrupt:
    sys.exit('\ninterrupted by user')