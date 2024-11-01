import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse
from tqdm import tqdm


class PyDownloader:
    def __init__(
        self,
        url,
        dest=None,
        folder_temp=None,
        threads_count=3,
        min_chunk_size=10 * 1024 * 1024,
    ):
        self.url = url
        self.dest = dest or Path(Path(urlparse(url).path).name)
        self.threads_count = threads_count
        self.min_chunk_size = min_chunk_size

        self.folder_temp = Path(folder_temp) if folder_temp else folder_temp
        self.progress_bar = None

        # Comprueba que la ruta de destino no tenga un punto de extensión.
        if self.folder_temp:
            if self.folder_temp.suffix:
                self.folder_temp = self.folder_temp.parent
            self.folder_temp.mkdir(parents=True, exist_ok=True)
            self.original_dest = self.dest
            self.dest = self.folder_temp / self.dest.name

        if Path(self.dest).exists():
            raise FileExistsError(f"File {self.dest} already exists")

    def download(self):
        filesize = self._get_filesize()
        chunks = self._calculate_chunks(filesize)
        self.progress_bar = tqdm(
            total=filesize, unit="B", unit_scale=True, desc="Downloading"
        )

        with ThreadPoolExecutor(max_workers=self.threads_count) as executor:
            futures = [
                executor.submit(self._download_chunk, chunk, i)
                for i, chunk in enumerate(chunks)
            ]

            for future in as_completed(futures):
                future.result()

        self.progress_bar.close()
        self._combine_files(len(chunks))

    def _get_filesize(self):
        response = requests.head(self.url)
        response.raise_for_status()
        return int(response.headers.get("Content-Length", 0))

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
        self.dest.parent.mkdir(parents=True, exist_ok=True)
        start, end = chunk
        headers = {"Range": f"bytes={start}-{end}"}
        response = requests.get(self.url, headers=headers, stream=True)
        response.raise_for_status()

        chunk_file = Path(f"{self.dest}.part{index}")
        with chunk_file.open("wb") as f:
            for data in response.iter_content(chunk_size=8192):
                f.write(data)
                self.progress_bar.update(len(data))

        return chunk_file

    def _combine_files(self, num_chunks, buffer_size=1024 * 1024 * 50):
        with Path(self.dest.with_suffix(".temp")).open("wb") as f:
            for i in range(num_chunks):
                chunk_file = Path(f"{self.dest}.part{i}")
                with chunk_file.open("rb") as f2:
                    data = f2.read(buffer_size)
                    while data:
                        f.write(data)
                        data = f2.read(buffer_size)
                chunk_file.unlink()

        if self.folder_temp:
            self.original_dest.parent.mkdir(parents=True, exist_ok=True)
            self.dest.rename(self.original_dest)

        self.dest.with_suffix(".temp").rename(self.dest)


if __name__ == "__main__":
    url = "https://ftp.nluug.nl/pub/graphics/blender/demo/movies/Sintel.2010.1080p.mkv"
    downloader = PyDownloader(url, folder_temp="tmp")
    downloader.download()
