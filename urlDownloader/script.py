import requests
from queue import Queue
import threading
from .utils import HEADERS, calcular_chunk_size, combine_files
from pathlib import Path
from urllib.parse import urlparse
from urllib.error import ContentTooShortError
from requests.exceptions import ChunkedEncodingError


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
        results, folder_temp = manager.multi_threaded_download(block=True)
        combine_files(results, self.dest)
        folder_temp.rmdir()

    def start(self):
        manager = ThreadManager(**self.__dict__)
        manager.multi_threaded_download(block=False)


def download(url, fin, inicio, count, path, block_sz, headers, archivo, index):
    with requests.get(url, headers=headers, stream=True) as response:
        response.raise_for_status()
        while True:
            for chunk in response.iter_content(chunk_size=block_sz):
                if chunk:
                    count += len(chunk)
                    archivo.write(chunk)
            break
        if not count == fin - inicio + 1:
            path.unlink()
            raise ContentTooShortError(
                f" Hilo {index} : El servidor envio menos bytes de los requeridos"
            )
        return response


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

        count_ChunkedEncodingError = 0
        while True:
            try:
                with open(path, "wb") as archivo:
                    response = download(
                        url, fin, inicio, count, path, block_sz, headers, archivo, index
                    )
                break
            except ChunkedEncodingError as e:
                print(e)
                if count_ChunkedEncodingError < 2:
                    count_ChunkedEncodingError += 1
                    continue
                else:
                    print("count_ChunkedEncodingError se ha generado dos veces")
                    exit()
        return resultados.put((index, response.status_code, path))

    def multi_threaded_download(
        self, block=True
    ) -> tuple[Queue[tuple[int, int, Path]], Path]:
        filesize = self._get_filesize(self.url)
        chunks = calcular_chunk_size(
            filesize=filesize,
            threads_count=self.threads_count,
            minChunkFile=self.minChunkFile,
        )
        self._resultados = Queue()
        self._threads = []
        self._folder = self.dest.parent / "temp"
        self._folder.mkdir(exist_ok=True)
        for index in range(0, self.threads_count):
            name = self.dest.with_name(f"{self.dest.stem}-{index}")
            filename = name.with_suffix(self.dest.suffix)
            path = self._folder / filename
            thread = threading.Thread(
                target=self._download_chunk,
                args=(self.url, chunks[index], self._resultados, index, path),
            )
            self._threads.append(thread)
            thread.start()
        if block:
            for thread in self._threads:
                thread.join()

        return self._resultados, self._folder
