from math import ceil
from queue import Queue
from pathlib import Path

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
}


def calcular_chunk_size(
    filesize,
    threads_count: int,
    minChunkFile,
) -> list[tuple[int, int]]:
    if ceil(filesize / threads_count) < minChunkFile:
        threads_count = 1
    chunks = []
    pos = 0
    chunk = ceil(filesize / threads_count)
    for index in range(threads_count):
        startByte = pos
        endByte = pos + chunk
        if endByte > filesize - 1:
            # Se resta menos 1 porque en http range el valor cero se tiene encuenta como un byte <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Range>
            endByte = filesize - 1
        chunks.append((startByte, endByte))
        pos += chunk + 1
    return chunks


def combine_files(results: Queue[tuple[int, int, Path]], dest):
    chunkSize = 1024 * 1024 * 20
    files = []
    while not results.empty():
        result = results.get()
        files.append(result)

    files_sorted = sorted(files, key=lambda x: x[0])
    first_part: Path = files_sorted.pop(0)[2]
    with open(first_part, "ab") as output:
        for file in files_sorted:
            path: Path = file[2]
            with open(path, "rb") as input:
                data = input.read(chunkSize)
                while data:
                    output.write(data)
                    data = input.read(chunkSize)
            path.unlink()
    first_part.rename(dest)
