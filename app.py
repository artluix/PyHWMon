#!/usr/bin/env python

from gi import require_version
require_version('Gtk', '3.0')


from gi.repository import Gtk, GObject, Pango
import threading
import time
import json
import re


from host import Host
from cpu import CPU
from gpu_integrated import GPU_Integrated
from gpu_discrete import GPU_Discrete 
from ssd import SSD
from battery import Battery


INTERVAL = 1


class App(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)

        self.host = Host()
        self.cpu = CPU()
        self.gpu_integrated = GPU_Integrated()
        self.gpu_discrete = GPU_Discrete()
        self.ssd = SSD()
        self.bat = Battery()

        self.notebook = Gtk.Notebook()
        self.add(self.notebook)

        self.page_1 = Gtk.Box()
        self.__fill_page_1()
        self.notebook.append_page(self.page_1, Gtk.Label('Hardware Monitor'))


        self.page_2 = Gtk.Box()
        self.__fill_page_2()
        self.notebook.append_page(self.page_2, Gtk.Label('Hardware Info'))


        self.page_3 = Gtk.Box()
        self.__fill_page_3()
        self.notebook.append_page(self.page_3, Gtk.Label('About'))

#---------------------------------------------- PAGE 1 -------------------------------------------------------------

    def __fill_page_1(self):
        self.store_1 = Gtk.TreeStore(str, str, str, str) 
        treeview = Gtk.TreeView(self.store_1)
        treeview.set_enable_tree_lines(True)
        treeview.modify_font(Pango.FontDescription('monaco 10'))
        renderer = Gtk.CellRendererText()

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.add(treeview)
        self.page_1.pack_start(scrolled_window, True, True, 0)

        columns = ('Sensor', 'Value', 'Min', 'Max')
        for i in range(len(columns)):
            column = Gtk.TreeViewColumn(columns[i], renderer, text=i)
            treeview.append_column(column)

        self.__add_nodes_to_store_1()
        treeview.expand_all()

        self.__add_threads()
        self.__set_threads_daemons()
        self.__start_threads()


    def __add_nodes_to_store_1(self):
        host_node = self.store_1.append(None, [self.host.get_name()] + [''] * 3 )

        cpu_node = self.store_1.append(host_node, [self.cpu.get_name()] + [''] * 3)

        cpu_temp_node = self.store_1.append(cpu_node, ['Temperature'] + [''] * 3)
        self.cpu_temp_value_nodes = []     
        for t_l in self.cpu.get_temp_labels():
            self.cpu_temp_value_nodes.append(self.store_1.append(cpu_temp_node, [t_l] + [''] * 3))

        cpu_freq_node = self.store_1.append(cpu_node, ['Frequency'] + [''] * 3)
        self.cpu_freq_value_nodes = []     
        for f_l in self.cpu.get_freq_labels():
            self.cpu_freq_value_nodes.append(self.store_1.append(cpu_freq_node, [f_l] + [''] * 3))

        cpu_usage_node = self.store_1.append(cpu_node, ['Usage'] + [''] * 3)
        self.cpu_usage_value_nodes = []     
        for u_l in self.cpu.get_usage_labels():
            self.cpu_usage_value_nodes.append(self.store_1.append(cpu_usage_node, [u_l] + [''] * 3))

        gpu_interated_node = self.store_1.append(host_node, [self.gpu_integrated.get_name()] + [''] * 3)
        gpu_integrated_freq_node = self.store_1.append(gpu_interated_node, ['Frequency'] + [''] * 3)
        self.gpu_integrated_freq_value_node = self.store_1.append(gpu_integrated_freq_node, \
            [self.gpu_integrated.get_freq_label()] + [''] * 3)

        gpu_discrete_node = self.store_1.append(host_node, [self.gpu_discrete.get_name()] + [''] * 3)
        gpu_discrete_temp_node = self.store_1.append(gpu_discrete_node, ['Temperature'] + [''] * 3)
        self.gpu_discrete_temp_value_node = self.store_1.append(gpu_discrete_temp_node, \
            [self.gpu_discrete.get_temp_label()] + [''] * 3)

        ssd_node = self.store_1.append(host_node, [self.ssd.get_name()] + [''] * 3)

        ssd_temp_node = self.store_1.append(ssd_node, ['Temperature'] + [''] * 3)
        self.ssd_temp_value_node = self.store_1.append(ssd_temp_node, [self.ssd.get_temp_label()] + [''] * 3)

        bat_node = self.store_1.append(host_node, [self.bat.get_name()] + [''] * 3)

        bat_voltage_node = self.store_1.append(bat_node, ['Voltage'] + [''] * 3)
        self.bat_voltage_value_node = self.store_1.append(bat_voltage_node, [self.bat.get_voltage_label()] + [''] * 3) 

        bat_charge_node = self.store_1.append(bat_node, ['Charge'] + [''] * 3)
        self.store_1.append(bat_charge_node, [self.bat.get_charge_header_label()] + self.bat.get_charge_header_row())
        self.bat_charge_value_node = self.store_1.append(bat_charge_node, [self.bat.get_charge_label()] + [''] * 3)


    def __add_threads(self):
        sensors_update_callbacks = [
                                    self.__cpu_temp_update_callback, 
                                    self.__cpu_freq_update_callback,
                                    self.__cpu_usage_update_callback, 
                                    self.__gpu_integrated_freq_update_callback, 
                                    self.__gpu_discrete_temp_update_callback, 
                                    self.__ssd_temp_update_callback, 
                                    self.__bat_voltage_update_callback, 
                                    self.__bat_charge_update_callback
                                    ]

        self.sensors_threads = []
        for c in sensors_update_callbacks:
            self.sensors_threads.append(threading.Thread(target=self.__thread_callback, args=[c]))

    def __thread_callback(self, update_func):
        while True:
            GObject.idle_add(update_func)
            time.sleep(INTERVAL)
    
    def __set_threads_daemons(self):
        for t in self.sensors_threads:
            t.daemon = True

    def __start_threads(self):
        for t in self.sensors_threads:
            t.start()



    def __cpu_temp_update_callback(self):
        cpu_temperature = self.cpu.get_temperature()
        for i, cpu_temp_row in enumerate(zip(*cpu_temperature)):
            self.store_1[self.cpu_temp_value_nodes[i]][1:] = [str(x) + ' °C' for x in cpu_temp_row]


    def __cpu_freq_update_callback(self):
        cpu_frequency = self.cpu.get_frequency()
        for i, cpu_freq_row in enumerate(zip(*cpu_frequency)):
            self.store_1[self.cpu_freq_value_nodes[i]][1:] = [str(x) + ' MHz' for x in cpu_freq_row]

    def __cpu_usage_update_callback(self):
        cpu_usage = self.cpu.get_usage()
        for i, cpu_usage_row in enumerate(zip(*cpu_usage)):
            self.store_1[self.cpu_usage_value_nodes[i]][1:] = [str(x) + ' %' for x in cpu_usage_row]


    def __gpu_integrated_freq_update_callback(self):
        gpu_freq_row = self.gpu_integrated.get_frequency()
        self.store_1[self.gpu_integrated_freq_value_node][1:] = [str(x) + ' MHz' for x in gpu_freq_row]

    def __gpu_discrete_temp_update_callback(self):
        gpu_temp_row = self.gpu_discrete.get_temperature()
        self.store_1[self.gpu_discrete_temp_value_node][1:] = [str(x) + ' °C' for x in gpu_temp_row]


    def __ssd_temp_update_callback(self):
        ssd_temp_row = self.ssd.get_temperature()
        self.store_1[self.ssd_temp_value_node][1:] = [str(x) + ' °C' for x in ssd_temp_row]


    def __bat_voltage_update_callback(self):
        bat_voltage_row = self.bat.get_voltage()
        self.store_1[self.bat_voltage_value_node][1:] = [str(x) + ' V' for x in bat_voltage_row]

    def __bat_charge_update_callback(self):
        bat_charge_row = self.bat.get_charge()
        self.store_1[self.bat_charge_value_node][1:] = [str(x) + ' mWh' for x in bat_charge_row]

