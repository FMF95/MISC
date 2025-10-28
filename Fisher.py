import os
import msvcrt
import subprocess
import time
from datetime import datetime


#################################################
##                     INFO                    ##
#################################################


# Este codigo tiene como finalidad lanzar un bucle que recupere informacion de la Utilidad de Licencias de Altair para encontrar un pool con tokens disponibles.
# El bucle comprueba primero si el usuario ya tiene licencias cogidas, y en ese caso termina.
# En caso de no tener licencias cogidas, el bucle se ejecuta infinitamente realizando la busqueda hasta que encuentre la cantidad de tokens especificada.
# Cuando se encuentran los tokens requeridos se ejecuta una ventana HyperMesh de 21000 tokens para reservar ese numero de licencias.


#################################################
##                    INPUTS                   ##
#################################################


# Usuario del servidor de licenecias
user = "frmi01@EXT0209"

# Tiempo de espera entre repeticiones
wait_time = 10

# Pintar mas detalles por consola
print_details = False

# Lista de IDs de pools de licencias
license_list = [107975, 92291]

# Nombre del feature para buscar
feature_name = "GlobalZoneEU"

# Ruta del directorio donde se encuentrea la Utilidad de Licencias de Altair
dir_almutil = r"C:\Altair\security\bin\win64"

# Ejecutable de la Utilidad de Licencias de Altair
almutil = f"almutil.exe"

# Obtenido desde propiedades del icono de HM 2021. Para ejecutar HyperMesh
hm_run_command = [r'C:\Program Files\Altair\2021.2\hwdesktop\hw\bin\win64\hw.exe', '/clientconfig', 'hwfepre.dat'] 
hm_run_dir = os.path.expandvars(r'%USERPROFILE%\Documents')

# Cantidad de licencias buscadas
needed_tokens = 21000


#################################################
##                     CODE                    ##
#################################################


# Comprobacion de si se esta ya conectado a algun pool
def isconnected():
    connected = 0
    for license in license_list:
        parameters_2 = ["-licstat", "-id", f"{license}", "-feature", f"{feature_name}","-network"]
        command_2 = [dir_almutil + "\\" + almutil] + parameters_2
        result_2 = subprocess.run(command_2, capture_output=True, text=True) # Se ejecuta para obtener un string en el que buscar el usuario
        connected += result_2.stdout.find(user)

        if connected > 0:
            now = datetime.now().strftime("%H:%M:%S")
            print(f"{now} - (License ID: {license}) Already connected.")
            connected = True
            return connected
        else:
            connected = False

    return connected

connected = isconnected()
if connected:
    capture = True
else:
    capture = False

# Bucle de busqueda de tokens
while not capture:
    for license in license_list:
        parameters_1 = ["-licstat", "-id", f"{license}", "-feature", f"{feature_name}", "-totals"]
        command_1 = [dir_almutil + "\\" + almutil] + parameters_1
        result_1 = subprocess.run(command_1, capture_output=True, text=True) # Se ejecuta para recuperar las licencias usadas

        # Verifica si el comando se ejecuto correctamente
        if print_details:
            if result_1.returncode == 0:
                # Imprime la salida estandar
                print("Salida estandar:")
                print(result_1.stdout)
            else:
                # Imprime el error estandar
                print("Error estandar:")
                print(result_1.stderr)

        stdout_lines = result_1.stdout.splitlines()

        stdout_last_line = stdout_lines[-1].split()

        used_tkns = int(stdout_last_line[0])
        total_tkns = int(stdout_last_line[2])

        available_tkns = total_tkns - used_tkns

        now = datetime.now().strftime("%H:%M:%S")
        print(f"{now} - (License ID: {license}) Available license(s): {available_tkns}")

        if (available_tkns >= needed_tokens) and not capture:
            print(f"{now} - (License ID: {license}) License captured!")
            capture = True
            subprocess.Popen(hm_run_command, cwd=hm_run_dir) # Se ejecuta HM para coger 21000 tokens
            break

    if not capture:
        time.sleep(wait_time)

now = datetime.now().strftime("%H:%M:%S")
print(f"{now} - End program.")
print("Press any key to close the window.") 
msvcrt.getch()