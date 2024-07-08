# Proyecto Final Sistemas Operativos

    Planificador para la gestión de contenedores

El aplicativo desarrollado para el proyecto final consiste en un programa que ejecuta comandos de bash, como por ejemplo “ls -l”.Para cada ejecución se utilizará la herramienta Docker, lo que significa que cada comando proporcionado por el usuario se ejecuta dentro de su propio contenedor. Los contenedores utilizan una imagen de Alpine, que es una versión minimalista de Linux, lo que asegura un entorno ligero y eficiente.

El aplicativo recibe una lista de comandos y los ejecuta utilizando diferentes algoritmos de planificación de procesos. Los algoritmos implementados son los siguientes:

- First Come First Served (FCFS)
- Round Robin (con un quantum de 2 segundos)
- Shortest Process Next (SPN)
- Shortest Remaining Time (SRT)
- Highest Response Ratio Next (HRRN)

# Integrantes:

- Juan David Fonseca - 2323942
- Elkin Tovar - 1931440
- Ivan Noriega - 2126012
- Yenny Rivas - 2181527
