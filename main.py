import time
import glob
import subprocess
import os


INTERVAL = 0.5

cpu_freq_table = []
cpu_temp_table = []
cpu_usage_table = []
gpu_freq_row = []
hdd_temp_row = []
bat_voltage_row = []
bat_charge_row = []


def main():
    while 1:
        #os.system('clear')
        cpu_t = cpu_temperature()
        cpu_f = cpu_frequency()
        cpu_u = cpu_usage()
        hdd_t = hdd_temperature()
        gpu_f = gpu_frequency()
        bat_v = bat_voltage()
        bat_c = bat_charge()
        print('-' * 80)
        print(cpu_name_str)
        print(cpu_t)
        print(cpu_f)
        print(cpu_u + '\n')
        print('-' * 80)
        print(gpu_name_str)
        print(gpu_f + '\n')
        print('-' * 80)
        print(hdd_name_str)
        print(hdd_t + '\n')
        print('-' * 80)
        print(bat_v)
        print(bat_c)
        time.sleep(INTERVAL)


def min_row(list_1, list_2):
    return [min(a, b) for a, b in zip(list_1, list_2)]


def max_row(list_1, list_2):
    return [max(a, b) for a, b in zip(list_1, list_2)]



# ----------------------------------------   Indexes:   0 - Physical Id 0   --------------------------------
# ----------------------------------------              1 - Core 0          --------------------------------
# ----------------------------------------              2 - Core 1          --------------------------------

def cpu_name():
    cpu_name_str = subprocess.check_output('lscpu | grep \'Model name\'', shell = True).decode()
    return cpu_name_str.split(':')[1].lstrip(' ')


def cpu_temperature():
    path = '/sys/class/hwmon/hwmon0/temp[0-9]_'

    temp_row = []
    for filename in sorted(glob.glob(path + 'input')):
        with open(filename, 'r') as f:
            temp_row.append(int(int(f.readline()) / 1000))

    global cpu_temp_table
    if not cpu_temp_table:
        cpu_temp_table = [temp_row] * 3
    else:
        cpu_temp_table[0] = temp_row
        cpu_temp_table[1] = min_row(temp_row, cpu_temp_table[1])
        cpu_temp_table[2] = max_row(temp_row, cpu_temp_table[2])

    temp_label = []
    for filename in sorted(glob.glob(path + 'label')):
        with open(filename, 'r') as f:
            temp_label.append(f.readline().rstrip('\n'))

    s = 'CPU temperature [Cur    Min     Max]\n'
    for l, temp_str in zip(temp_label, zip(*cpu_temp_table)):
        s += str(l).ljust(16) + '   '.join(str(x) + ' °C' for x in temp_str)	+ '\n'
    return s


def cpu_frequency():
    path = '/sys/devices/system/cpu/cpu[0-9]/cpufreq/cpuinfo_cur_freq'

    freq_row = []
    for filename in sorted(glob.glob(path)):
        with open(filename, 'r') as f:
            freq_row.append(int(int(f.readline()) / 1000))

    global cpu_freq_table
    if not cpu_freq_table:
        cpu_freq_table = [freq_row] * 3
    else:
        cpu_freq_table[0] = freq_row
        cpu_freq_table[1] = min_row(freq_row, cpu_freq_table[1])
        cpu_freq_table[2] = max_row(freq_row, cpu_freq_table[2])

    s = 'CPU frequency [Cur       Min        Max]\n'
    for i, freq_str in enumerate(zip(*cpu_freq_table)):
        s += 'Core ' + str(i).ljust(9) + '   '.join(str(x) + ' MHz' for x in freq_str) + '\n'
    return s


