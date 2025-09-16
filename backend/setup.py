from setuptools import setup, find_packages

# Minimal setup configuration
setup(
    name="poverty_alleviation_api",
    version="0.1.0",
    packages=find_packages(where='.'),
    package_dir={"": "."},
    python_requires='>=3.9',
    install_requires=[
        # Core dependencies
        'fastapi>=0.68.0',
        'uvicorn>=0.15.0',
        'sqlalchemy>=1.4.0',
        'pydantic>=1.8.0',
        'python-jose[cryptography]>=3.3.0',
        'passlib[bcrypt]>=1.7.4',
        'python-multipart>=0.0.5',
        'email-validator>=1.1.3',
        'python-dotenv>=0.19.0',
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="Poverty Alleviation Platform API",
    long_description="Poverty Alleviation Platform API",
    long_description_content_type='text/plain',
    url="https://github.com/yourusername/poverty-alleviation-platform",
    include_package_data=True,
    zip_safe=False,
)
