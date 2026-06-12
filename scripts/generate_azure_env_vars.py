import sys
import os
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()
import json
import pyperclip






def update_entries(azure_envs, operation: str):
    strs = []
    enabled = []
    disabled = []
    for entry in azure_envs:
        entry_name = entry['name']
        if 'AzureWebJobs' != entry_name[:12] or entry_name == 'AzureWebJobsStorage':
            continue
        short_name = entry_name.split('.')[1]
        value = entry['value']
        status = get_status(value)
        func_len = 35 - len(short_name)
        if status == 'enabled':
            enabled.append(short_name)
        elif status == 'disabled':
            disabled.append(short_name)

        if operation == 'toggle':
            entry['value'] = 'true' if entry['value'] == 'false' else 'false' if entry['value'] == 'true' else entry['value']
        elif operation == 'disable':
            entry['value'] = 'true'
            if value != 'true':
                strs.append(f'{short_name}{' ' * func_len}enabled              disabled')
        elif operation == 'enable':
            entry['value'] = 'false'
            if value != 'false':
                strs.append(f'{short_name}{' ' * func_len}disabled             enabled')
    
    print('\nDisabled\n------------')
    for s in disabled:
        print(s)
    print('\nEnabled\n------------')
    for s in enabled:
        print(s)    
    print()
    print('Function                           Old Status           New Status')
    print('------------------------------------------------------------------')
    for s in strs:
        print(s)

    return azure_envs


def decide_function_status(azure_envs):
    changes = []
    for entry in azure_envs:
        entry_name = entry['name']
        if 'AzureWebJobs' != entry_name[:12] or entry_name == 'AzureWebJobsStorage':
            continue
        short_name = entry_name.split('.')[1]
        value = entry['value']
        status = get_status(value)
        print(f'\n{short_name}: {status}')
        
        new_status = input(f'Confirm status? (y/n): ').lower()
        if new_status[0] in['y', 'c']:
            print('status confirmed')
        elif new_status[0] in ['n', 'u']:
            old = entry['value']
            new = 'true' if old == 'false' else 'true'
            entry['value'] = new
            changes.append({
                'func': short_name,
                'old': get_status(old),
                'new': get_status(new)
            })
            print(f'{short_name} changed from {get_status(old)} to {get_status(new)}')
    print()
    for change in changes:
        func_len = 25 - len(change['func'])
        old_len  = 9 - len(change['old'])
        new_len  = 9 - len(change['new'])

        print(f'{change['func']}:{' ' * func_len}{change['old']}{' ' * old_len}-> {change['new']}{' ' * new_len}')
    return azure_envs










def get_status(disabled: str):
    if disabled == 'true':
        return 'disabled'
    elif disabled == 'false':
        return 'enabled'



def read_azure_env() -> list | None:
    it = 0
    while True and it < 5:
        try:
            azure_envs = json.loads(pyperclip.paste())
            return azure_envs
        except Exception:
            it +=1
            input('Could not parse clipboard. Copy the Azure Environment Variables JSON, then press Enter...')
    return None

def read_local_env() -> list:
    current_env = []
    with open('.env' , 'r') as f:
        current_env_file = f.read()
    if current_env_file:
        current_env_line = current_env_file.split('\n')

    for line in current_env_line:
        if len(line) > 0 and line[0] !='#':
            line_split = line.split('=')
            st =  line_split[1][0]
            end = line_split[1][-1]
            if line_split[1][0] == '"' and line_split[1][-1] == "'":
                test = f'{line_split[1][1:-1]}'
                line_split[1] = f'{line_split[1][1:-1]}'
                bp = 'here'
            elif line_split[1][0] == "'":
                line_split[1] = line_split[1].replace("'", '"') 
            entry = {
                'name': f'{line_split[0]}',
                'value': line_split[1],
                "slotSetting": False
            }
            current_env.append(entry)
    return current_env



def compare_azure_vs_local(azure_env_vars: list, local_env_vars: list):
    bp = 'here'
    azure_env_backup = azure_env_vars.copy()
    print(f'Current number of env variables in Azure input: {len(azure_env_vars)}')
    print(f'Current number of env variables in local .env file: {len(local_env_vars)}')
    new_entries = []
    value_conflicts = []
    for variable in local_env_vars:
        name_matches = [az for az in azure_env_vars if az['name'] == variable['name']]
        if name_matches == []:
            print(f'New variable! {variable['name']}:{variable['value']}')
            bp = 'here'
            new_entries.append(variable)
        else:
            if len(name_matches) > 1:
                print(f'Multiple matches!!! Double check this!')
                continue
            name_match = name_matches[0]
            if variable['value'] != name_match['value']:
                print(f'!!\nValue conflict in {variable['name']}!')
                print(f'\t.env:  {variable['value']}')
                print(f'\tazure: {name_match['value']}')
                print(f'Keeping value found in Azure ({name_match['value']})')
                value_conflicts.append({
                    'name': variable['name'],
                    '.env': variable['value'],
                    'azure': name_match['value']
                })
                bp = 'here'
            bp = 'here'
    return new_entries, value_conflicts


