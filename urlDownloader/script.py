import requests
from queue import Queue
import threading
from .utils import headers, calcular_chunk_size, combine_files
from pathlib import Path
from urllib.parse import urlparse


class urlDownloader:
    def __init__(
        self,
        url,
        dest: Path = None,
        headers=headers,
        threads_count: int = 3,
        minChunkFile=None,
    ):
        self.url = url
        if type(dest) is str:
            dest = Path(dest)
        self.dest = dest or Path(Path(urlparse(url).path).name)
        self.headers = headers
        self.threads_count = threads_count
        self.minChunkFile = minChunkFile or 1024 * 1024 * 10  # 10MB

    def download(self):
        manager = ThreadManager(**self.__dict__)
        result = manager.multi_threaded_download()
        combine_files(result, self.dest)


class ThreadManager(urlDownloader):
    def _get_filesize(self, url):
        response = requests.get(url, headers=self.headers, stream=True)
        response.raise_for_status()
        filesize = int(response.headers["Content-Length"])
        return filesize

    def _download_chunk(self, url: str, chunk, resultados, index):
        inicio = chunk[0]
        fin = chunk[1]
        headers = {"Range": f"bytes={inicio}-{fin}"}
        count = 0
        path_new = self.dest.with_name(f"{self.dest}-{index}" + self.dest.suffix)
        block_sz = 16384
        with open(path_new, "wb") as archivo:
            response = requests.get(url, headers=headers, stream=True)
            while True:
                for chunk in response.iter_content(chunk_size=block_sz):
                    if chunk:
                        count += len(chunk)
                        archivo.write(chunk)
                        print(f"Wrote {count} bytes.")
                break
        return resultados.put((response.status_code, path_new))

    def multi_threaded_download(self) -> Queue[tuple[int, Path]]:
        filesize = self._get_filesize(self.url)
        chunks = calcular_chunk_size(
            filesize=filesize,
            threads_count=self.threads_count,
            minChunkFile=self.minChunkFile,
        )
        resultados = Queue()
        threads = []
        for i in range(0, self.threads_count):
            thread = threading.Thread(
                target=self._download_chunk,
                args=(self.url, chunks[i], resultados, i),
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        return resultados
