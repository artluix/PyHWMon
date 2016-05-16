
class Battery:
    def __init__(self):
        self.name = self.__name()
        self.voltage_label = 'Voltage'
        self.voltage_row = []

        self.charge_header_label = 'Category'
        self.charge_header_row = ['Now', 'Full', 'Full Design']
        
        self.charge_label = 'Charge'
        self.charge_row = []

    def get_name(self):
        return self.name 


    def get_voltage_label(self):
        return self.voltage_label

    def get_voltage(self):
        self.__voltage()
        return self.voltage_row


    def get_charge_header_label(self):
        return self.charge_header_label

    def get_charge_header_row(self):
        return self.charge_header_row


    def get_charge_label(self):
        return self.charge_label

    def get_charge(self):
        self.__charge()
        return self.charge_row


    def __name(self):
        path_manufacturer = '/sys/class/power_supply/BAT1/manufacturer'
        path_model_name = '/sys/class/power_supply/BAT1/model_name'
        bat_name_str = ''
        with open(path_manufacturer, 'r') as f:
            bat_name_str = f.readline().rstrip('\n')
        with open(path_model_name, 'r') as f:
            bat_name_str += f.readline().rstrip('\n')
        return bat_name_str


    def __voltage(self):
        path = '/sys/class/power_supply/BAT1/voltage_now'
        voltage_cur = 0
        with open(path, 'r') as f:
            voltage_cur = int(f.readline()) / 1000000

        if not self.voltage_row:
            self.voltage_row = [voltage_cur] * 3
        else:
            self.voltage_row[0] = voltage_cur
            self.voltage_row[1] = min(voltage_cur, self.voltage_row[1])
            self.voltage_row[2] = max(voltage_cur, self.voltage_row[2])


    def __charge(self):
        charge_filenames = ('now', 'full', 'full_design')
        path = '/sys/class/power_supply/BAT1/charge_'  
        if not self.charge_row:
            for filename in charge_filenames:
                with open(path + filename) as f:
                    self.charge_row.append(int(int(f.readline()) / 1000))
        else:
            for i, filename in enumerate(charge_filenames[0:1]):
                with open(path + filename) as f:
                    self.charge_row[i] = int(int(f.readline()) / 1000)