def read_function_app():
    dir_path = Path(__file__).parent.parent
    with open(str(dir_path / 'function_app.py'), 'r') as r:
        function_app = r.read()
    lines = function_app.split('\n')
    # for line in lines:
    #     bp = 'here'
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
    for line in lines if 'def' in line and '(timer: af.TimerRequest)' in line]
    bp = 'here'
    functions = [
        {
        "name": f"AzureWebJobs.{line}.Disabled",
        "value": "false",
        "slotSetting": False
        } 
    for line in lines]

    return functions, lines



def pick_new_entries(new_entries: list):
    filtered_new_entries = []
    print(f'---------------------')
    bp = 'here'
    for i, variable in enumerate(new_entries):
        if variable in filtered_new_entries:
            print(f'{variable['name']}:{variable['value']} already added!')
            continue
        if 'ACUMATICA_API' in new_entries:
            print(f'skipping ACUMATICA_API vars')
            continue
        entry_group = [v for v in new_entries if v['name'].split('_')[0] == variable['name'].split('_')[0]]
        bp = 'here'


        if '-local' in variable['value']:
            print(f'Skipping local acumatica api login: {variable['name']}:{variable['value']}')
            continue
        inp = input(f'''Add {variable['name']}:{variable['value']} to Azure Environment variables?
press 1 for yes, 2 for no, 3 to add all with same prefix: ''')[0]
        if inp == '0':
            filtered_new_entries.append(variable)
            print(f'{variable['name']}:{variable['value']} added!')
        elif inp == '3':
            filtered_new_entries.extend(entry_group)
            print(f'{variable['name']}:{variable['value']} added!')
    return filtered_new_entries



def driver():
    deployed_functions, function_names = read_function_app()
    azure_env_vars = read_azure_env()
    if not azure_env_vars:
        return
    local_env_vars = read_local_env()
    new_entries, value_conflicts = compare_azure_vs_local(azure_env_vars=azure_env_vars, local_env_vars=local_env_vars)
    new_entries = pick_new_entries(new_entries)
    bp = 'here'
    deployed_functions, function_names = read_function_app()
    bp = 'here'


driver()

#region done
while True:
    try:
        azure_envs = json.loads(pyperclip.paste())
        break
    except Exception:
        input('Could not parse clipboard. Copy the Azure Environment Variables JSON, then press Enter...')



current_env = []
with open('.env' , 'r') as f:
    current_env_file = f.read()


if current_env_file:
    current_env_line = current_env_file.split('\n')

for line in current_env_line:
    if len(line) > 0 and line[0] !='#':
        line_split = line.split('=')
        st =  line_split[1][0]
        end = line_split[1][-1]
        if line_split[1][0] == '"' and line_split[1][-1] == "'":
            test = f'{line_split[1][1:-1]}'
            line_split[1] = f'{line_split[1][1:-1]}'
            bp = 'here'
        elif line_split[1][0] == "'":
            line_split[1] = line_split[1].replace("'", '"') 
        entry = {
            'name': f'{line_split[0]}',
            'value': line_split[1],
            "slotSetting": False
        }
        current_env.append(entry)


bp = 'here'
azure_env_backup = azure_envs.copy()
print(f'Current number of env variables in Azure input: {len(azure_envs)}')
print(f'Current number of env variables in local .env file: {len(current_env)}')
new_entries = []
value_conflicts = []
for entry in current_env:
    name_matches = [az for az in azure_envs if az['name'] == entry['name']]
    if name_matches == []:
        print(f'New variable! {entry['name']}:{entry['value']}')
        bp = 'here'
        new_entries.append(entry)
    else:
        if len(name_matches) > 1:
            print(f'Multiple matches!!! Double check this!')
            continue
        name_match = name_matches[0]
        if entry['value'] != name_match['value']:
            print(f'!!\nValue conflict in {entry['name']}!')
            print(f'\t.env:  {entry['value']}')
            print(f'\tazure: {name_match['value']}')
            print(f'Keeping value found in Azure ({name_match['value']})')
            value_conflicts.append({
                'name': entry['name'],
                '.env': entry['value'],
                'azure': name_match['value']
            })
            bp = 'here'
        bp = 'here'
#endregion done

azure_envs.extend(new_entries)

function_option_selection = input('''
Would you like to disable/enable functions?
press 1 to disable all functions
press 2 to enable all functions
press 3 to toggle all functions
press 4 to iterate and decide for each
press any other key to do nothing: ''')[0]

option_map = {
    '1': 'disable',
    '2': 'enable',
    '3': 'toggle'
}

if function_option_selection in['1', '2', '3']:
    azure_envs = update_entries(azure_envs, option_map[function_option_selection])
elif function_option_selection == '4':
    azure_envs = decide_function_status(azure_envs)
else:
    bp = 'here'




new = []
for entry in azure_envs:
    match = next((be for be in azure_env_backup if entry == be), None)
    if not match:
        new.append(f'{entry['name']}: {entry['value']}')

pyperclip.copy(json.dumps(azure_envs, indent=2))
print(f'New env json ready for paste to azure! {len(azure_envs) - len(azure_env_backup)} variables added')
print(f'\n\nAdditions:\n----')
for new_item in new:
    print(new_item)
bp = 'here'
