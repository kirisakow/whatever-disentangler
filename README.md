# `whatever_disentangler` is a brute-force disentangler for legacy encodings

* It is available as both a self-hosted web service and a package (soon officially, let's hope so!)
* It supports [as many encodings as Python itself](https://docs.python.org/3/library/codecs.html#standard-encodings)

```py
from whatever_disentangler import whatever_disentangler as wd

# this one is an offline disentangler
disentangler = wd.Disentangler()

# this one is remote and calls a homemade REST API
remote_disentangler = wd.RemoteDisentangler(endpoint='https://crac.ovh/fix_legacy_encoding')
```

### Use cases

* When you already know what the expected (disentangled) string looks like
* When you know which encodings you want to try, even without knowing what the expected string looks like
* Tough cases which need two-step detangling

# To see `whatever_disentangler` in action, please see [README.ipynb](https://github.com/kirisakow/whatever_disentangler/blob/main/README.ipynb)
