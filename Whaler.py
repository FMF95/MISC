import os
import msvcrt
import subprocess
import time
import winsound
from datetime import datetime
from tkinter import filedialog


#################################################
##                     INFO                    ##
#################################################


# Este codigo tiene como finalidad lanzar un bucle que recupere informacion de la Utilidad de Licencias de Altair para encontrar un pool con tokens disponibles con la finalidad de correr analisis.
# El bucle comprueba primero si el usuario ya tiene licencias cogidas.
# En caso de encontrar licencias suficientes para lanzar el solver, este se lanza.
# En caso de no encontrar licencias para lanzar el solver, pero si para abrir HM, se abre HM para coger esas licencias.
# Si se tiene HM abierto y se encuentran licencias suficientes contando con esas para lanzar el solver se da un aviso.

# A la hora de correr analisis se comprueba si los lanzadores ya se han corrido mirando las extensiones de los archivos de la carpeta.
# Si se encuentran archivos con las extensiones especificadas no se corre el analisis.
# En caso de no encontrar extensiones se corre el analis.


#################################################
##                    INPUTS                   ##
#################################################


# Usuario del servidor de licenecias
user = "frmi01@EXT0209"

# Tiempo de espera entre repeticiones
wait_time = 10

# Pintar mas detalles por consola
print_license_details = False
print_solver_details = True

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
needed_tokens = 27000
hm_tokens = 21000

#####################   #####################   #####################

# Path to tcl executable
tcl_exe = r"C:/Program Files/Altair/2022.3/common/tcl/tcl8.5.9/win64/bin/tclsh85t.exe"

# Path solvers tcl launcher
path_solvers_launcher = r"C:/Program Files/Altair/2022.3/hwdesktop/../common/acc/scripts/hwsolver.tcl"

# Opciones del Solver
solver_options = ["-len", "20000", "-optskip", "-checkel", "YES", "-nt", "4", "-v", "2022.3", "-dir", "-solver", "OS"] #"-screen",

# Tipo de resultados que buscar

results_type = ('.op2', '.h3d') # Sin el tipo .out o .stat si hay un error en el lanzador sigue intentando correr indefinidamente

# Abrir HM para asegurar licencias
open_hm = True

# Aviso si es posible correr el solver liberando licencias propias
alert = True


#################################################
##                     CODE                    ##
#################################################

# Se abre el explorador de archivos para seleccionar los archivos a calcular
files_path_tuple = filedialog.askopenfilenames(title="Select the file(s) to run",
                                        filetypes=( ("FEM Files (*.fem)", "*.fem"), ("Include Files (*.inc)", "*.inc"), ("All Files (*.*)", "*.*"),))

work_dir = os.path.dirname(files_path_tuple[0]) + '/'

files_name_list = []
for file_path in files_path_tuple:
    files_name_list.append(os.path.basename(file_path).split('.')[0])

def is_run(file_name: str)-> bool:
    for type in results_type:
        is_run = os.path.isfile(work_dir + file_name + type)
    return is_run

def run_solver():

    for file in files_name_list:

        count = files_name_list.index(file)

        if not is_run(file):

            file_to_run = work_dir + file + ".fem"

            solver_run_command = [tcl_exe, path_solvers_launcher, file_to_run] + solver_options

            now = datetime.now().strftime("%H:%M:%S")
            print(f"{now} - {file_to_run} is running...  ({count+1}/{len(files_name_list)})\n")

            solver_console = subprocess.run(solver_run_command, capture_output=True, text=True)

            # Verifica si el comando se ejecuto correctamente
            if print_solver_details:
                if solver_console.returncode >= 0:
                    # Imprime la salida estandar
                    print("Salida estandar:")
                    print(solver_console.stdout)
                    print("\n")
            else:
                    # Imprime el error estandar
                    print("Error estandar:")
                    print(solver_console.stderr)
                    print("\n")

            capture = False
            break # Se rompe el bucle para volver a comprobar si hay licencia antes de lanzar el solver de nuevo
        else:
            capture = True
            pass   
    
        if count+1 == len(files_name_list):
            now = datetime.now().strftime("%H:%M:%S")
            print(f"{now} - All files are run. Formats {results_type} found.")    

    return capture

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
    #capture = True
    capture = False
else:
    capture = False

# Bucle de busqueda de tokens
while not capture:
    for license in license_list:
        parameters_1 = ["-licstat", "-id", f"{license}", "-feature", f"{feature_name}", "-totals"]
        command_1 = [dir_almutil + "\\" + almutil] + parameters_1
        result_1 = subprocess.run(command_1, capture_output=True, text=True) # Se ejecuta para recuperar las licencias usadas

        # Verifica si el comando se ejecuto correctamente
        if print_license_details:
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
        connected = isconnected()

        if (needed_tokens > available_tkns >= hm_tokens) and (not capture) and (not connected) and open_hm:
            print(f"{now} - (License ID: {license}) License for HM captured!")
            capture = True
            subprocess.Popen(hm_run_command, cwd=hm_run_dir) # Se ejecuta HM para coger 21000 tokens
            #break
        elif (available_tkns < needed_tokens) and (available_tkns + hm_tokens >= needed_tokens) and connected and alert:
            print(f"{now} - (License ID: {license}) It could be possible to run the solver.")
            winsound.Beep(2500, 100) # (Hz, ms)

        elif (available_tkns >= needed_tokens) and not capture:
            print(f"{now} - (License ID: {license}) License for OptiStruct captured!")
            capture =  run_solver()

    if not capture:
        time.sleep(wait_time)

now = datetime.now().strftime("%H:%M:%S")
print(f"{now} - End program.")
print("Press any key to close the window.") 
msvcrt.getch()