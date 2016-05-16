import glob
import time


INTERVAL = 1

class CPU:

    def __init__(self):
        self.name = self.__name()
        self.temp_table = []
        self.temp_labels = self.__temp_labels()

        self.freq_table = []
        self.freq_labels = self.__freq_labels()

        self.usage_table = []
        self.usage_labels = self.__usage_labels()


    def get_name(self):
        return self.name


    def get_temperature(self):
        self.__temperature()
        return self.temp_table

    def get_temp_labels(self):
        return self.temp_labels


    def get_frequency(self):
        self.__frequency()
        return self.freq_table

    def get_freq_labels(self):
        return self.freq_labels


    def get_usage(self):
        self.__usage()
        return self.usage_table

    def get_usage_labels(self):
        return self.usage_labels


    def __name(self):
        path = 'sysfs/cpu_name'
        with open(path, 'r') as f:
            name_str = f.readline()
        return name_str.split(':')[1].lstrip(' ').rstrip('\n')


    def __temp_labels(self):
        path = '/sys/class/hwmon/hwmon0/temp[0-9]_label'
        temp_labels = []
        for filename in sorted(glob.glob(path)):
            with open(filename, 'r') as f:
                temp_labels.append(f.readline().rstrip('\n'))
        return temp_labels

    def __temperature(self):
        path = '/sys/class/hwmon/hwmon0/temp[0-9]_input'
        temp_row = []
        for filename in sorted(glob.glob(path)):
            with open(filename, 'r') as f:
                temp_row.append(int(int(f.readline()) / 1000))
        
        if not self.temp_table:
            self.temp_table = [temp_row] * 3
        else:
            self.temp_table[0] = temp_row
            self.temp_table[1] = self.__min_row(temp_row, self.temp_table[1])
            self.temp_table[2] = self.__max_row(temp_row, self.temp_table[2])


    def __freq_row(self):
        path = '/sys/devices/system/cpu/cpu[0-9]/cpufreq/cpuinfo_cur_freq'
        freq_row = []
        for filename in sorted(glob.glob(path)):
            with open(filename, 'r') as f:
                freq_row.append(int(int(f.readline()) / 1000))
        return freq_row

    def __freq_labels(self):
        freq_row = self.__freq_row()
        self.freq_table = [freq_row] * 3
        return ['Core ' + str(i) for i in range(len(freq_row))]

    def __frequency(self):
        freq_row = self.__freq_row()
        self.freq_table[0] = freq_row
        self.freq_table[1] = self.__min_row(freq_row, self.freq_table[1])
        self.freq_table[2] = self.__max_row(freq_row, self.freq_table[2])


    def __usage_row(self):
        def get_times():
            path = '/proc/stat'
            times = []
            with open(path, 'r') as f:
                times = [s.replace('  ', ' ').split(' ')[1:] \
                    for s in f.readlines() if 'cpu' in s]
            return [(int(y) for y in x) for x in times]

        def delta_times():
            times_1 = get_times()
            time.sleep(INTERVAL / 2)
            times_2 = get_times()
            return [[(t2 - t1) for t1, t2 in zip(t1_row, t2_row)] for t1_row, t2_row in zip(times_1, times_2)]

        def get_load():
            dt = delta_times()
            idle_time = [float(x[3]) for x in dt]
            total_time = [sum(x) for x in dt]
            load = [int((1 - (x / y)) * 100) for x, y in zip(idle_time, total_time)]
            return load

        return get_load()

    def __usage_labels(self):
        usage_row = self.__usage_row()
        self.usage_table = [usage_row] * 3
        return ['UC'] + ['Core ' + str(x) for x in range(len(usage_row) - 1)]

    def __usage(self):
        usage_row = self.__usage_row()
        self.usage_table[0] = usage_row
        self.usage_table[1] = self.__min_row(usage_row, self.usage_table[1])
        self.usage_table[2] = self.__max_row(usage_row, self.usage_table[2])


    def __min_row(self, list_1, list_2):
        return [min(a, b) for a, b in zip(list_1, list_2)]

    def __max_row(self, list_1, list_2):
        return [max(a, b) for a, b in zip(list_1, list_2)]
