from setuptools import setup, find_packages

# Read requirements from requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# Filter out comments and empty lines
install_requires = [line for line in requirements if line and not line.startswith('#')]

setup(
    name="poverty-alleviation-platform",
    version="0.1.0",
    packages=find_packages(where="backend"),
    package_dir={"": "backend"},
    python_requires=">=3.12",
    install_requires=install_requires,
    include_package_data=True,
    zip_safe=False,
    # Prevent setuptools from trying to build Rust extensions
    setup_requires=["setuptools>=68.2.2"],
    # Disable building platform-specific wheels
    options={
        "bdist_wheel": {
            "universal": True
        }
    },
    # Package metadata
    author="Your Name",
    author_email="your.email@example.com",
    description="Poverty Alleviation Platform - A platform to help alleviate poverty through microfinance and community support",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/poverty-alleviation-platform",
    classifiers=[
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)