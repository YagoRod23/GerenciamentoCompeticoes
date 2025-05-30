"""
Setup script para o Sistema de Gerenciamento Esportivo - Web App
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="sistema-esportivo-web",
    version="1.0.0",
    author="Sistema de Gerenciamento Esportivo",
    author_email="admin@sistema.com",
    description="Sistema web para gerenciamento de competições esportivas",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seu-usuario/sistema-esportivo",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Flask",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.2",
            "pytest-flask>=1.2.0",
            "black>=23.7.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "sistema-web=web_app.app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "web_app": [
            "templates/**/*.html",
            "static/**/*",
        ],
    },
)
