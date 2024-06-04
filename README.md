# `whatever-disentangler` is a brute-force disentangler for legacy encodings

* It is available as both a self-hosted web service and an importable library
* It supports [as many encodings as Python itself](https://docs.python.org/3/library/codecs.html#standard-encodings)

### Use cases

* When you already know what the expected (disentangled) string looks like
* When you know which encodings you want to try, even without knowing what the expected string looks like
* Tough cases which need two-step detangling

### Installation with Poetry
```bash
git clone https://github.com/kirisakow/whatever-disentangler.git

cd whatever-disentangler

poetry install
```

### Use `whatever-disentangler` as a CLI executable

Run script with no arguments to see a complete usage note. Here are the key moments:

1. `str_to_fix` is the only required argument and the only positional argument. As a positional argument, it takes no key, only the value; as the only positional argument, it goes either to the very first or the very last position of the command line (prefer the beginning though, otherwise it may be mistaken for the value of those other arguments that can take multiple values). If the string contains spaces, enclose it in quotation marks.
2. All the other arguments are optional. Their keys must go in pair with their values: `--expected_str "the actual expected string"`. Both the underscore and the hyphen are valid characters to write the keys; in other words, both `snake_case` and `kebab-case` notations are valid.
3. The optional arguments `--encoding-from` and `--encoding-to` can take multiple values, separated by space or another IFS.

Examples:

```bash
python whatever_disentangler "ÃƒÂ©chÃƒÂ©ancier" --recursivity-depth 2 --expected-str "échéancier" --encoding_from cp1250 cp1251 cp1252
```
```
...
'ÃƒÂ©chÃƒÂ©ancier' ('cp1252') -> 'Ã©chÃ©ancier' ('utf_8')
    -> 'Ã©chÃ©ancier' ('cp1252') -> 'échéancier' ('utf_8')
    -> 'Ã©chÃ©ancier' ('cp1252') -> 'échéancier' ('utf_8_sig')
...
```

### Use `whatever-disentangler` as an importable library in Python code

Add `whatever-disentangler` as a dependency so you can import it:
```bash
cd your-project

poetry add --editable ../rel/path/to/whatever-disentangler/

poetry install
```
Use `whatever-disentangler` as both offline executable or a remote HTTP API caller:
```py
from whatever_disentangler import Disentangler, RemoteDisentangler

# this one is an offline disentangler:
disentangler = Disentangler()
disentangler.flatten_legibly(
  disentangler.disentangle(str_to_fix="боз▌з╤з╙з╤ б░з▄зтз╤Б0Ж3з▀Б0┌1! Б0┘5з╓зтзрз┴з▐ зуз▌з╤з╙з╤!", expected_str="Слава Україні! Героям слава!", recursivity_depth=2)
)

# and this one is remote: it calls a homemade REST API:
remote_disentangler = RemoteDisentangler(endpoint='https://crac.ovh/fix_legacy_encoding')
response_obj = await remote_disentangler.fetch_response(str_to_fix="ŢčŢ»ŢąŢ¦ ŢÓŢ¦Ţ®Ţ˘Ţ´Ţ·ŢµŢş! ŢčŢ»ŢąŢ¦ ŢąŢ¦ŢŔŢ°Ţ˘!", expected_str="Жыве Беларусь! Жыве вечна!", recursivity_depth=2)
remote_disentangler.flatten_legibly(response_obj)
```

To see `whatever_disentangler` in action,
* have a look at [README.ipynb](https://github.com/kirisakow/whatever_disentangler/blob/main/README.ipynb)
* play with the live HTTP API:
  * https://crac.ovh/fix_legacy_encoding?str_to_fix=GocÅ‚awski&encoding_from=&encoding_to=&expected_str=Gocławski&recursivity_depth=
  * https://crac.ovh/fix_legacy_encoding?str_to_fix=ÃƒÂ©chÃƒÂ©ancier&encoding_from=&encoding_to=&expected_str=échéancier&recursivity_depth=2
