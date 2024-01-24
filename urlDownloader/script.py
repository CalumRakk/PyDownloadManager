import requests
from queue import Queue
import threading
from .utils import HEADERS, calcular_chunk_size, combine_files
from pathlib import Path
from urllib.parse import urlparse


class urlDownloader:
    def __init__(
        self,
        url,
        dest: Path = None,
        headers=None,
        threads_count: int = 3,
        minChunkFile=None,
    ):
        self.url = url
        if type(dest) is str:
            dest = Path(dest)
        self.dest = dest or Path(Path(urlparse(url).path).name)
        self.headers = headers or HEADERS
        self.threads_count = threads_count
        self.minChunkFile = minChunkFile or 1024 * 1024 * 10  # 10MB

    def download(self):
        manager = ThreadManager(**self.__dict__)
        results, folder_temp = manager.multi_threaded_download()
        combine_files(results, self.dest)
        folder_temp.rmdir()


class ThreadManager(urlDownloader):
    def _get_filesize(self, url):
        response = requests.get(url, headers=self.headers, stream=True)
        response.raise_for_status()
        filesize = int(response.headers["Content-Length"])
        return filesize

    def _download_chunk(self, url: str, chunk, resultados, index, path):
        inicio = chunk[0]
        fin = chunk[1]
        headers = {"Range": f"bytes={inicio}-{fin}"}
        count = 0
        block_sz = 16384
        with open(path, "wb") as archivo:
            response = requests.get(url, headers=headers, stream=True)
            while True:
                for chunk in response.iter_content(chunk_size=block_sz):
                    if chunk:
                        count += len(chunk)
                        archivo.write(chunk)
                break
        return resultados.put((index, response.status_code, path))

    def multi_threaded_download(self) -> tuple[Queue[tuple[int, int, Path]], Path]:
        filesize = self._get_filesize(self.url)
        chunks = calcular_chunk_size(
            filesize=filesize,
            threads_count=self.threads_count,
            minChunkFile=self.minChunkFile,
        )
        resultados = Queue()
        threads = []
        folder = self.dest.parent / "temp"
        folder.mkdir(exist_ok=True)
        for index in range(0, self.threads_count):
            name = self.dest.with_name(f"{self.dest.stem}-{index}")
            filename = name.with_suffix(self.dest.suffix)
            path = folder / filename
            thread = threading.Thread(
                target=self._download_chunk,
                args=(self.url, chunks[index], resultados, index, path),
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        return resultados, folder
