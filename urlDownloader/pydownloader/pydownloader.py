import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse
from tqdm import tqdm
import time


def get_folder_temp(folder_temp):
    # Devuelve un directorio temporal.
    # Si folder_temp es None, se devuelve un directorio temporal en el sistema temporal.
    # Si folder_temp es un archivo, se devuelve el directorio padre del archivo.
    if isinstance(folder_temp, str):
        folder_temp = Path(folder_temp)
    elif folder_temp is None:
        return Path()

    if folder_temp.suffix:
        return folder_temp.parent
    return folder_temp


def get_output(output, url):
    if isinstance(output, str):
        output = Path(output)
    elif output is None:
        filename = Path(urlparse(url).path).name
        return Path(filename)

    if output.suffix:
        return output

    filename = Path(urlparse(url).path).name
    return output / filename


def move_file(source: Path, dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if source.drive != dest.drive:
        temp_filename = dest.with_suffix(".temp")
        temp_path = dest.parent / temp_filename
        source.rename(temp_path)
        return temp_path.rename(dest)
    return source.rename(dest)


class PyDownloader:
    def __init__(
        self,
        url,
        output=None,
        folder_temp=None,
        threads_count=3,
        min_chunk_size=10 * 1024 * 1024,
    ):
        self.url = url
        self.output = output
        self.threads_count = threads_count
        self.min_chunk_size = min_chunk_size

        self.__folder_temp = folder_temp

    @property
    def content_length(self):
        # El tamaño del archivo se obtiene de la respuesta HEAD.
        if hasattr(self, "_content_length"):
            return getattr(self, "_content_length")

        response = requests.head(self.url)
        response.raise_for_status()
        content_length = int(response.headers.get("Content-Length", 0))
        setattr(self, "_content_length", content_length)
        return content_length

    @property
    def progress_bar(self):
        if hasattr(self, "_progress_bar"):
            return getattr(self, "_progress_bar")

        progress_bar = tqdm(
            total=self.content_length, unit="B", unit_scale=True, desc="Downloading"
        )
        setattr(self, "_progress_bar", progress_bar)
        return progress_bar

    @property
    def folder_temp(self):
        if hasattr(self, "_folder_temp"):
            return getattr(self, "_folder_temp")

        folder_temp = get_folder_temp(self.__folder_temp)
        folder_temp.mkdir(parents=True, exist_ok=True)
        setattr(self, "_folder_temp", folder_temp)
        return folder_temp

    def download(self):
        dest = get_output(self.output, self.url)
        if dest.exists():
            raise FileExistsError(f"{dest} already exists")

        source_temp = get_output(self.folder_temp, self.url)
        if source_temp.exists():
            return move_file(source_temp, dest)

        chunks = self._calculate_chunks(self.content_length)
        count_chunks = self._download_chunks(chunks)
        source = self._combine_chunks(count_chunks)
        return move_file(source, dest)

    def _download_chunks(self, chunks) -> int:
        with ThreadPoolExecutor(max_workers=self.threads_count) as executor:
            futures = [
                executor.submit(self._download_chunk, chunk, i)
                for i, chunk in enumerate(chunks)
            ]

            for future in as_completed(futures):
                future.result()

        self.progress_bar.close()
        return len(chunks)

    def _calculate_chunks(self, total_size):
        """
        Calcula los intervalos de chunks (bloques) que se van a dividir
        de acuerdo al tamaño total del archivo y el número de threads disponibles.

        Args:
            total_size (int): Tamaño total del archivo en bytes.

        Returns:
            list: Lista de tuplas con el rango (inicio, fin) de cada chunk.
        """

        chunk_size = max(total_size // self.threads_count, self.min_chunk_size)
        chunks = []

        for start in range(0, total_size, chunk_size):
            chunk_start = start
            chunk_end = min(start + chunk_size - 1, total_size - 1)
            chunks.append((chunk_start, chunk_end))

        return chunks

    def _download_chunk(self, chunk, index):

        start, end = chunk
        headers = {"Range": f"bytes={start}-{end}"}
        response = requests.get(self.url, headers=headers, stream=True)
        response.raise_for_status()

        filename = Path(urlparse(self.url).path).name + ".part" + str(index)
        path = self.folder_temp / filename
        with path.open("wb") as f:
            for data in response.iter_content(chunk_size=8192):
                f.write(data)
                self.progress_bar.update(len(data))

        return path

    def _combine_chunks(self, num_chunks: int, buffer_size=1024 * 1024 * 50):
        filename = Path(urlparse(self.url).path).name
        path = self.folder_temp / filename
        temp_path = path.with_suffix(".combining")

        with temp_path.open("wb") as f:
            for i in range(num_chunks):
                chunk_file = Path(f"{path}.part{i}")
                with chunk_file.open("rb") as f2:
                    data = f2.read(buffer_size)
                    while data:
                        f.write(data)
                        data = f2.read(buffer_size)
                chunk_file.unlink()
        try:
            temp_path.rename(path)
        except PermissionError:
            time.sleep(5)
            temp_path.rename(path)
        return path


if __name__ == "__main__":
    # url = "https://ftp.nluug.nl/pub/graphics/blender/demo/movies/Sintel.2010.1080p.mkv"
    url = "https://www.peach.themazzone.com/durian/movies/sintel-2048-surround.mp4"
    downloader = PyDownloader(url, output=r"D:\temp")
    downloader.download()
