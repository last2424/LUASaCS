import luasacs, office, time, uvicorn
from multiprocessing import Process

threads = []

def start_auth_system():
    uvicorn.run(luasacs.app, host='127.0.0.1', port=5001) 

def start_methodical_office():
    uvicorn.run(office.app, host='127.0.0.1', port=8000) 

def start_cli_system():
    comm = input("Ожидание команды: ")
    if comm == "exit":
        for thread in threads:
            thread.terminate()
        return
    start_cli_system()


if __name__ == "__main__":
    auth_system = Process(target=start_auth_system)
    methodical_office = Process(target=start_methodical_office)
    threads.append(auth_system)
    threads.append(methodical_office)
    auth_system.start()
    methodical_office.start()
    time.sleep(5)
    start_cli_system()