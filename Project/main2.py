import time
import subprocess
import hashlib
import pickle
import threading

class Command:
    def __init__(self, command, start_time, estimated_time):
        self.command = command
        self.start_time = start_time
        self.estimated_time = estimated_time
        self.turnaround_time = 0
        self.response_time = 0
        self.execution_start_time = 0
        self.remaining_time = estimated_time

def create_docker_image(command):
    hash_object = hashlib.sha1(command.encode())
    image_name = f"command_image_{hash_object.hexdigest()}"
    try:
        output = subprocess.check_output(["docker", "images", "-q", image_name])
        if not output.strip():
            raise subprocess.CalledProcessError(1, "Image not found")
    except subprocess.CalledProcessError:
        dockerfile = f"FROM alpine:latest\nCMD {command}"
        with open("Dockerfile", "w") as f:
            f.write(dockerfile)
        subprocess.run(["docker", "build", "-t", image_name, "."], check=True)
    return image_name
def execute_command(image_name):
    subprocess.run(["docker", "run", image_name])

def execute_command_partial(image_name, duration):
    # Ejecutar el comando en un hilo separado para poder interrumpirlo
    def run_container():
        subprocess.run(["docker", "run", image_name])
    
    thread = threading.Thread(target=run_container)
    thread.start()
    thread.join(duration)
    
    if thread.is_alive():
        # Esto mata el contenedor después del tiempo especificado
        subprocess.run(["docker", "stop", image_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        thread.join()

def fcfs_scheduler(commands):
    start_time = time.time()
    for command in commands:
        wait_time = command.start_time - (time.time() - start_time)
        time.sleep(max(0, wait_time))
        command.execution_start_time = time.time()
        image_name = create_docker_image(command.command)
        execute_command(image_name)
        end_time = time.time()
        command.turnaround_time = end_time - start_time
        command.response_time = command.execution_start_time - start_time

def round_robin_scheduler(commands, quantum=2):
    queue = commands[:]
    start_times = {cmd: time.time() + cmd.start_time for cmd in commands}
    while queue:
        command = queue.pop(0)
        wait_time = max(0, start_times[command] - time.time())
        time.sleep(wait_time)
        command.execution_start_time = time.time()
        image_name = create_docker_image(command.command)
        
        # Ejecutar el comando solo por el tiempo del quantum o el tiempo restante, lo que sea menor
        execute_command_partial(image_name, min(quantum, command.remaining_time))
        end_time = time.time()
        
        elapsed_time = end_time - command.execution_start_time
        command.remaining_time -= elapsed_time
        
        command.turnaround_time = end_time - start_times[command]
        command.response_time = command.execution_start_time - start_times[command]
        
        if command.remaining_time > 0:
            queue.append(command)

def spn_scheduler(commands):
    commands.sort(key=lambda cmd: cmd.estimated_time)
    fcfs_scheduler(commands)

def srt_scheduler(commands):
    start_time = time.time()
    while commands:
        commands.sort(key=lambda cmd: cmd.estimated_time - (time.time() - start_time))
        command = commands.pop(0)
        wait_time = command.start_time - (time.time() - start_time)
        time.sleep(max(0, wait_time))
        command.execution_start_time = time.time()
        image_name = create_docker_image(command.command)
        execute_command(image_name)
        end_time = time.time()
        command.turnaround_time = end_time - start_time
        command.response_time = command.execution_start_time - start_time

def hrrn_scheduler(commands):
    start_time = time.time()
    while commands:
        for command in commands:
            wait_time = time.time() - start_time - command.start_time
            response_ratio = (wait_time + command.estimated_time) / command.estimated_time
            command.response_ratio = response_ratio
        commands.sort(key=lambda cmd: cmd.response_ratio, reverse=True)
        command = commands.pop(0)
        wait_time = command.start_time - (time.time() - start_time)
        time.sleep(max(0, wait_time))
        command.execution_start_time = time.time()
        image_name = create_docker_image(command.command)
        execute_command(image_name)
        end_time = time.time()
        command.turnaround_time = end_time - start_time
        command.response_time = command.execution_start_time - start_time

class ExecutionHistory:
    def __init__(self):
        self.history = []

    def add_execution(self, commands, algorithm):
        self.history.append({
            "commands": [cmd.command for cmd in commands],
            "algorithm": algorithm,
            "turnaround_times": [cmd.turnaround_time for cmd in commands],
            "response_times": [cmd.response_time for cmd in commands]
        })

    def save_history(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self.history, f)

    def load_history(self, filename):
        with open(filename, 'rb') as f:
            self.history = pickle.load(f)

    def print_history(self):
        history_s = ''
        for history in self.history:
            history_s += f'Commands: {history["commands"]}\nAlgorithm: {history["algorithm"]}\nTurnaround Times: {history["turnaround_times"]}\nResponse Times: {history["response_times"]}\n\n'
        return history_s

def get_user_input():
    commands = []
    while True:
        command = input("Ingrese el comando (o 'fin' para terminar): ")
        if command.lower() == 'fin':
            break
        start_time = int(input("Ingrese el tiempo de inicio (en segundos): "))
        estimated_time = int(input("Ingrese el tiempo estimado de ejecución (en segundos): "))
        commands.append(Command(command, start_time, estimated_time))
    return commands

def select_scheduler():
    print("Seleccione el algoritmo de planificación:")
    print("1. First Come First Served (FCFS)")
    print("2. Round Robin (RR)")
    print("3. Shortest Process Next (SPN)")
    print("4. Shortest Remaining Time (SRT)")
    print("5. Highest Response Ratio Next (HRRN)")
    choice = int(input("Ingrese el número correspondiente al algoritmo: "))
    if choice == 1:
        return 'fcfs'
    elif choice == 2:
        return 'rr'
    elif choice == 3:
        return 'spn'
    elif choice == 4:
        return 'srt'
    elif choice == 5:
        return 'hrrn'
    else:
        print("Selección inválida. Usando FCFS por defecto.")
        return 'fcfs'

def main():
    commands = get_user_input()
    scheduler = select_scheduler()
    
    if scheduler == 'fcfs':
        fcfs_scheduler(commands)
    elif scheduler == 'rr':
        quantum = int(input("Ingrese el quantum para Round Robin (en segundos): "))
        round_robin_scheduler(commands, quantum)
    elif scheduler == 'spn':
        spn_scheduler(commands)
    elif scheduler == 'srt':
        srt_scheduler(commands)
    elif scheduler == 'hrrn':
        hrrn_scheduler(commands)

    history = ExecutionHistory()
    history.add_execution(commands, scheduler.upper())
    history.save_history("execution_history.pkl")

    # Mostrar el historial de ejecuciones
    history.load_history("execution_history.pkl")
    print(history.print_history())

if __name__ == "__main__":
    main()
