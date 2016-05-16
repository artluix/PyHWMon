
class GPU_Integrated:

    def __init__(self):
        self.name = self.__name()
        self.freq_label = 'GPU Integrated'
        self.freq_row = []


    def get_name(self):
        return self.name


    def get_freq_label(self):
        return self.freq_label

    def get_frequency(self):
        self.__frequency()
        return self.freq_row


    def __name(self):
        path = 'sysfs/gpu_integrated_name'
        with open(path, 'r') as f:
            gpu_name_str = f.readline()
        return gpu_name_str.split('VGA compatible controller: ')[1].rstrip('\n')

    def __frequency(self):
        path = '/sys/class/drm/card0/gt_cur_freq_mhz'
        freq_cur = 0
        with open(path, 'r') as f:
            freq_cur = int(f.readline())

        if not self.freq_row:
            self.freq_row = [freq_cur] * 3
        else:
            self.freq_row[0] = freq_cur
            self.freq_row[1] = min(freq_cur, self.freq_row[1])
            self.freq_row[2] = max(freq_cur, self.freq_row[2])
