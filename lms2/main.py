import platform
import subprocess
from os import chdir, getcwd
from os.path import join as path_join, isdir, isfile

STATIC_PROJECT_PATH = ['home', 'govindgrover', 'lms2']
ROOT_DIR = path_join('/', *STATIC_PROJECT_PATH)


chdir(ROOT_DIR)
print(f"\nChanged to root directory: {getcwd()}\n")
# directory changed

if not isdir(path_join(ROOT_DIR, '.lms2-env')):
	print("\nSetting up virtual environment...\n")
	subprocess.run(['python', '-m', 'venv', '.lms2-env'])
# venv created

if platform.system() == "Windows":
	subprocess.call('cls')  		# Windows
	python_in_envir = path_join('.lms2-env', 'Scripts', 'python')
	pip_in_envir = path_join('.lms2-env', 'Scripts', 'pip')
else:
	subprocess.call('clear')		# Linux
	python_in_envir = path_join('.lms2-env', 'bin', 'python')
	pip_in_envir = path_join('.lms2-env', 'bin', 'pip')
# determined the pip path


if isfile(path_join(ROOT_DIR, 'requirements.txt')):
	print("Installing dependencies...")
	subprocess.run([pip_in_envir, 'install', '-r', 'requirements.txt'])
# Dependencies installed, if requirements.txt exists


if platform.system() == "Windows":
	subprocess.call('cls')			# Windows
	python_in_envir = path_join('.lms2-env', 'Scripts', 'python')
else:
	subprocess.call('clear')		# Linux
	python_in_envir = path_join('.lms2-env', 'bin', 'python')
# python path determined


api_application = path_join(ROOT_DIR, 'lms2-api', 'app.py')         	# API App
frontend_application = path_join(ROOT_DIR, 'lms2-frontend', 'app.py')	# Frontend App


# Start both applications
process1 = subprocess.Popen([python_in_envir, api_application])
process2 = subprocess.Popen([python_in_envir, frontend_application])


# Printing info
print("API & Frontend servers have been started...")
print("Kindly visit http://localhost:8000 for Project LMS -- V2\n\n")

# Wait for the processes to complete (indefinitely)
process1.wait()
process2.wait()
