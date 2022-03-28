# Data of Empires
## Proyecto de Análisis de datos

Data of Empires es una app que permite obtener y visualizar datos correspondientes a partidas del videojuego Age of Empires II Definitive Edition,

## Funciones

- Análisis del historial personal de partidas de un jugador
    - Rendimiento a través del tiempo
    - Rendimiento discriminado por mapas y civilizaciones
- Estadísticas de civilizaciones y mapas
    -  Porcentaje de victorias entre civilizaciones
    -  Porcentaje de victorias y de uso de civilizaciones
    -  Mejor combinación de civilzaciones en juego por equipos
    -  Porcentaje de selección de mapas
- Estadísticas de jugadores
    - Distribución de elo
    - Estadísticas por país
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
