
class GPU_Discrete:

    def __init__(self):
        self.name = self.__name() 
        self.temp_label = 'GPU Discrete'
        self.temp_row = []


    def get_name(self):
        return self.name 


    def get_temp_label(self):
        return self.temp_label

    def get_temperature(self):
        self.__temperature()
        return self.temp_row

    
    def __name(self):
        path = 'sysfs/gpu_discrete_name'
        with open(path, 'r') as f:
            gpu_name_str = f.readline()
        return gpu_name_str.split('VGA compatible controller: ')[1].rstrip('\n')


    def __temperature(self):
        path = 'sysfs/gpu_discrete_temp'
        with open(path, 'r') as f:
            l = f.readlines()
            if not l:
                temp_cur = self.temp_row[0]
            else:
                temp_cur = int(l[-1])
            
        if not self.temp_row:
            self.temp_row = [temp_cur] * 3
        else:
            self.temp_row[0] = temp_cur    
            self.temp_row[1] = min(temp_cur, self.temp_row[2])    
            self.temp_row[2] = max(temp_cur, self.temp_row[2])    



