urlDownloader es un simple administrador de descarga para Python.

Las principales funcionalidades son:

- [x] Descargar archivos en conexiones lentas.
- [x] Aceleración de descargas en el sentido de dividir un archivo en partes y descargarlas simultáneamente para aumentar la velocidad de descarga.
- [ ] Evitar que la descarga se corrompa si hay una desconexión accidental.
- [ ] Establecer un limite de velocidad a la descarga

## Instalación

Abre el shell del sistema y ejecuta el siguiente comando:

```shell
pip install git+https://github.com/CalumRakk/urlDownloader
```

## Ejemplo

El siguiente código descarga un archivo y lo guarda en la ubicación donde se ejecute el script

```python
from urlDownloader import urlDownloader

url = "https://v3.cdnpk.net/videvo_files/video/free/2018-09/originalContent/180824_TheEarth_36.mp4"
urlDL = urlDownloader(url)
urlDL.download()
```
