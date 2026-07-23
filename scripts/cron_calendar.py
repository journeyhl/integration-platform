import sys
import os
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
from datetime import datetime
from calendar import monthrange
from integration_platform.connectors.sql import SQLConnector
import polars as pl
'''
This script generates
'''

dbc = SQLConnector(pipeline='cron-calendar', database_name='db_CentralStore')

def cron_to_db_central(ip_cron: dict):
    def get_minutes(minstr: str):
        if minstr == '*':
            month_days = monthrange(now.year, now.month)[1]
            minutes = [m for m in range(60)]
            return minutes
        if ',' in minstr:
            minutes = []
            min_split = minstr.split(',')
            bp = 'here'
            for min in min_split:
                if '/' in min:
                    step = int( min.split('/')[0])
                    freq = int( min.split('/')[1])
                    ex_per_hour = 60/freq
                    minutes = minutes + [i for i in range(step, 60, freq)]
                    bp = 'here'
                else:
                    minutes.append(int(min))
                minutes.sort()
            return minutes
        elif '/' in minstr:
            step = 0 if minstr[0] == '*' else int(minstr.split('/')[0])
            freq = int( minstr.split('/')[1])
            minutes = [i for i in range(0, 60, freq)]
            return minutes
        else:
            return [int(minstr)]
        return minutes

    
    def get_hours(hrstr: str):
        if hrstr == '*':
            month_days = monthrange(now.year, now.month)[1]
            hours = [h for h in range(24)]
            return hours
        if ',' in hrstr:
            hours = []
            hr_split = hrstr.split(',')
            bp = 'here'
            for hr in hr_split:
                if '/' in hr:
                    step = int( hr.split('/')[0])
                    freq = int( hr.split('/')[1])
                    ex_per_hour = 24/freq
                    hours = hours + [i for i in range(step, 24, freq)]
                    bp = 'here'
                else:
                    hours.append(int(hr))
                hours.sort()
            return hours
        elif '/' in hrstr:
            step = 0 if hrstr[0] == '*' else int(hrstr.split('/')[0])
            freq = int( hrstr.split('/')[1])
            hours = [i for i in range(0, 24, freq)]
            return hours
        elif '-' in hrstr:
            split = hrstr.split('-')
            start = int(split[0])
            end = int(split[1])
            hours = [h for h in range(start, end)]
            return hours
        else:
            return [int(hrstr)]
        
    def get_days(daystr: str):
        month_days = monthrange(now.year, now.month)[1] + 1
        if daystr == '*':
            days = [d for d in range(1, month_days)]
            return days
        try:
            if ',' in daystr:
                days = []
                day_split = daystr.split(',')
                bp = 'here'
                for d in day_split:
                    if '/' in d:
                        step = int( d.split('/')[0])
                        freq = int( d.split('/')[1])
                        days = days + [i for i in range(step, month_days, freq)]
                        bp = 'here'
                    else:
                        days.append(int(hr))
                    days.sort()
                return days
            elif '/' in daystr:
                step = 0 if daystr[0] == '*' else int(daystr.split('/')[0])
                freq = int( daystr.split('/')[1])
                days = [i for i in range(1, month_days, freq)]
                return days
            elif '-' in daystr:
                split = daystr.split('-')
                start = int(split[0])
                end = int(split[1])
                days = [d for d in range(start, end)]
                return days
            else:
                return [int(daystr)]
        except Exception as e:
            bp = 'here'
        return days

    bp = 'here'
    now = datetime.now()
    year_now = now.year
    month_now = now.month
    day_now = now.day
    executions = []
    for function, schedule in ip_cron.items():
        segments = schedule.split(' ')
        minute = segments[0]
        hour = segments[1]
        day = segments[2]
        month = segments[3]
        weekday = segments[4]

        minutes = get_minutes(minstr=minute)
        hours = get_hours(hrstr=hour)
        days = get_days(day)
        bp = 'here'
        for day in days:
            for hr in hours:
                for min in minutes:
                    ex = {
                        'AzureFunction': function,
                        'ExecutionTime': datetime(year=year_now, month=month_now, day=day, hour=hr, minute=min)
                    }
                    executions.append(ex)
                bp = 'here'
            bp = 'here'

    df_executions = pl.DataFrame(executions, infer_schema_length=None)
    dbc.raw_execute(f'delete from _util.Schedule')
    dbc.insert_df(df_data_loaded=df_executions, table_name='_util.Schedule')
    return executions
        
    bp = 'here'








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
sch_str = ''
formatter = '\n\t'
for i, line in enumerate(lines):
    if '*' in line: continue
    schedule[line] = lines[i-1]
    jline = f'"{line}":"{lines[i-1]}",'
    sch_str += f"{formatter}{jline}"

schedule_string += f'{sch_str}\n'
import pyperclip
pyperclip.copy(schedule_string)
bp = 'here'


jstring = '{'  + sch_str.replace(formatter, '')[:-1] + '}'
ip_cron = json.loads(jstring)

dbc_executions = cron_to_db_central(ip_cron)



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



    # def get_days(daystr: str):
    #     if daystr == '*':
    #         month_days = monthrange(now.year, now.month)[1]
    #         days = [d for d in range(month_days)]
    #         return days
    #     try:
    #         if ',' in daystr:
    #             days = []
    #             day_split = daystr.split(',')
    #             bp = 'here'
    #             for day in day_split:
    #                 if '/' in day_split:
    #                     bp = 'here'
    #         else:
    #             bp = 'here'
    #     except Exception as e:
    #         bp = 'here'
    #     return days