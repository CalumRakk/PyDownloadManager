urlDownloader is a simple download manager for Python.

Key features include:

- [x] Download files on slow connections.
- [x] Download acceleration by splitting a file into parts and downloading them simultaneously to increase download speed.
- [ ] Prevent the download from being corrupted if there is an accidental disconnection.
- [ ] Set a download speed limit.

## Installing

Open the system shell and run the following command:

```shell
pip install git+https://github.com/CalumRakk/urlDownloader
```

## Example

The following code downloads a file and saves it in the location where the script is executed:

```python
from urlDownloader import urlDownloader

url = "https://v3.cdnpk.net/videvo_files/video/free/2018-09/originalContent/180824_TheEarth_36.mp4"
urlDL = urlDownloader(url)
urlDL.download()
```