#---------------------------------------------- PAGE 2 -------------------------------------------------------------

    def __fill_page_2(self):
        self.store_2 = Gtk.TreeStore(str)
        treeview = Gtk.TreeView(self.store_2)
        treeview.set_enable_tree_lines(True)
        treeview.modify_font(Pango.FontDescription('monaco 10'))
        renderer = Gtk.CellRendererText()

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.add(treeview)
        self.page_2.pack_start(scrolled_window, True, True, 0)

        column = Gtk.TreeViewColumn('List Hardware', renderer, text=0)
        treeview.append_column(column)

        self.dimms = self.__read_dimms()

        data = self.__read_lshw()
        self.__parse_json_to_store_2(data)


    def __read_dimms(self):
        path = 'sysfs/decode_dimms'
        with open(path, 'r') as f:
            s = f.read()
        return s.split('\n\n\n')[1:3]


    def __parse_dimm(self, dimm, parent_node, i):
        dimm_blks = dimm.split('\n\n')
        dimm_header = dimm_blks[0].split('\n')
        dimm_header[0], dimm_header[1] = dimm_header[1], dimm_header[0]
        dimm_blks[0] = dimm_header[1]

        dimm_name = dimm_header[0][48:-1] + str(i)
        dimm_from_name = dimm_header[1].split(':')[0]
        dimm_from_path = dimm_header[1].split(':')[1].lstrip(' ')

        name_node = self.store_2.append(parent_node, [dimm_name])
        k_node = self.store_2.append(name_node, [dimm_from_name])
        self.store_2.append(k_node, [dimm_from_path])

        for blk in dimm_blks[1:]:
            blk_l = blk.split('\n')
            blk_name = blk_l[0].split('===')[1][1:-1]
            blk_name_node = self.store_2.append(name_node, [blk_name])
            for s in blk_l[1:]:
                k = s[0:48].rstrip(' ')
                v = s[48:]
                k_node = self.store_2.append(blk_name_node, [k])
                self.store_2.append(k_node, [v])


    def __read_lshw(self):
        path = 'sysfs/lshw'
        with open(path, 'r') as f:
            data_str = f.read()
        return json.loads(data_str)


    def __parse_json_to_store_2(self, d, parent_node=None):
        if type(d) is dict:
            if 'id' in d:
                if re.match('bank:[0-9]', d['id']):
                    n = int(d['id'][-1])
                    if n in (0, 2):
                        n >>= 1
                        self.__parse_dimm(self.dimms[n], parent_node, n)
                else:
                    parent_node = self.store_2.append(parent_node, [str(d['id'])])
                    del(d['id'])
                    for k in d:
                        if k not in ('capabilities', 'configuration', 'children'):
                            key_node = self.store_2.append(parent_node, [str(k)])
                            if type(d[k]) is not list:
                                value_node = self.store_2.append(key_node, [str(d[k])])
                            else:
                                for v in d[k]:
                                    value_node = self.store_2.append(key_node, [str(v)])
                        elif k in ('configuration', 'capabilities'):
                            key_node = self.store_2.append(parent_node, [str(k)])
                            value_dict = d[k]
                            for k_dict in value_dict:
                                key_l_node = self.store_2.append(key_node, [str(k_dict)])
                                self.store_2.append(key_l_node, [str(value_dict[k_dict])])

                if 'children' in d:
                    for list_dict in d['children']:
                        self.__parse_json_to_store_2(list_dict, parent_node)

#---------------------------------------------- PAGE 3 -------------------------------------------------------------

    def __fill_page_3(self):
        textview = Gtk.TextView()
        textview.modify_font(Pango.FontDescription('Droid Sans 14'))
        textview.set_editable(False)
        textview.set_cursor_visible(False)
        textview.set_justification(Gtk.Justification.CENTER)
        textbuffer = textview.get_buffer()
        s = '\n\n\n\n\n\n\n\n\nThis program is brought to you by\nArtluix - Daineko Stanislau\nSt. of BSUIR of FKSiS\nof chair of Informatics\n\nBig thanks and credits to devs of:\ndecode-dimms\n lshw\n hdparm\n hddtemp'
        textbuffer.set_text(s)
        self.page_3.pack_start(textview, True, True, 0)


def main():
    GObject.threads_init()
    app = App()
    app.connect('delete-event', Gtk.main_quit)
    app.show_all()
    Gtk.main()


if __name__ == '__main__':
    main()
