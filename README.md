

## btor2ex: Barebones symbolic execution (and model checker) for BTOR2 



### Requirements:

- `btor2-opt`: for parsing btor2 programs
- `pyboolector`: currently implemented verification backend. Boolector Python bindings need to be installed manually (see https://boolector.github.io/)

### Examples:

The following results in a violation and CEX trace:
```
python3 btor2ex_main.py tests/btor/reg_en.bad.btor -b 4
```
the following does not:
```
python3 btor2ex_main.py tests/btor/reg_en.safe.btor -b 4
```


---

(c) Adwait Godbole, BSD-3-Clause