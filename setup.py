"""
Setup script for Agno CLI SDK
"""

from setuptools import setup, find_packages

setup(
    name="agno-cli",
    version="2.4.3",
    description="A Python SDK CLI that wraps around Agno AI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Paul Gedeon",
    url="https://github.com/paulgg-code/agno-cli",
    packages=find_packages(),
    install_requires=[
        "agno>=1.7.0",
        "typer>=0.9.0",
        "rich>=13.0.0",
        "pyyaml>=6.0",
        "anthropic>=0.25.0",
        "openai>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "agno=agno_cli.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    keywords="ai cli assistant agno llm chatbot",
)

