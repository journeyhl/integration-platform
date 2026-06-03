import sys
import os
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

dir_path = Path(__file__).parent.parent
with open(str(dir_path / 'function_app.py'), 'r') as r:
    function_app = r.read()

lines = function_app.split('\n')

lines = [line.strip().replace(
            '(timer: af.TimerRequest):', ''
        ).replace(
            'def ', ''
        ).replace(
            "schedule = '", ''
        ).replace(
            "',", ''
        ).replace(
            '",', ''
        )
for line in lines if 'schedule = ' in line or ('def' in line and '(timer: af.TimerRequest)' in line)]
bp = 'here'



schedule = {}

schedule_string = 'function_app_schedule = {'
for i, line in enumerate(lines):
    if '*' in line: continue
    schedule[line] = lines[i-1]
    schedule_string += f"\n\t'{line}': '{lines[i-1]}',"
schedule_string += '\n}'
import pyperclip
pyperclip.copy(schedule_string)
bp = 'here'