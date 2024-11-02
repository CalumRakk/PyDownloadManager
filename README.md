# PyDownloadManager (PyDM)

PyDownloadManager (**PyDM**) es un simple acelerador de descargas escrito en Python diseñado para mejorar la velocidad de descarga en conexiones lentas. Permite descargar archivos en múltiples partes simultáneamente.

## Instalación

Abra el shell del sistema y ejecute el siguiente comando:

```shell
pip install git+https://github.com/CalumRakk/PyDownloadManager.git
```

## Ejemplo

El siguiente ejemplo muestra cómo descargar un archivo desde una URL y guardarlo en el directorio especificado (output) al finalizar la descarga:

```python
from pydm import PyDM

url = "https://www.peach.themazzone.com/durian/movies/sintel-2048-surround.mp4"
downloader = PyDM(url, output=r"D:\temp")
downloader.download()
```
