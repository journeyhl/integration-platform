import sys
import os
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

'''
This script generates
'''

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

with open(r'C:\Users\jordanj\Desktop\integration-dashboard\utilities\sidebar_left.py', 'r') as file_with_schedule:
    file_text = file_with_schedule.read()

file_lines = file_text.split('\n')
new_file = []


replace_start = file_lines.index('function_app_schedule = {')
replace_end = file_lines.index('def upcoming_runs_today(per_function_cap: int = 8):')

first_segment = file_lines[:replace_start]
second_segment = file_lines[replace_end:]
new_file = first_segment + schedule_string.split('\n') + ['', ''] + second_segment

with open(r'C:\Users\jordanj\Desktop\integration-dashboard\utilities\sidebar_left.py', 'w', newline='\n') as file_with_schedule:
    file_with_schedule.write('\n'.join(new_file))


bp = 'here'


