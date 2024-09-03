from flask import Flask, render_template, redirect, url_for, request
import os
import subprocess
import threading
import queue
import shutil

app = Flask(__name__)

# Use a lock to ensure thread safety when accessing the running_scripts dictionary
lock = threading.Lock()
running_scripts = {}

@app.route('/')
def index():
    # Script directory
    script_dir = 'Scripts'
    script_folders = [f for f in os.listdir(script_dir) if os.path.isdir(os.path.join(script_dir, f))]

    return render_template('index.html', script_folders=script_folders, running_scripts=running_scripts)

@app.route('/create_script', methods=['GET'])
def create_script():
    script_name = request.args.get('name')
    if script_name:
        create_script_directory(script_name)
    return redirect(url_for('index'))

@app.route('/start_script', methods=['GET'])
def start_script():
    script_name = request.args.get('name')
    if script_name:
        if not check_script_running(script_name):
            start_script_thread(script_name)
    return redirect(url_for('index'))

@app.route('/stop_script', methods=['GET'])
def stop_script():
    script_name = request.args.get('name')
    if script_name:
        stop_script_thread(script_name)
    return redirect(url_for('index'))

def create_script_directory(script_name):
    script_directory = os.path.join('Scripts', script_name)
    os.makedirs(script_directory, exist_ok=True)

    venv_directory = os.path.join(script_directory, 'venv')
    subprocess.run(['python', '-m', 'venv', venv_directory], check=True)

    script_file = os.path.join(script_directory, script_name+'.py')
    with open(script_file, 'w') as f:
        f.write('')

    log_file = os.path.join(script_directory, 'log.txt')
    with open(log_file, 'w') as f:
        f.write('')

def check_script_running(script_name):
    with lock:
        return script_name in running_scripts

def start_script_thread(script_name):
    script_directory = os.path.join('Scripts', script_name)
    venv_directory = os.path.join(script_directory, 'venv')
    script_file = os.path.join(script_directory, script_name+'.py')
    log_file = os.path.join(script_directory, 'log.txt')

    def run_script():
        try:
            activate_cmd = os.path.join(venv_directory, 'Scripts', 'activate.bat') if os.name == 'nt' else os.path.join(venv_directory, 'bin', 'activate')
            command = f'. "{activate_cmd}" && python "{script_file}"'
            process = subprocess.Popen(command, shell=True, stdout=open(log_file, 'w'), stderr=subprocess.STDOUT)
            process.wait()
        except Exception as e:
            print(f"Error running script: {e}")
        finally:
            on_exit(script_name)

    thread = threading.Thread(target=run_script)
    thread.start()
    with lock:
        running_scripts[script_name] = thread

def on_exit(script_name):
    with lock:
        del running_scripts[script_name]

def stop_script_thread(script_name):
    with lock:
        if script_name in running_scripts:
            thread = running_scripts[script_name]
            thread.join()

if __name__ == '__main__':
    app.run(debug=True)