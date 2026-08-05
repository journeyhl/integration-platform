
import sys
import os
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

dir_path = Path(__file__).parent.parent
with open(str(dir_path / 'function_app.py'), 'r') as r:
    function_app = r.read()


file_lines = function_app.split('\n')
functions = []
pipes = []
for line in file_lines:
    if 'def ' in line and 'timer: af.TimerRequest' in line:
        functions.append(line.replace('def ', '').replace('(timer: af.TimerRequest):', '').strip())
    if '_re_init()' in line or '.run()' in line:
        pipes.append(line.strip())

print(f'{len(functions)} functions and {len(pipes)} pipelines')
bp = 'here'