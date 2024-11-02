from setuptools import setup, find_packages


def get_version(fname="pydm/version.py"):
    exec(compile(open(fname, encoding="utf-8").read(), fname, "exec"))
    return locals()["VERSION"]


setup(
    name="PyDownloadManager",
    version=get_version(),
    description="PyDownloadManager es un simple gestor de descargas para Python",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    readme="README.md",
    author="Leo",
    url="https://github.com/CalumRakk/PyDownloadManager.git",
    install_requires=["requests", "tqdm"],
    packages=find_packages(),
)
