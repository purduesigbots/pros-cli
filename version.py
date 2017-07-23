import subprocess

try:
    v = subprocess.check_output(['git', 'describe', '--dirty'], stderr=subprocess.DEVNULL).decode().strip().replace('-','b', 1).replace('-','.')
except subprocess.CalledProcessError as e:
    v = open('version').read().strip()

print(v)
