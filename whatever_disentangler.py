import argparse
import colorama
import requests
import os
import sys
import time
import types
from urllib.parse import urlencode, unquote
from urllib.request import urlretrieve
from whatever_disentangler_constants import STANDARD_ENCODINGS


# si environnement MS-DOS : démarrer colorama
if os.name == 'nt' or sys.platform == 'win32':
    colorama.init()


class Disentangler:
    def __init__(self):
        self.expected_str = None
        self.recursivity_depth = 1

    def disentangle(self, *, str_to_fix: str, encoding_from=None, encoding_to=None, expected_str: str = None, recursivity_depth: int = 1) -> types.GeneratorType:
        if str_to_fix is None or str_to_fix.strip() == '':
            raise ValueError(
                f"The required parameter str_to_fix (string to fix) is empty."
            )

        def _fix(str_to_fix: str, encoding_from: str, encoding_to: str):
            return str_to_fix.encode(encoding_from).decode(encoding_to, errors='replace')

        def _resolve_encodings(enc):
            if isinstance(enc, str):
                return [enc]
            if isinstance(enc, list):
                return enc
            elif enc is None:
                standard_encodings = STANDARD_ENCODINGS.splitlines()
                return standard_encodings

        cache = []

        def _fix_legacy_encoding(str_to_fix: str, _encoding_from: list, _encoding_to: list, expected_str: str, recursivity_depth: int):
            for enc_from in _encoding_from:
                for enc_to in _encoding_to:
                    if enc_from == enc_to:
                        continue
                    try:
                        fixed_str = _fix(str_to_fix, enc_from, enc_to)
                    except UnicodeEncodeError:
                        pass
                    except Exception as e:
                        print(e)
                    else:
                        return_pack = {
                            "str_to_fix": str_to_fix,
                            "encoding_from": enc_from,
                            "fixed_str": fixed_str,
                            "encoding_to": enc_to,
                            "recursivity_depth": recursivity_depth
                        }
                        if (expected_str is None
                            or expected_str.strip() == ''
                            or expected_str.strip().lower() == fixed_str.strip().lower()
                                or recursivity_depth > 1):
                            if return_pack not in cache:
                                cache.append(return_pack)
                                yield return_pack
                        if recursivity_depth > 1:
                            decremented_depth = recursivity_depth - 1
                            yield from _fix_legacy_encoding(fixed_str, _encoding_from, _encoding_to, expected_str, decremented_depth)

        self.expected_str = expected_str
        self.recursivity_depth = recursivity_depth

        yield from _fix_legacy_encoding(str_to_fix, _resolve_encodings(encoding_from), _resolve_encodings(encoding_to), expected_str, recursivity_depth)

    def flatten_legibly(self, result_generator: types.GeneratorType) -> None:
        for d in result_generator:
            indent_width = 4 * (
                self.recursivity_depth - int(d['recursivity_depth'])
            )
            indent = indent_width * ' '
            indent += '-> ' if indent_width > 0 else ''
            match = self.expected_str is not None and d['fixed_str'] == self.expected_str
            fixed_str = d['fixed_str']
            if match:
                fixed_str = colorama.Fore.GREEN + fixed_str + colorama.Style.RESET_ALL
            s = f"{indent}{d['str_to_fix']!r} ({d['encoding_from']!r}) -> '{fixed_str}' ({d['encoding_to']!r})"
            print(s)
            if match:
                time.sleep(1)


class RemoteDisentangler:
    def __init__(self, endpoint: str = None):
        self.endpoint = endpoint
        self.expected_str = None
        self.recursivity_depth = 1

    async def fetch_response(self, *, str_to_fix: str, encoding_from=None, encoding_to=None, expected_str: str = None, recursivity_depth: int = 1):
        self.expected_str = expected_str
        self.recursivity_depth = recursivity_depth
        qparams = {}
        params = [str_to_fix, encoding_from,
                  encoding_to, expected_str, recursivity_depth]
        param_names = ['str_to_fix', 'encoding_from',
                       'encoding_to', 'expected_str', 'recursivity_depth']
        for pname, pvalue in zip(param_names, params):
            if pvalue:
                qparams[pname] = pvalue
        response = requests.get(self.endpoint + '?' + urlencode(qparams))
        return response

    def flatten_legibly(self, response_obj) -> None:
        payload, req_url = (response_obj.json(), response_obj.request.url)
        if payload in (None, []):
            print(
                f"Got an empty response {payload!r} ({type(payload).__name__}) for the request {unquote(req_url)!r}")
            return
        for d in payload:
            indent_width = 4 * (
                self.recursivity_depth - int(d['recursivity_depth'])
            )
            indent = indent_width * ' '
            indent += '-> ' if indent_width > 0 else ''
            match = self.expected_str is not None and d['fixed_str'] == self.expected_str
            fixed_str = d['fixed_str']
            if match:
                fixed_str = colorama.Fore.GREEN + fixed_str + colorama.Style.RESET_ALL
            s = f"{indent}{d['str_to_fix']!r} ({d['encoding_from']!r}) -> '{fixed_str}' ({d['encoding_to']!r})"
            print(s)


