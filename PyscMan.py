from flask import Flask, render_template, redirect, url_for, request
import os
import subprocess


app = Flask(__name__)

running_scripts = {}

@app.route('/')
def index():
    # Script directory
    script_dir = 'Scripts'

    # get the list of folders in the script directory
    script_folders = [f for f in os.listdir(script_dir) if os.path.isdir(os.path.join(script_dir, f))]

    return render_template('index.html', script_folders=script_folders)

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
            start_script_process(script_name)
    return redirect(url_for('index'))

@app.route('/stop_script', methods=['GET'])
def stop_script():
    script_name = request.args.get('name')
    if script_name:
        stop_script_process(script_name)
    return redirect(url_for('index'))


def create_script_directory(script_name):
    # Create a new directory for the script
    script_directory = os.path.join('Scripts', script_name)
    os.makedirs(script_directory, exist_ok=True)

    # Create venv directory
    venv_directory = os.path.join(script_directory, 'venv')
    os.system(f'python -m venv {venv_directory}')

    # Create an empty .py file for the script
    script_file = os.path.join(script_directory, script_name+'.py')
    with open(script_file, 'w') as f:
        f.write('')

    # Create a new file for the script log
    log_file = os.path.join(script_directory, 'log.txt')
    with open(log_file, 'w') as f:
        f.write('')
def check_script_running(script_name):
    return script_name in running_scripts
def start_script_process(script_name):
    # Script directory
    script_directory = os.path.join('Scripts', script_name)

    # Venv directory
    venv_directory = os.path.join(script_directory, 'venv')

    # Script file
    script_file = os.path.join(script_directory, script_name+'.py')

    # Log file
    log_file = os.path.join(script_directory, 'log.txt')

    # Construct the command to activate the virtual environment and start the script
    if os.name == 'nt':  # For Windows
        activate_cmd = os.path.join(venv_directory, 'Scripts', 'activate.bat')
        command = f'call "{activate_cmd}" && python "{script_file}"'
    else:  # For Unix-like systems
        activate_cmd = os.path.join(venv_directory, 'bin', 'activate')
        command = f'source "{activate_cmd}" && python "{script_file}"'

    # Start the script within the activated virtual environment
    process = subprocess.Popen(command, shell=True, stdout=open(log_file, 'w'), stderr=subprocess.STDOUT)

    # Store the process in the running_scripts dictionary
    running_scripts[script_name] = process

    # Wait for the subprocess to finish and call the callback function (if provided)
    exit_status = process.wait()
    if exit_status == 0:
        print(f'Script {script_name} finished successfully')
    else:
        print(f'Script {script_name} failed with exit status {exit_status}')
def stop_script_process(script_name):
    if script_name in running_scripts:
        process = running_scripts[script_name]
        process.terminate()
        del running_scripts[script_name]


if __name__ == '__main__':
    app.run(debug=True)