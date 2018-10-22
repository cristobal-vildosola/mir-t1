import re
import sys
from typing import List, Tuple, Dict

from Distancia import Frame, leer_videos


class Cercanos:
    def __init__(self, tiempo: float, frames: List[Frame]):
        self.tiempo = tiempo
        self.frames = frames


def leer_cercanos(archivo: str) -> List[Cercanos]:
    """
    Lee un archivo que contiene los frames más cercanos a cada frame de un video. Cada linea debe tener el siguiente
    formato: 'tiempo $ comercial # indice | comercial # indice | ...'.

    :param archivo: nombre del archivo que contiene la información

    :return: una lista de Cercanos, objeto que almacena la información de una linea.
    """
    cercanos = []

    with open(archivo, 'r') as log:
        for linea in log:
            # separar tiempo de los frames.
            tiempo, datos = linea.split(' $ ')

            # parsear tiempo y separar frames.
            tiempo = float(tiempo)
            datos = datos.split(' | ')

            # parsear frames.
            frames = []
            for dato in datos:
                comercial, indice = dato.split(' # ')
                frames.append(Frame(comercial=comercial, indice=int(indice), distancia=0))

            # agregar linea parseada a la lista
            cercanos.append(Cercanos(frames=frames, tiempo=tiempo))

    return cercanos


def contar_frames_comerciales() -> Dict[str, int]:
    """
    Lee las caracteristicas de los comerciales para encontrar el número de frames de cada uno.

    :return: Un diccionario vinculando nombre de comercial con número de frames.
    """

    comerciales = leer_videos('comerciales_car')

    numero_frames = dict()
    for comercial in comerciales:
        numero_frames[comercial.nombre] = len(comercial.frames)

    return numero_frames


def buscar_inicio(frames: List[Frame], maximo_inicial: int = 2) -> Tuple[int, str]:
    """
    Busca un frame inicial entre los frames cercanos. Este frame debe tener indice entre 0 y maximo_inicial,
    se retorna el que tenga menor indice en caso de haber más de uno que cumpla la condición.

    :param frames: lista de frames cercanos.
    :param maximo_inicial: índice inicial máximo permitido.

    :return: retorna el nombre del comercial y el indice.
    """
    comercial = ''
    indice = maximo_inicial + 1

    # buscar frame con mínimo índice.
    for frame in frames:
        if frame.indice <= maximo_inicial and frame.indice < indice:
            indice = frame.indice
            comercial = frame.comercial

    # no se encontró ningún frame inicial.
    if indice == maximo_inicial + 1:
        return -1, ''

    return indice, comercial


def buscar_indice(comercial: str, indice: int, frames: List[Frame], rango: int = 1) -> bool:
    """
    Busca un índice para un comercial en una lista de cercanos. Acepta cualquier indice dentro
    de [indice - rango, indice + rango].

    :param comercial: nombre del comercial a buscar.
    :param indice: índice a buscar.
    :param frames: lista de frames en la que buscar.
    :param rango: rango de flexibilidad para buscar el frame

    :return: True si encuentra el frame, False si no.
    """

    for frame in frames:
        if comercial == frame.comercial and (frame.indice - rango) <= indice <= (frame.indice + rango):
            return True

    # indice no encontrado.
    return False


class Candidato:
    def __init__(self, nombre: str, indice: int, tiempo_inicio: float):
        self.nombre = nombre
        self.indice = indice
        self.tiempo_inicio = tiempo_inicio
        self.errores = 0


def buscar_comerciales(archivo: str, max_porc_error: float = 0.2):
    """
    Busca comerciales en un archivo que contiene los k frames más cercanos a cada frame de un video y los registra en
    un archivo 'respuesta.txt'

    :param archivo: la ubicación del archivo.
    :param max_porc_error: máximo porcentaje de error que puede haber en una detección.
    """

    # nombre del video
    nombre_video = re.split('[/.]', archivo)[-2]
    print(f'buscando comerciales en {nombre_video}')

    # leer cercanos del video.
    lista_cercanos = leer_cercanos(archivo)

    # leer comerciales para encontrar su frame final.
    numero_frames = contar_frames_comerciales()

    # lista de candidatos para buscar comerciales
    candidatos = []

    # abrir log
    log = open('respuesta.txt', 'a')
    encontrados = 0

    for cercanos in lista_cercanos:

        # se tiene una lista de comerciales para eliminar (especificos) y comerciales completados para eliminar todos
        # los que coincidan en el nombre (general)
        eliminados = []
        completados = []

        # recorrer candidatos
        for cand in candidatos:

            # detectar final del comercial.
            if cand.indice == numero_frames[cand.nombre] - 1:

                # registrar comercial.
                duracion = cercanos.tiempo - cand.tiempo_inicio
                log.write(f'{nombre_video}\t{"%.1f" % cand.tiempo_inicio}\t{"%.1f" % duracion}\t{cand.nombre}\n')
                print(f'{nombre_video}\t{"%.1f" % cand.tiempo_inicio}\t{"%.1f" % duracion}\t{cand.nombre}')
                encontrados += 1

                # eliminar de la lista (después del for).
                completados.append(cand.nombre)

            # buscar secuencia de comercial.
            else:
                cand.indice += 1

                # buscar siguiente frame y contar errores.
                if not buscar_indice(cand.nombre, cand.indice, cercanos.frames):
                    cand.errores += 1

                # determinar error de detección y eliminar de la lista (después del loop).
                if cand.errores >= max_porc_error * numero_frames[cand.nombre]:
                    eliminados.append(cand)

        # eliminar comerciales
        for eliminado in eliminados:
            candidatos.remove(eliminado)
        eliminados = []
        for completado in completados:
            for cand in candidatos:
                if cand.nombre == completado:
                    eliminados.append(cand)
        for eliminado in eliminados:
            candidatos.remove(eliminado)

        # buscar candidatos.
        indice, nombre = buscar_inicio(cercanos.frames, maximo_inicial=1)
        if indice != -1:
            candidatos.append(Candidato(nombre, indice, cercanos.tiempo))

    # cerrar log
    log.close()
    print(f'se encontraron {encontrados} comerciales')

    return


def main(archivo: str, max_porc_error: float = 0.2):
    buscar_comerciales(f'television_cercanos/{archivo}.txt', max_porc_error)
    return


if __name__ == '__main__':
    video = ''

    if len(sys.argv) == 1:
        video = 'mega-2014_04_11'
    elif len(sys.argv) == 2:
        video = sys.argv[1]
    else:
        print(f'Uso: {sys.argv[0]} nombre_video (sin extensión)\n por ejemplo: {sys.argv[0]} mega-2014_04_10')
        exit(1)

    # máximo porcentaje de errores permitidos
    max_porc_errores = 0.5

    main(video, max_porc_errores)
