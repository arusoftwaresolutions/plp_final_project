from setuptools import setup, find_packages
from pathlib import Path

# Read requirements from requirements.txt
with open('requirements.txt') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read the README for the long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="poverty_alleviation_api",
    version="0.1.0",
    packages=find_packages(where='.'),
    package_dir={"": "."},
    install_requires=requirements,
    python_requires='>=3.9',
    author="Your Name",
    author_email="your.email@example.com",
    description="Poverty Alleviation Platform API",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/yourusername/poverty-alleviation-platform",
    include_package_data=True,
    zip_safe=False,
)
