## Detección de Comerciales

Esta tarea es para el ramo CC5213 - Recuperación de información multimedia y consiste en detectar la ocurrencia de comerciales en grabaciones de televisión comparando frames.


### Preparación:

Para montar el proyecto se debe hacer lo siguiente:

- `pip install requirements`
- Descargar comerciales y poner en la carpeta `comerciales/` (al mismo nivel que el resto de los archivos).
- Descargar grabaciones de televisión y poner en la carpeta `television/` (al mismo nivel que el resto de los archivos).


### Ejecución:

Para ejecutar el proyecto basta con ejecutar `python Tarea1.py {nombre_video}`. El nombre del video debe ser igual al nombre del video en la carpeta `television/` que se desea analizar, sin extensión. e.g. `python Tarea1.py mega-2014_04_10`.

Los comerciales detectados quedan registrados en el archivo respuesta.txt

Opcionalmente, se puede ejecutar cada paso por separado usando:
- `python Extraccion.py {nombre_video}` extrae las características de los comerciales y el video.
- `python Distancia.py {nombre_video}` calcula los frames más cercanos a cada frame del video.
- `python Busqueda.py {nombre_video}` busca la ocurrencia de comerciales.

No se puede ejecutar un paso sin haber ejecutado el anterior previamente.


### Configuración:

Para configurar algunos parámetros de cada fase se puede editar el archivo de cada parte (`Extraccion.py`, `Distancia.py`, `Busqueda.py`). Al final de cada archivo se encuentran los parámetros importantes que se pueden editar fácilmente antes de llamar a la función `main()`.
