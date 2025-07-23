#!/usr/bin/env python3
"""
PyPI Upload Script for agno_cli

This script automates the process of building and uploading the agno_cli package to PyPI.
It includes version management, testing, and safety checks.
"""

import os
import sys
import subprocess
import re
import json
import shutil
from pathlib import Path
from typing import Optional, Tuple, List
import argparse


class PyPIUploader:
    def __init__(self, test_pypi: bool = False, dry_run: bool = False):
        self.test_pypi = test_pypi
        self.dry_run = dry_run
        self.project_root = Path(__file__).parent
        self.package_name = "agno_cli"
        
        # PyPI URLs
        self.pypi_url = "https://test.pypi.org/legacy/" if test_pypi else "https://upload.pypi.org/legacy/"
        self.pypi_name = "testpypi" if test_pypi else "pypi"
        
        # Colors for output
        self.colors = {
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'purple': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'bold': '\033[1m',
            'end': '\033[0m'
        }
    
    def print_colored(self, message: str, color: str = 'white', bold: bool = False):
        """Print colored output"""
        color_code = self.colors.get(color, '')
        bold_code = self.colors.get('bold', '') if bold else ''
        print(f"{bold_code}{color_code}{message}{self.colors['end']}")
    
    def run_command(self, command: List[str], check: bool = True, capture_output: bool = False) -> Tuple[int, str, str]:
        """Run a shell command and return exit code, stdout, stderr"""
        self.print_colored(f"Running: {' '.join(command)}", 'cyan')
        
        if self.dry_run:
            self.print_colored("DRY RUN - Command would be executed", 'yellow')
            return 0, "", ""
        
        try:
            result = subprocess.run(
                command,
                check=check,
                capture_output=capture_output,
                text=True,
                cwd=self.project_root
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return e.returncode, e.stdout or "", e.stderr or ""
    
    def check_prerequisites(self) -> bool:
        """Check if all required tools are installed"""
        self.print_colored("Checking prerequisites...", 'blue', bold=True)
        
        required_tools = ['python', 'pip', 'twine']
        missing_tools = []
        
        for tool in required_tools:
            try:
                subprocess.run([tool, '--version'], capture_output=True, check=True)
                self.print_colored(f"✓ {tool} is available", 'green')
            except (subprocess.CalledProcessError, FileNotFoundError):
                missing_tools.append(tool)
                self.print_colored(f"✗ {tool} is missing", 'red')
        
        if missing_tools:
            self.print_colored(f"Missing tools: {', '.join(missing_tools)}", 'red', bold=True)
            self.print_colored("Please install missing tools:", 'yellow')
            for tool in missing_tools:
                if tool == 'twine':
                    self.print_colored(f"  pip install {tool}", 'cyan')
                else:
                    self.print_colored(f"  Install {tool} from your system package manager", 'cyan')
            return False
        
        return True
    
    def get_current_version(self) -> Optional[str]:
        """Get current version from setup.py or pyproject.toml"""
        # Try pyproject.toml first
        pyproject_path = self.project_root / "pyproject.toml"
        if pyproject_path.exists():
            content = pyproject_path.read_text()
            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
        
        # Try setup.py
        setup_path = self.project_root / "setup.py"
        if setup_path.exists():
            content = setup_path.read_text()
            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
        
        return None
    
    def update_version(self, version_type: str = 'patch') -> Optional[str]:
        """Update version number"""
        current_version = self.get_current_version()
        if not current_version:
            self.print_colored("Could not determine current version", 'red')
            return None
        
        # Parse version
        parts = current_version.split('.')
        if len(parts) != 3:
            self.print_colored(f"Invalid version format: {current_version}", 'red')
            return None
        
        major, minor, patch = map(int, parts)
        
        # Update version based on type
        if version_type == 'major':
            major += 1
            minor = 0
            patch = 0
        elif version_type == 'minor':
            minor += 1
            patch = 0
        elif version_type == 'patch':
            patch += 1
        else:
            self.print_colored(f"Invalid version type: {version_type}", 'red')
            return None
        
        new_version = f"{major}.{minor}.{patch}"
        
        # Update files
        files_to_update = []
        
        # Update pyproject.toml
        pyproject_path = self.project_root / "pyproject.toml"
        if pyproject_path.exists():
            content = pyproject_path.read_text()
            new_content = re.sub(
                r'version\s*=\s*["\'][^"\']+["\']',
                f'version = "{new_version}"',
                content
            )
            pyproject_path.write_text(new_content)
            files_to_update.append("pyproject.toml")
        
        # Update setup.py
        setup_path = self.project_root / "setup.py"
        if setup_path.exists():
            content = setup_path.read_text()
            new_content = re.sub(
                r'version\s*=\s*["\'][^"\']+["\']',
                f'version="{new_version}"',
                content
            )
            setup_path.write_text(new_content)
            files_to_update.append("setup.py")
        
        # Update __init__.py
        init_path = self.project_root / "agno_cli" / "__init__.py"
        if init_path.exists():
            content = init_path.read_text()
            new_content = re.sub(
                r'__version__\s*=\s*["\'][^"\']+["\']',
                f'__version__ = "{new_version}"',
                content
            )
            init_path.write_text(new_content)
            files_to_update.append("agno_cli/__init__.py")
        
        self.print_colored(f"Updated version from {current_version} to {new_version}", 'green')
        self.print_colored(f"Updated files: {', '.join(files_to_update)}", 'cyan')
        
        return new_version
    
    def clean_build_artifacts(self):
        """Clean previous build artifacts"""
        self.print_colored("Cleaning build artifacts...", 'blue')
        
        dirs_to_clean = ['build', 'dist', '*.egg-info']
        for pattern in dirs_to_clean:
            for path in self.project_root.glob(pattern):
                if path.is_dir():
                    shutil.rmtree(path)
                    self.print_colored(f"Removed: {path}", 'yellow')
                elif path.is_file():
                    path.unlink()
                    self.print_colored(f"Removed: {path}", 'yellow')
    
    def run_tests(self) -> bool:
        """Run tests to ensure package quality"""
        self.print_colored("Running tests...", 'blue', bold=True)
        
        # Check if tests directory exists
        tests_dir = self.project_root / "tests"
        if not tests_dir.exists():
            self.print_colored("No tests directory found, skipping tests", 'yellow')
            return True
        
        # Run pytest if available
        try:
            exit_code, stdout, stderr = self.run_command(['python', '-m', 'pytest', 'tests/'], check=False)
            if exit_code == 0:
                self.print_colored("✓ All tests passed", 'green')
                return True
            else:
                self.print_colored("✗ Tests failed", 'red')
                if stdout:
                    print(stdout)
                if stderr:
                    print(stderr)
                return False
        except FileNotFoundError:
            self.print_colored("pytest not found, skipping tests", 'yellow')
            return True
    
    def build_package(self) -> bool:
        """Build the package"""
        self.print_colored("Building package...", 'blue', bold=True)
        
        # Build using build module (modern approach)
        exit_code, stdout, stderr = self.run_command(['python', '-m', 'build'], check=False)
        
        if exit_code != 0:
            self.print_colored("✗ Build failed", 'red')
            if stdout:
                print(stdout)
            if stderr:
                print(stderr)
            return False
        
        self.print_colored("✓ Package built successfully", 'green')
        return True
    
    def check_distribution(self) -> bool:
        """Check the built distribution"""
        self.print_colored("Checking distribution...", 'blue')
        
        dist_dir = self.project_root / "dist"
        if not dist_dir.exists():
            self.print_colored("✗ No dist directory found", 'red')
            return False
        
        # Check for wheel and source distribution
        wheel_files = list(dist_dir.glob("*.whl"))
        source_files = list(dist_dir.glob("*.tar.gz"))
        
        if not wheel_files and not source_files:
            self.print_colored("✗ No distribution files found", 'red')
            return False
        
        self.print_colored(f"✓ Found {len(wheel_files)} wheel(s) and {len(source_files)} source distribution(s)", 'green')
        return True
    
    def upload_to_pypi(self) -> bool:
        """Upload package to PyPI"""
        self.print_colored(f"Uploading to {self.pypi_name.upper()}...", 'blue', bold=True)
        
        # Check if credentials are available
        if not self.check_pypi_credentials():
            return False
        
        # Upload using twine
        exit_code, stdout, stderr = self.run_command([
            'twine', 'upload', '--repository', self.pypi_name, 'dist/*'
        ], check=False)
        
        if exit_code != 0:
            self.print_colored(f"✗ Upload to {self.pypi_name} failed", 'red')
            if stdout:
                print(stdout)
            if stderr:
                print(stderr)
            return False
        
        self.print_colored(f"✓ Successfully uploaded to {self.pypi_name}", 'green', bold=True)
        return True
    
    def check_pypi_credentials(self) -> bool:
        """Check if PyPI credentials are configured"""
        # Check for environment variables
        username = os.getenv('PYPI_USERNAME') or os.getenv('TWINE_USERNAME')
        password = os.getenv('PYPI_PASSWORD') or os.getenv('TWINE_PASSWORD')
        
        if username and password:
            self.print_colored("✓ PyPI credentials found in environment variables", 'green')
            return True
        
        # Check for .pypirc file
        pypirc_path = Path.home() / ".pypirc"
        if pypirc_path.exists():
            self.print_colored("✓ Found .pypirc configuration file", 'green')
            return True
        
        self.print_colored("✗ No PyPI credentials found", 'red')
        self.print_colored("Please set up credentials using one of these methods:", 'yellow')
        self.print_colored("1. Environment variables: PYPI_USERNAME and PYPI_PASSWORD", 'cyan')
        self.print_colored("2. .pypirc file in your home directory", 'cyan')
        self.print_colored("3. Interactive prompt during upload", 'cyan')
        return True  # Allow interactive prompt
    
    def show_upload_info(self):
        """Show information about the upload"""
        version = self.get_current_version()
        self.print_colored("\n" + "="*60, 'blue')
        self.print_colored("PYPI UPLOAD SUMMARY", 'blue', bold=True)
        self.print_colored("="*60, 'blue')
        self.print_colored(f"Package: {self.package_name}", 'white')
        self.print_colored(f"Version: {version}", 'white')
        self.print_colored(f"Target: {self.pypi_name.upper()}", 'white')
        self.print_colored(f"URL: {self.pypi_url}", 'white')
        self.print_colored(f"Dry run: {'Yes' if self.dry_run else 'No'}", 'white')
        self.print_colored("="*60, 'blue')
    
    def run(self, version_type: str = 'patch', skip_tests: bool = False, force: bool = False):
        """Run the complete upload process"""
        self.show_upload_info()
        
        # Check prerequisites
        if not self.check_prerequisites():
            return False
        
        # Update version
        new_version = self.update_version(version_type)
        if not new_version:
            return False
        
        # Clean build artifacts
        self.clean_build_artifacts()
        
        # Run tests (unless skipped)
        if not skip_tests:
            if not self.run_tests():
                if not force:
                    self.print_colored("Tests failed. Use --force to continue anyway.", 'red')
                    return False
                else:
                    self.print_colored("Tests failed but continuing due to --force flag", 'yellow')
        
        # Build package
        if not self.build_package():
            return False
        
        # Check distribution
        if not self.check_distribution():
            return False
        
        # Confirm upload (unless dry run)
        if not self.dry_run:
            if not self.confirm_upload():
                self.print_colored("Upload cancelled by user", 'yellow')
                return False
        
        # Upload to PyPI
        if not self.upload_to_pypi():
            return False
        
        self.print_colored("\n🎉 Upload completed successfully!", 'green', bold=True)
        self.print_colored(f"Package: {self.package_name} v{new_version}", 'white')
        self.print_colored(f"Available at: https://pypi.org/project/{self.package_name}/", 'cyan')
        
        return True
    
    def confirm_upload(self) -> bool:
        """Ask user to confirm upload"""
        self.print_colored("\n" + "!"*60, 'yellow')
        self.print_colored("UPLOAD CONFIRMATION", 'yellow', bold=True)
        self.print_colored("!"*60, 'yellow')
        self.print_colored(f"You are about to upload {self.package_name} to {self.pypi_name.upper()}", 'white')
        self.print_colored("This action cannot be undone!", 'red', bold=True)
        
        response = input("\nDo you want to continue? (y/N): ").strip().lower()
        return response in ['y', 'yes']


def main():
    parser = argparse.ArgumentParser(
        description="Upload agno_cli package to PyPI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python upload_to_pypi.py                    # Upload with patch version bump
  python upload_to_pypi.py --minor            # Upload with minor version bump
  python upload_to_pypi.py --major            # Upload with major version bump
  python upload_to_pypi.py --test             # Upload to TestPyPI
  python upload_to_pypi.py --dry-run          # Show what would be done
  python upload_to_pypi.py --skip-tests       # Skip running tests
  python upload_to_pypi.py --force            # Continue even if tests fail
        """
    )
    
    parser.add_argument(
        '--test', '--test-pypi',
        action='store_true',
        help='Upload to TestPyPI instead of PyPI'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without actually doing it'
    )
    
    parser.add_argument(
        '--major',
        action='store_true',
        help='Bump major version (x.0.0)'
    )
    
    parser.add_argument(
        '--minor',
        action='store_true',
        help='Bump minor version (0.x.0)'
    )
    
    parser.add_argument(
        '--patch',
        action='store_true',
        help='Bump patch version (0.0.x) - default'
    )
    
    parser.add_argument(
        '--skip-tests',
        action='store_true',
        help='Skip running tests before upload'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Continue even if tests fail'
    )
    
    args = parser.parse_args()
    
    # Determine version type
    version_type = 'patch'  # default
    if args.major:
        version_type = 'major'
    elif args.minor:
        version_type = 'minor'
    elif args.patch:
        version_type = 'patch'
    
    # Create uploader and run
    uploader = PyPIUploader(test_pypi=args.test, dry_run=args.dry_run)
    success = uploader.run(
        version_type=version_type,
        skip_tests=args.skip_tests,
        force=args.force
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main() 