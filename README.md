# backend-boilerplate
A python package for backend

## Installation

### Specific version (recommended)
```bash
pip install git+https://github.com/iras-test/backend-boilerplate.git@v0.1.1#egg=backend-boilerplate
```

### Latest main
```bash
pip install git+https://github.com/iras-test/backend-boilerplate.git@main#egg=backend-boilerplate
```

### In requirements.txt

**Simple format:**
```
git+https://github.com/iras-test/backend-boilerplate.git@main#egg=backend-boilerplate
```

**Specific version:**
```
git+https://github.com/iras-test/backend-boilerplate.git@v0.1.1#egg=backend-boilerplate
```

**Alternative syntax:**
```
backend-boilerplate @ git+https://github.com/iras-test/backend-boilerplate.git@v0.1.1
```

## Versioning

This project uses manual versioning. The version is defined in `backend_boilerplate/__init__.py`.

### Release workflow

1. Update version in `backend_boilerplate/__init__.py`:
   ```python
   __version__ = "0.1.2"
   ```

2. Commit and tag:
   ```bash
   git add backend_boilerplate/__init__.py
   git commit -m "Bump version to 0.1.2"
   git tag v0.1.2
   git push origin main --tags
   ```

