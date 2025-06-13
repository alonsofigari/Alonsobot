from setuptools import setup, find_packages

setup(
    name="bybit_bot",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "flask==3.0.3",
        "pybit==2.3.1",
        "requests==2.31.0",
        "gunicorn==21.2.0"
    ]
)
