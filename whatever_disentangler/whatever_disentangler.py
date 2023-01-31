import colorama
import requests
import os, sys
import time
from urllib.parse import urlencode, unquote
from urllib.request import urlretrieve

from constants import STANDARD_ENCODINGS


# si environnement MS-DOS : démarrer colorama
if os.name == 'nt' or sys.platform == 'win32':
    colorama.init()


class Disentangler:
    def __init__(self):
        self.expected_str = None
        self.recursivity_depth = 1


    def disentangle(self, *, str_to_fix: str, encoding_from=None, encoding_to=None, expected_str: str=None, recursivity_depth: int=1):
        if str_to_fix is None or str_to_fix.strip() == '':
            raise ValueError(f"The required parameter str_to_fix (string to fix) is empty.")

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


    def flatten_legibly(self, result_generator) -> None:
        for d in result_generator:
            indent_width = 4 * (self.recursivity_depth - int(d['recursivity_depth']))
            indent = indent_width * ' '
            indent += '-> ' if indent_width > 0 else ''
            match = self.expected_str is not None and d['fixed_str'] == self.expected_str
            fixed_str = d['fixed_str'] if not match else colorama.Fore.GREEN + d['fixed_str'] + colorama.Style.RESET_ALL
            s = f"{indent}{d['str_to_fix']!r} ({d['encoding_from']!r}) -> '{fixed_str}' ({d['encoding_to']!r})"
            print(s)
            if match:
                time.sleep(1)


class RemoteDisentangler:
    def __init__(self, endpoint: str = None):
        self.endpoint = endpoint
        self.expected_str = None
        self.recursivity_depth = 1


    async def fetch_response(self, *, str_to_fix: str, encoding_from=None, encoding_to=None, expected_str: str=None, recursivity_depth: int=1):
        self.expected_str = expected_str
        self.recursivity_depth = recursivity_depth
        qparams = {}
        params = [str_to_fix, encoding_from, encoding_to, expected_str, recursivity_depth]
        param_names = ['str_to_fix', 'encoding_from', 'encoding_to', 'expected_str', 'recursivity_depth']
        for pname, pvalue in zip(param_names, params):
            if pvalue:
                qparams[pname] = pvalue
        response = requests.get(self.endpoint + '?' + urlencode(qparams))
        return response


    def flatten_legibly(self, response_obj) -> None:
        payload, req_url = (response_obj.json(), response_obj.request.url)
        if payload in (None, []):
            print(f"Got an empty response {payload!r} ({type(payload).__name__}) for the request {unquote(req_url)!r}")
            return
        for d in payload:
            indent_width = 4 * (self.recursivity_depth - int(d['recursivity_depth']))
            indent = indent_width * ' '
            indent += '-> ' if indent_width > 0 else ''
            match = self.expected_str is not None and d['fixed_str'] == self.expected_str
            fixed_str = d['fixed_str'] if not match else colorama.Fore.GREEN + d['fixed_str'] + colorama.Style.RESET_ALL
            s = f"{indent}{d['str_to_fix']!r} ({d['encoding_from']!r}) -> '{fixed_str}' ({d['encoding_to']!r})"
            print(s)