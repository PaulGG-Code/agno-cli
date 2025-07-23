# PyPI Upload Script for agno_cli

This directory contains tools for uploading the `agno_cli` package to PyPI.

## Files

- `upload_to_pypi.py` - Main upload script
- `.pypirc.template` - Template for PyPI credentials configuration
- `UPLOAD_README.md` - This file

## Prerequisites

Before using the upload script, ensure you have the following tools installed:

```bash
# Install required tools
pip install twine build

# Optional: Install pytest for testing
pip install pytest
```

## Setup PyPI Credentials

### Option 1: Using .pypirc file (Recommended)

1. Copy the template file:
   ```bash
   cp .pypirc.template ~/.pypirc
   ```

2. Edit `~/.pypirc` and add your credentials:
   ```ini
   [pypi]
   username = your_pypi_username
   password = your_pypi_password
   
   [testpypi]
   username = your_testpypi_username
   password = your_testpypi_password
   ```

### Option 2: Using API Tokens (More Secure)

1. Go to [PyPI Account Settings](https://pypi.org/manage/account/)
2. Create an API token
3. Use the token in your `.pypirc`:
   ```ini
   [pypi]
   username = __token__
   password = pypi-your_api_token_here
   ```

### Option 3: Environment Variables

Set environment variables:
```bash
export PYPI_USERNAME="your_username"
export PYPI_PASSWORD="your_password"
```

## Usage

### Basic Usage

```bash
# Upload with patch version bump (default)
python upload_to_pypi.py

# Upload with minor version bump
python upload_to_pypi.py --minor

# Upload with major version bump
python upload_to_pypi.py --major
```

### Advanced Options

```bash
# Upload to TestPyPI first (recommended)
python upload_to_pypi.py --test

# Dry run - see what would be done without doing it
python upload_to_pypi.py --dry-run

# Skip running tests
python upload_to_pypi.py --skip-tests

# Force upload even if tests fail
python upload_to_pypi.py --force

# Combine options
python upload_to_pypi.py --test --minor --dry-run
```

### Complete Workflow

1. **Test on TestPyPI first:**
   ```bash
   python upload_to_pypi.py --test --minor
   ```

2. **Install and test from TestPyPI:**
   ```bash
   pip install --index-url https://test.pypi.org/simple/ agno_cli
   ```

3. **Upload to production PyPI:**
   ```bash
   python upload_to_pypi.py --minor
   ```

## What the Script Does

1. **Prerequisites Check**: Verifies that required tools are installed
2. **Version Management**: Automatically bumps version numbers in:
   - `pyproject.toml`
   - `setup.py`
   - `agno_cli/__init__.py`
3. **Cleanup**: Removes old build artifacts
4. **Testing**: Runs tests (if available)
5. **Building**: Creates wheel and source distributions
6. **Validation**: Checks the built package
7. **Upload**: Uploads to PyPI with confirmation

## Version Bumping

The script supports semantic versioning:

- `--patch` (default): 1.2.3 → 1.2.4
- `--minor`: 1.2.3 → 1.3.0
- `--major`: 1.2.3 → 2.0.0

## Safety Features

- **Dry Run**: Use `--dry-run` to see what would happen
- **Confirmation**: Script asks for confirmation before uploading
- **TestPyPI**: Upload to TestPyPI first to test
- **Error Handling**: Comprehensive error checking and reporting
- **Colored Output**: Clear visual feedback

## Troubleshooting

### Common Issues

1. **"Missing tools" error:**
   ```bash
   pip install twine build
   ```

2. **Authentication failed:**
   - Check your `.pypirc` file
   - Verify your PyPI credentials
   - Try using API tokens instead of passwords

3. **Version already exists:**
   - Use `--minor` or `--major` to bump version
   - Or manually update version in `pyproject.toml`

4. **Build fails:**
   - Check that all dependencies are in `requirements.txt`
   - Verify `pyproject.toml` is properly configured

### Getting Help

```bash
# Show all options
python upload_to_pypi.py --help

# Check current version
python -c "import agno_cli; print(agno_cli.__version__)"
```

## Best Practices

1. **Always test on TestPyPI first**
2. **Use semantic versioning appropriately**
3. **Run tests before uploading**
4. **Use API tokens instead of passwords**
5. **Keep your credentials secure**

## Security Notes

- Never commit `.pypirc` to version control
- Use API tokens instead of passwords when possible
- Keep your PyPI credentials secure
- Consider using environment variables for CI/CD

## CI/CD Integration

For automated deployments, you can use environment variables:

```bash
export PYPI_USERNAME="__token__"
export PYPI_PASSWORD="pypi-your_api_token_here"
python upload_to_pypi.py --skip-tests --force
``` 