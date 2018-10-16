import sys
import time

from Extraccion import caracteristicas_videos, caracteristicas_video
from Distancia import leer_videos, frames_mas_cercanos_video
from Busqueda import buscar_comerciales


def main(nombre_video: str):
    t = time.time()

    # extraer caracteristicas
    salto_frames = 10
    tamano = (10, 10)
    caracteristicas_videos('comerciales', salto_frames=salto_frames, tamano=tamano)
    caracteristicas_video(f'television/{nombre_video}.mp4', 'television_car', salto_frames=salto_frames, tamano=tamano)

    # buscar frames cercanos
    comerciales = leer_videos('comerciales_car')
    frames_mas_cercanos_video(f'television_car/{nombre_video}.txt', comerciales, 'television_cercanos', k=5)

    # buscar comerciales
    buscar_comerciales(f'television_cercanos/{nombre_video}.txt')

    print(f'el proceso tomó {int(time.time() - t)} segundos')
    return


if __name__ == '__main__':
    video = ''

    if len(sys.argv) == 1:
        video = 'mega-2014_04_10'
    elif len(sys.argv) == 2:
        video = sys.argv[1]
    else:
        print(f'Uso: {sys.argv[0]} nombre_video (sin extensión)\n por ejemplo: {sys.argv[0]} mega-2014_04_10')
        exit(1)

    main(video)