from setuptools import setup, find_packages

setup(
    name="genlayer-price-oracle",
    version="1.0.0",
    description="CoinGecko price oracle integration library for GenLayer Intelligent Contracts",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your@email.com",
    url="https://github.com/your-username/genlayer-price-oracle",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=[],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
    ],
    keywords="genlayer, intelligent contract, coingecko, price oracle, blockchain, defi",
)
