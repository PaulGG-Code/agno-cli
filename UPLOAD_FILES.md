# PyPI Upload Files

This directory contains all the files needed for uploading the `agno_cli` package to PyPI.

## Files Overview

| File | Purpose | Usage |
|------|---------|-------|
| `upload_to_pypi.py` | Main Python upload script | `python upload_to_pypi.py [options]` |
| `upload.sh` | Shell script wrapper | `./upload.sh [options]` |
| `.pypirc.template` | PyPI credentials template | Copy to `~/.pypirc` and configure |
| `UPLOAD_README.md` | Comprehensive documentation | Read for setup and usage |
| `UPLOAD_FILES.md` | This file | Overview of all upload files |

## Quick Start

1. **Install prerequisites:**
   ```bash
   pip install twine build
   ```

2. **Set up credentials:**
   ```bash
   cp .pypirc.template ~/.pypirc
   # Edit ~/.pypirc with your PyPI credentials
   ```

3. **Upload to TestPyPI first:**
   ```bash
   ./upload.sh --test --minor
   ```

4. **Upload to production PyPI:**
   ```bash
   ./upload.sh --minor
   ```

## File Details

### `upload_to_pypi.py`
- **Type**: Python script
- **Features**: 
  - Automatic version bumping
  - Prerequisites checking
  - Build and test automation
  - Safety confirmations
  - Colored output
  - Dry-run mode
- **Dependencies**: `twine`, `build`

### `upload.sh`
- **Type**: Bash script wrapper
- **Features**:
  - Simplified command-line interface
  - Error handling
  - Colored output
  - Argument validation
- **Dependencies**: `python`, `upload_to_pypi.py`

### `.pypirc.template`
- **Type**: Configuration template
- **Purpose**: Template for PyPI credentials
- **Usage**: Copy to `~/.pypirc` and configure with your credentials

### `UPLOAD_README.md`
- **Type**: Documentation
- **Content**: 
  - Setup instructions
  - Usage examples
  - Troubleshooting guide
  - Best practices
  - Security notes

## Version Management

The scripts automatically handle version bumping in:
- `pyproject.toml`
- `setup.py` 
- `agno_cli/__init__.py`

## Safety Features

- **Dry-run mode**: Test without making changes
- **TestPyPI**: Upload to test environment first
- **Confirmation prompts**: Prevent accidental uploads
- **Error handling**: Comprehensive error checking
- **Prerequisites checking**: Ensure all tools are available

## Security

- Never commit `.pypirc` to version control
- Use API tokens instead of passwords
- Keep credentials secure
- Use environment variables in CI/CD

## Support

For issues or questions:
1. Check `UPLOAD_README.md` for troubleshooting
2. Run `./upload.sh --help` or `python upload_to_pypi.py --help`
3. Use `--dry-run` to test without making changes 