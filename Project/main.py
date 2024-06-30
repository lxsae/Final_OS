import docker
import time
import io

client = docker.from_env()  # Crear cliente Docker

class Task:
    def __init__(self, command, start_time, estimated_time):
        self.command = command
        self.start_time = start_time
        self.estimated_time = estimated_time
        self.container = None

def create_container_image(command):
    dockerfile_content = f"FROM alpine\nCMD {command}"
    image, _ = client.images.build(rm=True, tag="temp_image", fileobj=io.BytesIO(dockerfile_content.encode('utf-8')))
    return image

def run_task(task):
    if task.container is None:
        container = client.containers.run("alpine", f'sh -c "{task.command}"', detach=True)
        task.container = container
    else:
        task.container.start()

    time.sleep(task.estimated_time)
    task.container.stop()

def stop_all_containers():
    for container in client.containers.list():
        container.stop()

def fcfs_scheduler(tasks):
    return sorted(tasks, key=lambda task: task.start_time)

def round_robin_scheduler(tasks, quantum):
    return sorted(tasks, key=lambda task: task.start_time)

def spn_scheduler(tasks):
    return sorted(tasks, key=lambda task: task.start_time)

def srt_scheduler(tasks):
    return sorted(tasks, key=lambda task: task.start_time)

def hrrn_scheduler(tasks):
    return sorted(tasks, key=lambda task: task.start_time)

executions = []

def register_execution(tasks, scheduler_name, times):
    execution = {
        'tasks': tasks,
        'scheduler': scheduler_name,
        'times': times
    }
    executions.append(execution)

def run_scheduler(scheduler, tasks, scheduler_name, **kwargs):
    times = {
        'Turnaround times': [],
        'Response times': [],
        'Turnaround time promedio': 0,
        'Response time promedio': 0
    }

    sorted_tasks = scheduler(tasks, **kwargs)

    for task in sorted_tasks:
        run_task(task)
        turnaround_time = task.start_time + task.estimated_time
        response_time = task.start_time
        times['Turnaround times'].append(turnaround_time)
        times['Response times'].append(response_time)

    times['Turnaround time promedio'] = sum(times['Turnaround times']) / len(times['Turnaround times'])
    times['Response time promedio'] = sum(times['Response times']) / len(times['Response times'])

    return times

container_images = {}

def get_or_create_container_image(command):
    if command in container_images:
        return container_images[command]
    else:
        image = create_container_image(command)
        container_images[command] = image
        return image

def main():
    tasks = []

    print("Ingrese los comandos a ejecutar (escriba 'fin' para terminar):")
    while True:
        command = input("Comando: ")
        if command.lower() == "fin":
            break
        start_time = int(input("Tiempo de inicio (en segundos): "))
        estimated_time = int(input("Tiempo estimado (en segundos): "))
        task = Task(command, start_time, estimated_time)
        tasks.append(task)

    fcfs_times = run_scheduler(fcfs_scheduler, tasks, "First Come First Served")
    register_execution(tasks, "First Come First Served", fcfs_times)

    rr_times = run_scheduler(round_robin_scheduler, tasks, "Round Robin", quantum=2)
    register_execution(tasks, "Round Robin", rr_times)

    spn_times = run_scheduler(spn_scheduler, tasks, "Shortest Process Next")
    register_execution(tasks, "Shortest Process Next", spn_times)

    srt_times = run_scheduler(srt_scheduler, tasks, "Shortest Remaining Time")
    register_execution(tasks, "Shortest Remaining Time", srt_times)

    hrrn_times = run_scheduler(hrrn_scheduler, tasks, "HRRN")
    register_execution(tasks, "HRRN", hrrn_times)

    print("\nRegistro de ejecuciones:")
    for execution in executions:
        print(f"\nAlgoritmo: {execution['scheduler']}")
        print("Tareas:")
        for task in execution['tasks']:
            print(f"  - {task.command}, inicio: {task.start_time}s, estimado: {task.estimated_time}s")
        print("Tiempos:")
        for time_name, time_value in execution['times'].items():
            print(f"  - {time_name}: {time_value}")

    stop_all_containers()

if __name__ == "__main__":
    main()
 
 
 
 