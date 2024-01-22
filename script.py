import requests
from math import ceil
from pathlib import Path
import threading
from queue import Queue


def calc_chunk_size(filesize, threads_count: int, minChunkFile):
    if ceil(filesize / threads_count) < minChunkFile:
        threads_count = 1
    chunks = []
    pos = 0
    chunk = ceil(filesize / threads_count)
    for i in range(threads_count):
        startByte = pos
        endByte = pos + chunk
        if endByte > filesize - 1:
            # Se resta menos 1 porque en http range el valor cero se tiene encuenta como un byte <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Range>
            endByte = filesize - 1
        chunks.append((startByte, endByte))
        pos += chunk + 1
    return chunks


def descargar_enlace(url, part, resultados, index):
    print(f"thread {index} iniciado")
    inicio = part[0]
    fin = part[1]
    headers = {"Range": f"bytes={inicio}-{fin}"}
    count = 0
    path_new = path.with_name(f"{path}-{index}" + path.suffix)
    block_sz = 8192
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


headers2 = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
}

# url = "https://ash-speed.hetzner.com/100MB.bin"
# url = "https://link.testfile.org/aYr11v"
# url = "http://212.183.159.230/1GB.zip"
url = "https://ddz4ak4pa3d19.cloudfront.net/a1/a1f27f61a697690e0b7ad3d7a83861abf1b99bbe/a1f27f61a697690e0b7ad3d7a83861abf1b99bbe-1080p.mp4?Expires=1705916871&Signature=UjSrUofclw6Ou7wLm4gn5YY82FNN-2wFx4kk88HiLRhvE5aSdISKZHn66lGjQ0AP85IaO-RbETvxsPDEnnfgaKqpA2gdsssJD2OZxXo0uO5eQ6kroI7ZlV61KzLs38~1hdkdZKmR2R2cfs2R56Ce3K7uNDgFbpAK~7O32QcfLMGYi7zFb0C7CW-CLCHiUp3FdLc9UM~sobnsbVSPKPktsbhyFhPHW6o1XZsNvBxabzv8cnZGDSLLujspSq0ZK9O1iNrIhzBtbreEpSeixAiw-zWIBIyXOxi1ajipjncp48OaiNl1q4A~uWNj-l3OFV0xfvHHP3ZsnoRfx8LslEHG5g__&Key-Pair-Id=APKAJZFE4UDHH3WZXVDA"
threads_count = 1
threads = []
minChunkFile = 1024**2 * 2  # 2MB
response = requests.get(url, headers=headers2, stream=True)
path = Path("file.bin")
resultados = Queue()
try:
    filesize = int(response.headers["Content-Length"])
    print("Content-Length is {} ({}).".format(filesize, filesize))
except (IndexError, KeyError, TypeError):
    print("Server did not send Content-Length. Filesize is unknown.")
    filesize = 0
chunks = calc_chunk_size(filesize, threads_count, minChunkFile)


for index, arg in enumerate(range(0, threads_count)):
    thread = threading.Thread(
        target=descargar_enlace, args=(url, chunks[index], resultados, index)
    )
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()


while not resultados.empty():
    resultado = resultados.get()
    status_code, path_r = resultado
    if status_code is not None:
        print(
            f"Descarga exitosa. Status Code: {status_code}. Tamaño del contenido: {path_r.name} bytes"
        )
    else:
        print(f"Error al descargar")
