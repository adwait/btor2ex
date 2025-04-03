

## btor2ex: Symbolic execution (and model checking) for BTOR2 

### Requirements:

`btor2ex` requires Python 3.11 or later. It is recommended to use a virtual environment to avoid conflicts with other packages. Please see `requirements.txt` for the list of required packages. Install them using: 

```bash
pip install -r requirements.txt
```

### Package build and install:

Use the `pyproject.toml` tool to build/install the package. This will also install the required packages.

```bash
pip install .
```

### Usage:

Without install:

```bash
python -m btor2ex.btor2ex_main --help
```

With install:

```bash
btor2ex --help
```

---

Copyright (c) 2024-25. Adwait Godbole, UC Berkeley.