# Data of Empires
## Proyecto de Datos

Data of Empires es una app que permite obtener y visualizar datos correspondientes a partidas del videojuego Age of Empires II Definitive Edition.

Para esto se sirve de los datos ofrecidos por https://aoe2.net/#api. Con los datos se realiza el proceso de Extracción, Transformación y Carga para su análisis y visualización posterior.

## Herramientas utilizadas
- Biblotecas: Pandas, Plotly, requests
- Framework :Dash
- DB: PostgreSQL

## Funciones y estado
- Análisis del historial personal de partidas de un jugador **WIP**
    - Evolución de su elo a través del tiempo **WIP**
    - Rendimiento discriminado por mapas y civilizaciones **WIP**
- Estadísticas de civilizaciones y mapas **DONE**
    -  Efectividad entre civilizaciones en partidas individuales **DONE**
    -  Estadísticas de victorias y uso de civilizaciones **DONE**
    -  Mejor combinación de civilzaciones en juego por equipos **DONE**
    -  Porcentaje de selección de mapas **DONE**
- Estadísticas de globales
    - Distribución cantidad de jugadores por franjas de elo **DONE**
    - Estadísticas de elo por país **DONE**
- Presentación Web **WIP**
## Requerimientos
- Se incluye un archivo requirements.txt

## Guía de instalación

Clonar el repositorio (o bien, descargarlo desde https://github.com/hectornauta/dataofempires y descomprimirlo)
> git clone https://github.com/hectornauta/dataofempires

En el directorio/carpeta donde se ha clonado/descargado el proyecto, abrir una terminal de comandos
> Mantener presionada la tecla SHIFT

> Clic derecho en un espacio vacío

> Hacer clic en "Abrir ventana de línea de comandos/PowerShell"

Crear un entorno virtual utilizando el comando
> python -m venv env

Activar el entorno virtual con el comando
> .\env\Scripts\activate

Instalar las dependencias, ejecutando el siguiente comando para hacer uso del archivo requirements.txt
> pip install -r requirements.txt 

Crear un archivo llamado simplemente **.env** con las credenciales de PostgreSQL, con el siguiente formato:

>DB_NAME =

>DB_USER =

>DB_PASSWORD =

>DB_HOST =

>DB_PORT =
