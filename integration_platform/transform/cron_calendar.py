import json
from calendar import monthrange
from datetime import datetime
import polars as pl

class Transform:
    def __init__(self, pipeline):
            bp = 'here'
            self.pipeline = pipeline
            pass

    def lander(self, data_extract):            
        cron_schedule = self._parse_file_(data_extract)
        execution_schedule = self.generate_schedule(cron_schedule=cron_schedule)
        return execution_schedule




    def _parse_file_(self, data_extract):
        lines = data_extract.split('\n')
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
        sch_str = ''
        for i, line in enumerate(lines):
            if '*' in line: continue
            schedule[line] = lines[i-1]
            jline = f'"{line}":"{lines[i-1]}",'
            sch_str += jline


        jstring = '{'  + sch_str[:-1] + '}'
        ip_cron = json.loads(jstring)
        return ip_cron



    def generate_schedule(self, cron_schedule):
        
        
            

        bp = 'here'
        self.now = datetime.now()
        self.year_now = self.now.year
        self.month_now = self.now.month
        executions = []
        for function, schedule in cron_schedule.items():
            if function == 'five9_call_segments':
                bp = 'here'
            segments = schedule.split(' ')
            minute = segments[0]
            hour = segments[1]
            day = segments[2]
            month = segments[3]
            weekday = segments[4]

            minutes = self._get_minutes_(minstr=minute)
            hours = self._get_hours_(hrstr=hour)
            days = self._get_days_(day)
            bp = 'here'
            for day in days:
                for hr in hours:
                    for min in minutes:
                        ex = {
                            'AzureFunction': function,
                            'ExecutionTime': datetime(year=self.year_now, month=self.month_now, day=day, hour=hr, minute=min)
                        }
                        executions.append(ex)

        df_executions = pl.DataFrame(executions, infer_schema_length=None)
        return df_executions




    def _get_days_(self, daystr):
        month_days = monthrange(self.year_now, self.month_now)[1] + 1
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
                        days.append(int(d))
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


    def _get_hours_(self, hrstr: str):
        if hrstr == '*':
            month_days = monthrange(self.year_now, self.month_now)[1]
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


        
    def _get_minutes_(self, minstr: str):
        if minstr == '*':
            month_days = monthrange(self.year_now, self.month_now)[1]
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
            minutes = [i for i in range(step, 60, freq)]
            return minutes
        else:
            return [int(minstr)]
        return minutes
