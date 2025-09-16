from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="poverty_alleviation_api",
    version="0.1.0",
    packages=find_packages(include=['app*']),
    install_requires=requirements,
    python_requires='>=3.9',
    author="Your Name",
    author_email="your.email@example.com",
    description="Poverty Alleviation Platform API",
    url="https://github.com/yourusername/poverty-alleviation-platform",
)
