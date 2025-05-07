"""
Setup script for DealFinder AI package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dealfinder-ai",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A chatbot that finds the best deals across multiple shopping sites",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/dealfinder-ai",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Consumers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
        "lxml>=4.9.0",
        "google-generativeai>=0.3.0",
        "python-dotenv>=1.0.0",
        "rich>=12.0.0",
        "Flask>=2.2.0",
    ],
    entry_points={
        "console_scripts": [
            "dealfinder=dealfinder.main:main",
        ],
    },
)