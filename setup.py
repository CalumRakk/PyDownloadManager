from setuptools import setup
from urlDownloader import VERSION

setup(
    name="urlDownloader",
    version=VERSION,
    description="urlDownloader is a simple download manager for Python.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    readme="README.md",
    author="Leo",
    url="https://github.com/CalumRakk/urlDownloader",
    install_requires=["requests==2.31.0"],
    packages=["urlDownloader"],
)