def main():
    usage = """

- invoke as a module:

    python -m whatever_disentangler "string to fix" [options]

or

    python -m whatever_disentangler [options] "string to fix"

- invoke as a standalone script:

    python whatever_disentangler.py "string to fix" [options]

or

    python whatever_disentangler.py [options] "string to fix"

Run with -h (--help) option to print a complete help notice.
-------------------------------------------------------------"""
    #
    # Get user-defined params
    #
    parser = argparse.ArgumentParser(prog="whatever_disentangler", usage=usage,
                                     description="""`whatever_disentangler` is a brute-force disentangler for legacy encodings. At the core, what it does is: `str_to_fix.encode(encoding_from).decode(encoding_to)` with `encoding_from` and `encoding_to` being one or more of all the encodings supported by Python (see https://docs.python.org/3/library/codecs.html#standard-encodings for details), only skipping the cases where `encoding_from` is `encoding_to`.""",
                                     epilog="Source code: https://github.com/kirisakow/whatever_disentangler")

    parser.add_argument('str_to_fix', default=None, type=str,
                        help="(required) Garbled string to fix. As a positional argument, it takes no key, only the value; as the only positional argument, it goes either to the very first or the very last position of the command line (prefer the beginning though, otherwise it may be mistaken for the value of those other arguments that can take multiple values). If the string contains spaces, enclose it in quotation marks.")

    parser.add_argument('--encoding-from', '--encoding_from', default=None, type=str, nargs='+',
                        help="(optional, default: all supported encodings) Set one or more of the encodings supported by Python that you suspect to be the one(s) from which the garbled `str_to_fix`. See https://docs.python.org/3/library/codecs.html#standard-encodings for details.")

    parser.add_argument('--encoding-to', '--encoding_to', default=None, type=str, nargs='+',
                        help="(optional, default: all supported encodings) One or more of the encodings supported by Python. See https://docs.python.org/3/library/codecs.html#standard-encodings for details.")

    parser.add_argument('--expected-str', '--expected_str', default=None, type=str, nargs=1,
                        help="(optional) What you expect the fixed string to look like. Adding this option narrows down the number of returned possibilities to those for which the result of `str_to_fix.encode(encoding_from).decode(encoding_to)` matches `expected_str`. The decoded strings matching `expected_str` are printed in green for better legibility in the output.")

    parser.add_argument('--recursivity-depth', '--recursivity_depth', default=1, type=int, nargs=1,
                        help="(optional, default: %(default)s) If you are not satisfied with the result with every possible encoding (or your selection of encodings), set this option to 2, which will result in that every possible already decoded result will be treated as if it were `str_to_fix` and taken to another tour of every possible encoding (or your selection of encodings). This will result in more output, slower run time and, possibly, a crash (with `RecursionError: maximum recursion depth exceeded` or a `MemoryError: Stack overflow`), therefore use with caution for values 3 or higher.")

    args = parser.parse_args()

    disentangler = wd.Disentangler()
    result_as_generator = disentangler.disentangle(
        str_to_fix=args.str_to_fix,
        encoding_from=args.encoding_from,
        encoding_to=args.encoding_to,
        expected_str=args.expected_str[0],
        recursivity_depth=args.recursivity_depth[0]
    )
    try:
        disentangler.flatten_legibly(result_as_generator)
    except KeyboardInterrupt:
        sys.exit('\ninterrupted by user')


if __name__ == '__main__':
    main()
