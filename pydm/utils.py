from pathlib import Path
from urllib.parse import urlparse


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
