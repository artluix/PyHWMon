
class SSD:

    def __init__(self):
        self.name = self.__name()
        self.temp_label = 'SSD'
        self.temp_row = []


    def get_name(self):
        return self.name


    def get_temp_label(self):
        return self.temp_label

    def get_temperature(self):
        self.__temperature()
        return self.temp_row


    def __name(self):
        path = 'sysfs/hdd_name'
        with open(path, 'r') as f:
            hdd_name_str = f.readline()
        return hdd_name_str.split(':')[1].lstrip(' ').rstrip('\n')


    def __temperature(self):
        path = 'sysfs/hdd_temp'
        with open(path, 'r') as f:
            temp_cur = int(f.readline())
        if not self.temp_row:
            self.temp_row = [temp_cur] * 3
        else:
            self.temp_row[0] = temp_cur
            self.temp_row[1] = min(temp_cur, self.temp_row[1])
            self.temp_row[2] = max(temp_cur, self.temp_row[2])
