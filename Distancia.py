import os
import re
import sys
import time
from typing import List

from scipy.spatial import distance


def distancia_l1(v1: List[int], v2: List[int]) -> float:
    """
    Calcula a distancia L1 entre 2 vectores (deben ser del mismo largo).

    :param v1: vector de largo n.
    :param v2: vector de largo n.

    :return: la distancia L1 entre v1 y v2.
    """

    return distance.cityblock(v1, v2)


def distancia_l2(v1: List[int], v2: List[int]) -> float:
    """
    Calcula a distancia L2 entre 2 vectores (deben ser del mismo largo).

    :param v1: vector de largo n.
    :param v2: vector de largo n.

    :return: la distancia L2 entre v1 y v2.
    """
    return distance.euclidean(v1, v2)


class Video:
    def __init__(self, nombre: str, frames: List[List[int]], tiempo: List[float]):
        self.nombre = nombre
        self.frames = frames
        self.tiempo = tiempo


def leer_video(archivo: str) -> Video:
    """
    Lee un archivo con las características de un video, cada linea contiene n + 1 números separados por espacios,
    el primero es el tiempo del frame y después vienen n enteros correspondientes a las características del frame.

    :param archivo: La dirección del archivo.

    :return: un objeto de la clase Video con el nombre del video, los frames y los tiempos.
    """

    nombre = re.split('[/.]', archivo)[-2]

    frames = []
    tiempo = []

    with open(archivo, "r") as log:
        for linea in log:
            datos = linea.split(" ")
            tiempo.append(float(datos[0]))
            frames.append([int(x) for x in datos[1:]])

    return Video(nombre, frames, tiempo)


def leer_videos(carpeta: str) -> List[Video]:
    """
    Lee las caracteristicas de todos los archivos dentro de la carpeta especificada
    y los retorna en un arreglo.

    :param carpeta: la carpeta desde la cuál obtener todos los videos.

    :return: una lista de Videos.
    """

    # obtener todos los archivos en la carpeta
    archivos = os.listdir(carpeta)
    videos = []

    # extraer la caracteristicas de cada comercial
    for video in archivos:
        videos.append(leer_video('%s/%s' % (carpeta, video)))

    return videos


class Frame:
    def __init__(self, comercial, indice, distancia):
        self.comercial = comercial
        self.indice = indice
        self.distancia = distancia


def insertar_min_frame(lista: List[Frame], frame: Frame):
    """
    Inserta un frame en una lista que mantiene los k frames con menores distancias ordenados (el frame solo se inserta
    si su distancia es menor a alguna de las distancias actuales).

    :param lista: lista de Frames.
    :param frame: Frame a insertar.
    """

    # si elemento es mayor al máximo actual se termina inmediatamente
    if frame.distancia > lista[-1].distancia:
        return

    # insertar de manera ordenada usando lógica de insertion sort
    i = len(lista) - 1
    while i > 0 and lista[i - 1].distancia > frame.distancia:
        lista[i] = lista[i - 1]
        i -= 1

    lista[i] = frame
    return


def frames_mas_cercanos_frame(frame: List[int], videos: List[Video], k: int = 5, funcion=distancia_l1) -> List[Frame]:
    """
    Encuentra los k frames más cercanos al frame dado, dentro de todos los frames en una lista de Videos.

    :param frame: el frame del cuál buscar frames cercanos.
    :param videos: una lista de Videos en los cuáles buscar frames cercanos.
    :param k: el número de frames cercanos a buscar.
    :param funcion: la función para calcular la distancia entre 2 vectores de ints.

    :return: una lista de Frames.
    """
    distancia_inf = Frame('', -1, 1000000000)
    cercanos = [distancia_inf for _ in range(k)]

    # buscar los frames más cercanos entre todos los frames de los videos.
    for video in videos:
        for i in range(len(video.frames)):
            dist = funcion(frame, video.frames[i])
            insertar_min_frame(cercanos, Frame(video.nombre, i, dist))

    return cercanos


def frames_mas_cercanos_video(archivo: str, videos: List[Video], carpeta_log: str, k: int = 5, funcion=distancia_l1):
    """
    Encuentra los k frames más cercanos a cada frame del video dado, dentro de todos los frames en una lista de Videos,
    registra esta información en un log txt.

    :param archivo: el archivo del cuál buscar frames cercanos.
    :param videos: una lista de Videos en los cuáles buscar frames cercanos.
    :param carpeta_log: la carpeta en la cual guardar el log.
    :param k: el número de frames cercanos a buscar.
    :param funcion: la función para calcular la distancia entre 2 vectores de ints.
    """

    # medir tiempo
    t0 = time.time()

    # leer caracteristicas del video
    video = leer_video(archivo)

    # abrir log
    nombre = re.split('[/.]', archivo)[-2]
    if not os.path.isdir(carpeta_log):
        os.mkdir(carpeta_log)
    log = open(f'{carpeta_log}/{nombre}.txt', 'w')

    print(f'buscando {k} frames más cercanos para {nombre}')

    # buscar los frames más cercanos de cada frame
    for i in range(len(video.frames)):
        cercanos = frames_mas_cercanos_frame(video.frames[i], videos, k=k, funcion=funcion)
        cercanos_str = ' | '.join([f'{frame.comercial} # {frame.indice}' for frame in cercanos])

        # registrar resultado
        log.write(f'{video.tiempo[i]} $ {cercanos_str}\n')

        if i % 500 == 0 and i != 0:
            print(f'progreso: {i} frames, {int(time.time() - t0)} segundos')

    log.close()
    print(f'la búsqueda de {k} frames más cercanos tomó {int(time.time() - t0)} segundos')
    return


def main(archivo: str, k: int, funcion):
    """
    Encuentra los k frames más cercanos a cada frame del video dado, dentro de todos los frames en una lista de Videos,
    registra esta información en un log txt en la carpeta television_cercanos/.

    :param archivo: el nombre del video de television del cuál buscar frames cercanos.
    :param k: el número de frames cercanos a buscar.
    :param funcion: la función para calcular la distancia entre 2 vectores de ints.
    """

    comerciales = leer_videos('comerciales_car')
    frames_mas_cercanos_video(f'television_car/{archivo}.txt', comerciales, 'television_cercanos', k, funcion)
    return


if __name__ == '__main__':
    nombre_video = ''

    if len(sys.argv) == 1:
        nombre_video = 'mega-2014_04_10'
    elif len(sys.argv) == 2:
        nombre_video = sys.argv[1]
    else:
        print(f'Uso: {sys.argv[0]} nombre_video (sin extensión)\n por ejemplo: {sys.argv[0]} mega-2014_04_10')
        exit(1)

    # cantidad de frames cercanos a buscar
    numero_de_cercanos = 5

    # funcion de distancia a utilizar
    funcion_de_distancia = distancia_l2

    main(nombre_video, numero_de_cercanos, funcion_de_distancia)
