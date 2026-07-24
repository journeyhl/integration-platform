import json
from calendar import monthrange
from datetime import datetime
import polars as pl
import logging
class Transform:
    def __init__(self, pipeline):
        bp = 'here'
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.Transform')
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
            segments = schedule.split(' ')
            minute = segments[0]
            hour = segments[1]
            day = segments[2]
            month = segments[3]
            weekday = segments[4]

            minutes = self._get_minutes_(minstr=minute)
            hours = self._get_hours_(hrstr=hour)
            days = self._get_days_(day)
            weekdays = self._get_weekdays_(wkdaystr=weekday)
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
                for d in day_split:
                    if '/' in d:
                        more_days = self.__slash__(cstr=d, units=month_days)
                        days.extend(more_days)
                    elif '-' in d:
                        more_days = self.__dash__(d)
                        days.extend(more_days)
                    else:
                        days.append(int(d))
                days.sort()
                return days
            elif '/' in daystr:
                days = self.__slash__(cstr=daystr, units=month_days)
                return days
            elif '-' in daystr:
                days = self.__dash__(daystr)
                return days
            else:
                return [int(daystr)]
        except Exception as e:
            bp = 'here'
        return days


    def _get_hours_(self, hrstr: str):
        if hrstr == '*':
            hours = [h for h in range(24)]
            return hours
        elif ',' in hrstr:
            hours = []
            hr_split = hrstr.split(',')
            bp = 'here'
            for hr in hr_split:
                if '/' in hr:
                    more_hours = self.__slash__(cstr=hr, units=24)
                    hours.extend(more_hours)
                elif '-' in hrstr:
                    more_hours = self.__dash__(hrstr)
                    hours.extend(more_hours)
                else:
                    hours.append(int(hr))
            hours.sort()
            return hours
        elif '-' in hrstr:
            hours = self.__dash__(hrstr)
            return hours
        elif '/' in hrstr:
            hours = self.__slash__(cstr=hrstr, units=24)
            return hours
        else:
            return [int(hrstr)]


        
    def _get_minutes_(self, minstr: str):
        if minstr == '*':
            minutes = [m for m in range(60)]
            return minutes
        elif ',' in minstr:
            minutes = []
            min_split = minstr.split(',')
            bp = 'here'
            for min in min_split:
                if '/' in min:
                    more_minutes = self.__slash__(min, 60)
                    minutes.extend(more_minutes)
                elif '-' in min:
                    more_minutes = self.__dash__(min)
                    minutes.extend(more_minutes)
                else:
                    minutes.append(int(min))
            minutes.sort()
            return minutes
        elif '-' in minstr:
            minutes = self.__dash__(minstr)
            return minutes
        elif '/' in minstr:
            minutes= self.__slash__(minstr, 60)
            return minutes
        else:
            return [int(minstr)]


    def _get_weekdays_(self, wkdaystr):
        if wkdaystr == '*':
            wd = [m for m in range(7)]
            return wd
        elif ',' in wkdaystr:
            wkdays = []
            wd_split = wkdaystr.split(', ')
            for wd in wd_split:
                if '/' in wkdaystr:
                    self.logger.error(f"What in the world are you trying to schedule? returning all weekdays...")
                    return [m for m in range(6)]
                elif '-' in wd_split:
                    more_wd = self.__dash__(wd)
                    wkdays.extend(more_wd)
                else:
                    wkdays.append(int(wd))
            wkdays.sort()
            return wkdays
        elif '-' in wkdaystr:
            wkdays = self.__dash__(wkdaystr)
            return wkdays
        else:
            return [int(wkdaystr)]




    def __dash__(self, cstr: str):
        split = cstr.split('-')
        start = int( split[0]) if split[0] != '*' else 0
        end = int(split[1])
        window = [i for i in range(start, end)]
        return window


    def __slash__(self, cstr: str, units: int):
        step = int( cstr.split('/')[0]) if cstr.split('/')[0] != '*' else 0
        freq = int( cstr.split('/')[1])
        times = [i for i in range(step, units, freq)]
        bp = 'here'
        return times
