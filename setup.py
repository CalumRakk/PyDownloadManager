from setuptools import setup, find_packages


def get_version(fname="urlDownloader/version.py"):
    exec(compile(open(fname, encoding="utf-8").read(), fname, "exec"))
    return locals()["VERSION"]


setup(
    name="urlDownloader",
    version=get_version(),
    description="urlDownloader is a simple download manager for Python.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    readme="README.md",
    author="Leo",
    url="https://github.com/CalumRakk/urlDownloader",
    install_requires=["requests"],
    packages=find_packages(),
)
