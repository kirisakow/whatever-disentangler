import requests
import os, sys
from urllib.parse import urlencode, unquote
from urllib.request import urlretrieve


class Disentangler:
    def __init__(self):
        pass


    def disentangle(self, *, str_to_fix: str, encoding_from=None, encoding_to=None, expected_str=None, recursivity_depth=1):
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
                # Copied from https://docs.python.org/3/library/codecs.html#standard-encodings
                with open('whatever_disentangler/assets/standard_encodings.txt', 'r') as f:
                    standard_encodings = f.read().splitlines()
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

        yield from _fix_legacy_encoding(str_to_fix, _resolve_encodings(encoding_from), _resolve_encodings(encoding_to), expected_str, recursivity_depth)


    def flatten_legibly(self, result_generator) -> None:
        max_depth = 1
        for d in result_generator:
            max_depth = max(max_depth, int(d['recursivity_depth']))
            indent_width = 4 * (max_depth - int(d['recursivity_depth']))
            indent = indent_width * ' '
            indent += '-> ' if indent_width > 0 else ''
            s = f"{indent}{d['str_to_fix']!r} ({d['encoding_from']!r}) -> {d['fixed_str']!r} ({d['encoding_to']!r})"
            print(s)


class RemoteDisentangler:
    def __init__(self, endpoint: str = None):
        self.endpoint = endpoint


    async def fetch_response(self, *, str_to_fix: str, encoding_from=None, encoding_to=None, expected_str=None, recursivity_depth=1):
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
        max_depth = max([int(d['recursivity_depth']) for d in payload]) if payload else 1
        for d in payload:
            indent_width = 4 * (max_depth - int(d['recursivity_depth']))
            indent = indent_width * ' '
            indent += '-> ' if indent_width > 0 else ''
            s = f"{indent}{d['str_to_fix']!r} ({d['encoding_from']!r}) -> {d['fixed_str']!r} ({d['encoding_to']!r})"
            print(s)