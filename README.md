# Data of Empires
## Proyecto de Análisis de datos

Data of Empires es una app que permite obtener y visualizar datos correspondientes a partidas del videojuego Age of Empires II Definitive Edition.
Para esto se sirve de los datos ofrecidos por https://aoe2.net/#api, con ellos así poder realizar el proceso de Extraer, Transformar y Cargar para finalmente poder realizar un análisis y visualziación de los datos. 

## Herramientas utilizadas
- Pandas
- Plotly
- Dash
- Librería requests
- PostgreSQL

## Funciones y estado
- Análisis del historial personal de partidas de un jugador **WIP**
    - Rendimiento a través del tiempo **WIP**
    - Rendimiento discriminado por mapas y civilizaciones **WIP**
- Estadísticas de civilizaciones y mapas **DONE**
    -  Rendimiento entre civilizaciones **DONE**
    -  Estadísticas de victorias y uso de civilizaciones **DONE**
    -  Mejor combinación de civilzaciones en juego por equipos **DONE**
    -  Porcentaje de selección de mapas **DONE**
- Estadísticas de jugadores
    - Distribución de elo **DONE**
    - Estadísticas por país **DONE**
- Presentación Web **WIP**
## Requerimientos
- 

## Guía de instalación

Clonar el repositorio (o bien, descargarlo desde https://github.com/hectornauta/dataofempires y descomprimirlo)
> git clone https://github.com/hectornauta/dataofempires

En el directorio/carpeta donde se ha coonado/descargado el proyecto, abrir una terminal de comandos
> Mantener presionada la tecla SHIFT
> Clic derecho en un espacio vacío
> Hacer clic en "Abrir ventana de línea de comandos/PowerShell"

Crear un entorno virtual utilizando el comando
> python -m venv env

Activar el entorno virtual con el comando
> .\env\Scripts\activate

Instalar los siguientes paquetes ejecutando los siguientes comandos
> 

O bien, ejecutar el siguiente comando para hacer uso del archivo requeriments.txt
> pip install -r requirements.txt 

Crear un archivo llamado simplemente **.env** con las credenciales de PostgreSQL, con el siguiente formato
>DB_NAME=
>DB_USER=
>DB_PASSWORD=
>DB_HOST=127.0.0.1