def cpu_usage():
    def get_times():
        path = '/proc/stat'
        cpus_times = []
        with open(path, 'r') as f:
            cpus_times = [s.replace('  ', ' ').split(' ')[1:] \
                for s in f.readlines() if 'cpu' in s]
        return [(int(y) for y in x) for x in cpus_times]

    def delta_times():
        times_1 = get_times()
        time.sleep(INTERVAL)
        times_2 = get_times()
        return [[(t2 - t1) for t1, t2 in zip(t1_row, t2_row)] for t1_row, t2_row in zip(times_1, times_2)]

    def get_cpu_load():
        dt = delta_times()
        idle_time = [float(x[3]) for x in dt]
        total_time = [sum(x) for x in dt]
        load = [int((1 - (x / y)) * 100) for x, y in zip(idle_time, total_time)]
        return load

    cpu_usage_row = get_cpu_load()
    global cpu_usage_table
    if not cpu_usage_table:
        cpu_usage_table = [cpu_usage_row] * 3
    else:
        cpu_usage_table[0] = cpu_usage_row
        cpu_usage_table[1] = min_row(cpu_usage_row, cpu_usage_table[1])
        cpu_usage_table[2] = max_row(cpu_usage_row, cpu_usage_table[2])

    usage_label = ['UC'] + ['Core ' + str(x) for x in range(len(cpu_usage_row) - 1)]

    s = 'CPU usage [Cur   Min    Max]\n'
    for l, cpu_usage_str in zip(usage_label, zip(*cpu_usage_table)):
        s += str(l).ljust(10) + '   '.join((str(x) + ' %').ljust(4) for x in cpu_usage_str) + '\n'
    return s


def gpu_name():
    gpu_name_str = subprocess.check_output('lspci | grep \'VGA\'', shell = True).decode()
    return gpu_name_str.split('VGA')[1].split(':')[1].lstrip(' ')


def hdd_name():
    hdd_name_str = subprocess.check_output('hdparm -I /dev/sda | grep \'Model Number\'', shell=True).decode()
    return hdd_name_str.split(':')[1].lstrip(' ')


def gpu_frequency():   
    path = '/sys/class/drm/card0/gt_cur_freq_mhz'

    freq_cur = 0
    with open(path, 'r') as f:
        freq_cur = int(f.readline())

    global gpu_freq_row
    if not gpu_freq_row:
        gpu_freq_row = [freq_cur] * 3
    else:
        gpu_freq_row[0] = freq_cur
        gpu_freq_row[1] = min(freq_cur, gpu_freq_row[1])
        gpu_freq_row[2] = max(freq_cur, gpu_freq_row[2])


    s = 'GPU frequency [Cur      Min       Max]\n' + ''.ljust(14) + '   '.join(str(x) + ' MHz' for x in gpu_freq_row) + '\n'
    return s


def hdd_temperature():
    temp_cur = int(subprocess.check_output(['hddtemp', '/dev/sda', '-n']))
    global hdd_temp_row
    if not hdd_temp_row:
            hdd_temp_row = [temp_cur] * 3
    else:
        hdd_temp_row[0] = temp_cur
        hdd_temp_row[1] = min(temp_cur, hdd_temp_row[1])
        hdd_temp_row[2] = max(temp_cur, hdd_temp_row[2])

    s = 'HDD temperature [Cur    Min     Max]\n' + ''.ljust(16) + '   '.join(str(x) + ' °C' for x in hdd_temp_row) + '\n'
    return s


def bat_voltage():
    path = '/sys/class/power_supply/BAT1/voltage_now'
    
    voltage_cur = 0
    with open(path, 'r') as f:
        voltage_cur = int(f.readline()) / 1000000

    global bat_voltage_row
    if not bat_voltage_row:
        bat_voltage_row = [voltage_cur] * 3
    else:
        bat_voltage_row[0] = voltage_cur
        bat_voltage_row[1] = min(voltage_cur, bat_voltage_row[1])
        bat_voltage_row[2] = max(voltage_cur, bat_voltage_row[2])

    s = 'Battery voltage [Cur      Min       Max]\n' + ''.ljust(16) + '   '.join('{:.2f} V'.format(x) for x in bat_voltage_row) + '\n'
    return s


def bat_charge():
    charge_filenames = ('now', 'full', 'full_design')

    path = '/sys/class/power_supply/BAT1/charge_'
    
    global bat_charge_row   
    if not bat_charge_row:
        for filename in charge_filenames:
            with open(path + filename) as f:
                bat_charge_row.append(int(int(f.readline()) / 1000))
    else:
        for i, filename in enumerate(charge_filenames[0:1]):
            with open(path + filename) as f:
                bat_charge_row[i] = int(int(f.readline()) / 1000)

    header_str = 'Battery charge [Cur       Full       Full Design]\n'
    s = header_str + ''.ljust(15) + '   '.join(str(x) + ' mWh' for x in bat_charge_row) + '\n'
    return s    


cpu_name_str = cpu_name()
gpu_name_str = gpu_name()
hdd_name_str = hdd_name()


#TODO:
#   1: Add Hardware info from dmidecode
#   2: Add name for CPU, GPU to Monitor (Done + )
#   3: Add GUI
#   4: Add Threads


if __name__ == '__main__':
    main()