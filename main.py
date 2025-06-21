import subprocess
from netmiko import ConnectHandler
from threading import Thread
from tqdm import tqdm
import tabulate
import getpass
import numpy as np
from colorama import Fore, Style, init

# Initialize colorama
init()

def read_dhcp_servers(filename):
    with open(filename, "r") as file:
        dhcp_servers = file.read().splitlines()
    return dhcp_servers

def set_mac_address_on_dhcp_servers(mac_address_full, dhcp_servers):
    mac_addressPC = mac_address_full.replace(":", "").replace(".", "")
    
    total_scopes = 0
    current_scope = 0
    for server in dhcp_servers:
        ps_command = f"Get-DhcpServerv4Scope -ComputerName {server} | Select-Object ScopeId"
        output = subprocess.run(["powershell", ps_command], capture_output=True)
        scope_ids = output.stdout.decode("utf-8").strip().split("\n")
        total_scopes += len(scope_ids)

    for server in dhcp_servers:
        ps_command = f"Get-DhcpServerv4Scope -ComputerName {server} | Select-Object ScopeId"
        output = subprocess.run(["powershell", ps_command], capture_output=True)
        scope_ids = output.stdout.decode("utf-8").strip().split("\n")

        for scope_id in scope_ids:
            scope_id = scope_id.strip().split(" ")[-1]
            ps_command = f"Get-DhcpServerv4Lease -ComputerName {server} -ScopeId {scope_id} -ClientId {mac_addressPC} | Select-Object IPAddress"
            output = subprocess.run(["powershell", ps_command], capture_output=True)
            output_str = output.stdout.decode("utf-8")
            current_scope += 1
            progress = (current_scope / total_scopes) * 100
            print(f"{Fore.BLUE}🔍 {current_scope} out of {total_scopes} scopes searched. {progress:.2f}% completed.{Style.RESET_ALL}")
            if "IPAddress" in output_str:
                PC_ip = output_str.strip().split(" ")[-1]
                return PC_ip
    return None

def search_ip_City17():
    mac_address_full = input(f"{Fore.CYAN}Введите полный MAC адрес или скопируйте из таблицы: {Style.RESET_ALL}").strip()
    dhcp_servers = read_dhcp_servers("dhcp_servers_City17.txt")
    PC_ip = set_mac_address_on_dhcp_servers(mac_address_full, dhcp_servers)
    if PC_ip:
        print(f"{Fore.CYAN}IP адрес для MAC адреса {mac_address_full}: {PC_ip}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}IP адрес для MAC адреса {mac_address_full} не найден.{Style.RESET_ALL}")

def search_ip_City18():
    mac_address_full = input(f"{Fore.CYAN}Введите полный MAC адрес или скопируйте из таблицы: {Style.RESET_ALL}").strip()
    dhcp_servers = read_dhcp_servers("dhcp_servers_City18.txt")
    PC_ip = set_mac_address_on_dhcp_servers(mac_address_full, dhcp_servers)
    if PC_ip:
        print(f"{Fore.CYAN}IP адрес для MAC адреса {mac_address_full}: {PC_ip}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}IP адрес для MAC адреса {mac_address_full} не найден.{Style.RESET_ALL}")

def search_ip_City19():
    mac_address_full = input(f"{Fore.CYAN}Введите полный MAC адрес или скопируйте из таблицы: {Style.RESET_ALL}").strip()
    dhcp_servers = read_dhcp_servers("dhcp_servers_City19.txt")
    PC_ip = set_mac_address_on_dhcp_servers(mac_address_full, dhcp_servers)
    if PC_ip:
        print(f"{Fore.CYAN}IP адрес для MAC адреса {mac_address_full}: {PC_ip}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}IP адрес для MAC адреса {mac_address_full} не найден.{Style.RESET_ALL}")

def search_ip_City20():
    mac_address_full = input(f"{Fore.CYAN}Введите полный MAC адрес или скопируйте из таблицы: {Style.RESET_ALL}").strip()
    dhcp_servers = read_dhcp_servers("dhcp_servers_City20.txt")
    PC_ip = set_mac_address_on_dhcp_servers(mac_address_full, dhcp_servers)
    if PC_ip:
        print(f"{Fore.CYAN}IP адрес для MAC адреса {mac_address_full}: {PC_ip}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}IP адрес для MAC адреса {mac_address_full} не найден.{Style.RESET_ALL}")

def connect_to_switch_search_double_cisco(switch_ip, username, password, table, pbar):
    try:
        net_connect = ConnectHandler(ip=switch_ip, device_type='cisco_ios', username=username, password=password)
        output = net_connect.send_command(f"show mac address-table")
        net_connect.disconnect()
    except:
        print(f"{Fore.RED}Не удалось подключиться к указанному IP адресу: {switch_ip}{Style.RESET_ALL}")
        pbar.update(1)
        return

    for line in output.split("\n"):
        if "    " in line:
            elements = line.split()
            if elements[0] not in ["Mac", "Vlan", "----"]:
                if elements[3] not in ["Po1", "Po2", "Po3", "Po6", "CPU"]:
                    table.append([switch_ip, elements[1], elements[0], elements[2], elements[3], elements[3]])
    pbar.update(1)

def search_double_ports_City17_cisco():
        username = input(f"{Fore.YELLOW}Enter Username: {Style.RESET_ALL}")
        password = getpass.getpass(f"{Fore.YELLOW}Enter Password: {Style.RESET_ALL}")
        table = []
        with open("ip_list_City17_cisco.txt", "r") as f:
            ip_list = f.read().splitlines()

        pbar = tqdm(total=len(ip_list), desc="🔗 Подключение к коммутаторам")

        threads = []
        for switch_ip in ip_list:
            t = Thread(target=connect_to_switch_search_double_cisco, args=(switch_ip, username, password, table, pbar))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()
        pbar.close()

        sorted_table = sorted(table, key=lambda x: x[4])

        # Фильтруем дополнительные аплинки, чтобы исключить их из поиска
        matrix_fil = np.array(sorted_table)
        result_fil = matrix_fil.copy()
        for i in range(len(result_fil)):
            a = '10.50.2.16'
            b = 'Gi1/0/47'
            if result_fil[i][0] == a and result_fil[i][4] == b:
                result_fil[i][4] = "UPLINK"

        sorted_table = list(filter(lambda x: 'UPLINK' not in x[4], result_fil))

        matrix = np.array(sorted_table)
        result = matrix.copy()
        for i in range(len(matrix)):
            a = matrix[i][4]
            b = matrix[i][2]
            c = matrix[i][0]
            if a != matrix[i - 1][4] and b != matrix[i - 1][2] and c != matrix[i - 1][0]:
                result[i][4] = a
            if a == matrix[i - 1][4] and b == matrix[i - 1][2] and c == matrix[i - 1][0]:
                result[i -1][4] = "DOUBLE"
                result[i][4] = "DOUBLE"

        print(f"{Fore.GREEN}Результат поиска:{Style.RESET_ALL}")
        sorted_result = sorted(result, key=lambda x: x[0])
        sorted_result = list(filter(lambda x: 'DOUBLE' in x[4], sorted_result))

        print(tabulate.tabulate(sorted_result, headers="firstrow", tablefmt="fancy_grid"))

def connect_to_switch_with_mac_cisco(switch_ip, username, password, mac_address_cisco, table, pbar):
    try:
        net_connect = ConnectHandler(ip=switch_ip, device_type='cisco_ios', username=username, password=password)
        output = net_connect.send_command(f"show mac address-table | include {mac_address_cisco}")
        net_connect.disconnect()
    except:
        print(f"{Fore.RED} Не удалось подключиться к указанному IP адресу: {switch_ip}{Style.RESET_ALL}")
        pbar.update(1)
        return

    for line in output.split("\n"):
        if "    " in line:
            elements = line.split()
            if elements[3] not in ["Po1", "Po2", "Po3", "CPU"]:
                table.append([switch_ip, elements[1], elements[0], elements[3]])
    pbar.update(1)

def search_mac_City17_cisco():
    username = input(f"{Fore.YELLOW}Введите Username: {Style.RESET_ALL}")
    password = getpass.getpass(f"{Fore.YELLOW}Введите Password: {Style.RESET_ALL}")

    mac_address_cisco = input(f"{Fore.CYAN}Введите минимум два значения от MAC-адреса устройства: {Style.RESET_ALL}").strip()

    table = [["Switch IP", "MAC Address", "VLAN", "Port"]]
    with open("ip_list_City17_cisco.txt", "r") as f:
        ip_list = f.read().splitlines()

    pbar = tqdm(total=len(ip_list), desc="🔗 Подключение к коммутаторам")

    threads = []
    for switch_ip in ip_list:
        t = Thread(target=connect_to_switch_with_mac_cisco, args=(switch_ip, username, password, mac_address_cisco, table, pbar))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    pbar.close()

    sorted_table = sorted(table, key=lambda x: x[3])

    # Фильтруем дополнительные аплинки, чтобы исключить их из поиска
    matrix_fil = np.array(sorted_table)
    result_fil = matrix_fil.copy()
    for i in range(len(result_fil)):
        a = '10.50.2.16'
        b = 'Gi1/0/47'
        if result_fil[i][0] == a and result_fil[i][3] == b:
            result_fil[i][3] = "UPLINK"

    sorted_table = list(filter(lambda x: 'UPLINK' not in x[3], result_fil))

    sorted_result = sorted(sorted_table, key=lambda x: x[0])

    print(f"{Fore.GREEN}Результат поиска:{Style.RESET_ALL}")
    print(tabulate.tabulate(sorted_result, headers="firstrow", tablefmt="fancy_grid"))

def connect_to_switch_search_double_H3C(switch_ip, username, password, table, pbar):
    try:
        net_connect = ConnectHandler(ip=switch_ip, device_type='hp_comware', username=username, password=password)
        output = net_connect.send_command(f"dis mac-address")
        net_connect.disconnect()
    except:
        print(f"{Fore.RED}Не удалось подключиться к указанному IP адресу: {switch_ip}{Style.RESET_ALL}")
        pbar.update(1)
        return

    for line in output.split("\n"):
        if "    " in line:
            elements = line.split()
            if elements[0] not in ["MAC"]:
                #Исключаем основные аплинки
                if elements[3] not in ["BAGG1", "BAGG2", "BAGG3", "BAGG4", "XGE1/0/24", "XGE1/0/52", "XGE1/0/1", "XGE1/0/2", "XGE1/0/3", "XGE1/0/4", "XGE1/0/5", "XGE1/0/6", "XGE1/0/7", "XGE1/0/8"]:
                    table.append([switch_ip, elements[0], elements[1], elements[2], elements[3], elements[3]])
    pbar.update(1)

def search_double_ports_City17_H3C():
        username = input(f"{Fore.YELLOW}Enter Username: {Style.RESET_ALL}")
        password = getpass.getpass(f"{Fore.YELLOW}Enter Password: {Style.RESET_ALL}")

        table = []
        with open("ip_list_City17_H3C.txt", "r") as f:
            ip_list = f.read().splitlines()

        pbar = tqdm(total=len(ip_list), desc="🔗 Подключение к коммутаторам")

        threads = []
        for switch_ip in ip_list:
            t = Thread(target=connect_to_switch_search_double_H3C, args=(switch_ip, username, password, table, pbar))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()
        pbar.close()

        sorted_table = sorted(table, key=lambda x: x[4])

        # Фильтруем дополнительные аплинки, чтобы исключить их из таблицы
        matrix_fil = np.array(sorted_table)
        result_fil = matrix_fil.copy()
        for i in range(len(result_fil)):
            a = '10.50.2.59'
            b = 'GE1/0/8'
            if result_fil[i][0] == a and result_fil[i][4] == b:
                result_fil[i][4] = "UPLINK"

        sorted_table = list(filter(lambda x: 'UPLINK' not in x[4], result_fil))

        matrix = np.array(sorted_table)
        result = matrix.copy()
        for i in range(len(matrix)):
            a = matrix[i][4]
            b = matrix[i][2]
            c = matrix[i][0]
            if a != matrix[i - 1][4] and b != matrix[i - 1][2] and c != matrix[i - 1][0]:
                result[i][4] = a
            if a == matrix[i - 1][4] and b == matrix[i - 1][2] and c == matrix[i - 1][0]:
                result[i -1][4] = "DOUBLE"
                result[i][4] = "DOUBLE"

        print(f"{Fore.GREEN}Результат поиска:{Style.RESET_ALL}")
        sorted_result = sorted(result, key=lambda x: x[0])
        sorted_result = list(filter(lambda x: 'DOUBLE' in x[4], sorted_result))

        print(tabulate.tabulate(sorted_result, headers="firstrow", tablefmt="fancy_grid"))

def connect_to_switch_with_mac_H3C(switch_ip, username, password, mac_address_H3C, table, pbar):
    try:
        net_connect = ConnectHandler(ip=switch_ip, device_type='hp_comware', username=username, password=password)
        output = net_connect.send_command(f"dis mac-address | include {mac_address_H3C}")
        net_connect.disconnect()
    except:
        print(f"{Fore.RED} Не удалось подключиться к указанному IP адресу: {switch_ip}{Style.RESET_ALL}")
        pbar.update(1)
        return

    for line in output.split("\n"):
        if "    " in line:
            elements = line.split()
            if elements[0] not in ["MAC Address"]:
                table.append([switch_ip, elements[0], elements[1], elements[3]])
    pbar.update(1)

def search_mac_City17_H3C():
    username = input(f"{Fore.YELLOW}Введите Username: {Style.RESET_ALL}")
    password = getpass.getpass(f"{Fore.YELLOW}Введите Password: {Style.RESET_ALL}")

    mac_address_H3C = input(f"{Fore.CYAN}Введите минимум два значения от MAC-адреса устройства: {Style.RESET_ALL}").strip()

    table = [["Switch IP", "MAC Address", "VLAN", "Port"]]
    with open("ip_list_City17_H3C.txt", "r") as f:
        ip_list = f.read().splitlines()

    pbar = tqdm(total=len(ip_list), desc="🔗 Подключение к коммутаторам")

    threads = []
    for switch_ip in ip_list:
        t = Thread(target=connect_to_switch_with_mac_H3C, args=(switch_ip, username, password, mac_address_H3C, table, pbar))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    pbar.close()

    sorted_table = sorted(table, key=lambda x: x[3])

    # Фильтруем дополнительные аплинки, чтобы исключить их из таблицы
    matrix_fil = np.array(sorted_table)
    result_fil = matrix_fil.copy()
    for i in range(len(result_fil)):
        a = '10.50.2.59'
        b = 'GE1/0/8'
        if result_fil[i][0] == a and result_fil[i][3] == b:
            result_fil[i][3] = "UPLINK"

    sorted_table = list(filter(lambda x: 'UPLINK' not in x[3], result_fil))

    sorted_result = sorted(sorted_table, key=lambda x: x[0])

    print(f"{Fore.GREEN}Результат поиска:{Style.RESET_ALL}")
    print(tabulate.tabulate(sorted_result, headers="firstrow", tablefmt="fancy_grid"))

def connect_to_switch_search_double_DLINK(switch_ip, username, password, table, pbar):
    try:
        net_connect = ConnectHandler(ip=switch_ip, device_type='dlink_ds', username=username, password=password)
        output = net_connect.send_command(f"sh fdb")
        net_connect.disconnect()
    except:
        print(f"{Fore.RED} Не удалось подключиться к указанному IP адресу: {switch_ip}{Style.RESET_ALL}")
        pbar.update(1)
        return

    for line in output.split("\n"):
        if "    " in line:
            elements = line.split()
            if elements[0] not in ["VID"]:
                if elements[0] not in ["----"]:
                    #Исключаем основные аплинки
                    if elements[3] not in ["25", "26", "27", "28", "CPU"]:
                        if elements[1] not in ["wifi-guest", "Wi-Fi_Guest", "management"]:
                            table.append([switch_ip, elements[2], elements[0], elements[1], elements[3], elements[3]])
    pbar.update(1)

def connect_to_switch_with_mac_DLINK(switch_ip, username, password, mac_address_DLINK, table, pbar):
    try:
        net_connect = ConnectHandler(ip=switch_ip, device_type='dlink_ds', username=username, password=password)
        output = net_connect.send_command(f"show fdb mac_address {mac_address_DLINK}")
        net_connect.disconnect()
    except:
        print(f"{Fore.RED} Не удалось подключиться к указанному IP адресу: {switch_ip}{Style.RESET_ALL}")
        pbar.update(1)
        return

    for line in output.split("\n"):
        if "    " in line:
            elements = line.split()
            if elements[0] not in ["VID"]:
                if elements[0] not in ["----"]:
                    #Исключаем основные аплинки
                    if elements[3] not in ["25", "26", "27", "28", "CPU"]:
                        table.append([switch_ip, elements[2], elements[0], elements[1], elements[3]])
    pbar.update(1)

def search_double_ports_City18_DLINK():
        username = input(f"{Fore.YELLOW}Enter Username: {Style.RESET_ALL}")
        password = getpass.getpass(f"{Fore.YELLOW}Enter Password: {Style.RESET_ALL}")

        table = []
        with open("ip_list_City18_DLINK.txt", "r") as f:
            ip_list = f.read().splitlines()

        pbar = tqdm(total=len(ip_list), desc="🔗 Подключение к коммутаторам")

        threads = []
        for switch_ip in ip_list:
            t = Thread(target=connect_to_switch_search_double_DLINK, args=(switch_ip, username, password, table, pbar))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()
        pbar.close()

        sorted_table = sorted(table, key=lambda x: x[4])

        matrix = np.array(sorted_table)
        result = matrix.copy()
        for i in range(len(matrix)):
            a = matrix[i][4]
            b = matrix[i][2]
            c = matrix[i][0]
            if a != matrix[i - 1][4] and b != matrix[i - 1][2] and c != matrix[i - 1][0]:
                result[i][4] = a
            if a == matrix[i - 1][4] and b == matrix[i - 1][2] and c == matrix[i - 1][0]:
                result[i -1][4] = "DOUBLE"
                result[i][4] = "DOUBLE"

        print(f"{Fore.GREEN}Результат поиска:{Style.RESET_ALL}")
        sorted_result = sorted(result, key=lambda x: x[0])
        sorted_result = list(filter(lambda x: 'DOUBLE' in x[4], sorted_result))

        print(tabulate.tabulate(sorted_result, headers="firstrow", tablefmt="fancy_grid"))

def search_double_ports_City18_cisco():
        username = input(f"{Fore.YELLOW}Enter Username: {Style.RESET_ALL}")
        password = getpass.getpass(f"{Fore.YELLOW}Enter Password: {Style.RESET_ALL}")

        table = []
        with open("ip_list_City18_cisco.txt", "r") as f:
            ip_list = f.read().splitlines()

        pbar = tqdm(total=len(ip_list), desc="🔗 Подключение к коммутаторам")

        threads = []
        for switch_ip in ip_list:
            t = Thread(target=connect_to_switch_search_double_cisco, args=(switch_ip, username, password, table, pbar))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()
        pbar.close()

        sorted_table = sorted(table, key=lambda x: x[4])

        # Фильтруем дополнительные аплинки, чтобы исключить их из поиска
        matrix_fil = np.array(sorted_table)
        result_fil = matrix_fil.copy()
        for i in range(len(result_fil)):
            a = '172.16.2.23'
            b = 'Gi0/21'
            if result_fil[i][0] == a and result_fil[i][4] == b:
                result_fil[i][4] = "UPLINK"

        sorted_table = list(filter(lambda x: 'UPLINK' not in x[4], result_fil))

        matrix = np.array(sorted_table)
        result = matrix.copy()
        for i in range(len(matrix)):
            a = matrix[i][4]
            b = matrix[i][2]
            c = matrix[i][0]
            if a != matrix[i - 1][4] and b != matrix[i - 1][2] and c != matrix[i - 1][0]:
                result[i][4] = a
            if a == matrix[i - 1][4] and b == matrix[i - 1][2] and c == matrix[i - 1][0]:
                result[i -1][4] = "DOUBLE"
                result[i][4] = "DOUBLE"

        print(f"{Fore.GREEN}Результат поиска:{Style.RESET_ALL}")
        sorted_result = sorted(result, key=lambda x: x[0])
        sorted_result = list(filter(lambda x: 'DOUBLE' in x[4], sorted_result))

        print(tabulate.tabulate(sorted_result, headers="firstrow", tablefmt="fancy_grid"))

def search_mac_City18_DLINK():
    username = input(f"{Fore.YELLOW}Введите Username: {Style.RESET_ALL}")
    password = getpass.getpass(f"{Fore.YELLOW}Введите Password: {Style.RESET_ALL}")


    mac_address_DLINK = input(f"{Fore.CYAN}Введите MAC-адреса устройства в формате(00-11-22-33-44-55): {Style.RESET_ALL}").strip()

    table = [["Switch IP", "MAC Address", "VLAN", "Port"]]
    with open("ip_list_City18_DLINK.txt", "r") as f:
        ip_list = f.read().splitlines()

    pbar = tqdm(total=len(ip_list), desc="🔗 Подключение к коммутаторам")

    threads = []
    for switch_ip in ip_list:
        t = Thread(target=connect_to_switch_with_mac_DLINK, args=(switch_ip, username, password, mac_address_DLINK, table, pbar))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    pbar.close()

    print(f"{Fore.GREEN}Результат поиска:{Style.RESET_ALL}")
    print(tabulate.tabulate(table, headers="firstrow", tablefmt="fancy_grid"))

def search_mac_City18_cisco():
    username = input(f"{Fore.YELLOW}Введите Username: {Style.RESET_ALL}")
    password = getpass.getpass(f"{Fore.YELLOW}Введите Password: {Style.RESET_ALL}")

    mac_address_cisco = input(f"{Fore.CYAN}Введите минимум два значения от MAC-адреса устройства: {Style.RESET_ALL}").strip()

    table = [["Switch IP", "MAC Address", "VLAN", "Port"]]
    with open("ip_list_City18_cisco.txt", "r") as f:
        ip_list = f.read().splitlines()

    pbar = tqdm(total=len(ip_list), desc="🔗 Подключение к коммутаторам")

    threads = []
    for switch_ip in ip_list:
        t = Thread(target=connect_to_switch_with_mac_cisco, args=(switch_ip, username, password, mac_address_cisco, table, pbar))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    pbar.close()

    sorted_table = sorted(table, key=lambda x: x[3])

    # Фильтруем дополнительные аплинки, чтобы исключить их из поиска
    matrix_fil = np.array(sorted_table)
    result_fil = matrix_fil.copy()
    for i in range(len(result_fil)):
        a = '172.16.2.23'
        b = 'Gi0/21'
        if result_fil[i][0] == a and result_fil[i][3] == b:
            result_fil[i][3] = "UPLINK"

    sorted_table = list(filter(lambda x: 'UPLINK' not in x[3], result_fil))

    sorted_result = sorted(sorted_table, key=lambda x: x[0])

    print(f"{Fore.GREEN}Результат поиска:{Style.RESET_ALL}")
    print(tabulate.tabulate(sorted_result, headers="firstrow", tablefmt="fancy_grid"))

def search_double_ports_City19_cisco():
        username = input(f"{Fore.YELLOW}Enter Username: {Style.RESET_ALL}")
        password = getpass.getpass(f"{Fore.YELLOW}Enter Password: {Style.RESET_ALL}")

        table = []
        with open("ip_list_City19_cisco.txt", "r") as f:
            ip_list = f.read().splitlines()

        pbar = tqdm(total=len(ip_list), desc="🔗 Подключение к коммутаторам")

        threads = []
        for switch_ip in ip_list:
            t = Thread(target=connect_to_switch_search_double_cisco, args=(switch_ip, username, password, table, pbar))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()
        pbar.close()

        sorted_table = sorted(table, key=lambda x: x[4])

        # Фильтруем дополнительные аплинки, чтобы исключить их из поиска
        matrix_fil = np.array(sorted_table)
        result_fil = matrix_fil.copy()
        for i in range(len(result_fil)):
            a = '10.24.2.244'
            b = 'Gi1/0/22'
            if result_fil[i][0] == a and result_fil[i][4] == b:
                result_fil[i][4] = "UPLINK"

        sorted_table = list(filter(lambda x: 'UPLINK' not in x[4], result_fil))

        matrix = np.array(sorted_table)
        result = matrix.copy()
        for i in range(len(matrix)):
            a = matrix[i][4] # № порта
            b = matrix[i][2] # № VLAN
            c = matrix[i][0] # IP адрес коммутатора
            if a != matrix[i - 1][4] and b != matrix[i - 1][2] and c != matrix[i - 1][0]:
                result[i][4] = a
            if a == matrix[i - 1][4] and b == matrix[i - 1][2] and c == matrix[i - 1][0]:
                result[i -1][4] = "DOUBLE"
                result[i][4] = "DOUBLE"

        print(f"{Fore.GREEN}Результат поиска:{Style.RESET_ALL}")
        sorted_result = sorted(result, key=lambda x: x[0])
        sorted_result = list(filter(lambda x: 'DOUBLE' in x[4], sorted_result))

        print(tabulate.tabulate(sorted_result, headers="firstrow", tablefmt="fancy_grid"))

def search_mac_City19_cisco():
    username = input(f"{Fore.YELLOW}Введите Username: {Style.RESET_ALL}")
    password = getpass.getpass(f"{Fore.YELLOW}Введите Password: {Style.RESET_ALL}")

    mac_address_cisco = input(f"{Fore.CYAN}Введите минимум два значения от MAC-адреса устройства: {Style.RESET_ALL}").strip()

    table = [["Switch IP", "MAC Address", "VLAN", "Port"]]
    with open("ip_list_City19_cisco.txt", "r") as f:
        ip_list = f.read().splitlines()

    pbar = tqdm(total=len(ip_list), desc="🔗 Подключение к коммутаторам")

    threads = []
    for switch_ip in ip_list:
        t = Thread(target=connect_to_switch_with_mac_cisco, args=(switch_ip, username, password, mac_address_cisco, table, pbar))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    pbar.close()

    sorted_table = sorted(table, key=lambda x: x[3])

    # Фильтруем дополнительные аплинки, чтобы исключить их из поиска
    matrix_fil = np.array(sorted_table)
    result_fil = matrix_fil.copy()
    for i in range(len(result_fil)):
        a = '10.24.2.244'
        b = 'Gi1/0/22'
        if result_fil[i][0] == a and result_fil[i][3] == b:
            result_fil[i][3] = "UPLINK"

    sorted_table = list(filter(lambda x: 'UPLINK' not in x[3], result_fil))

    sorted_result = sorted(sorted_table, key=lambda x: x[0])

    print(f"{Fore.GREEN}Результат поиска:{Style.RESET_ALL}")
    print(tabulate.tabulate(sorted_result, headers="firstrow", tablefmt="fancy_grid"))

def main():
    print(f"{Fore.CYAN}MAC address Tool{Style.RESET_ALL}")
    
    main_menu = f'Выберете действие:\n' \
                f'\t{Style.RESET_ALL}1. Найти неуправляемые {Style.BRIGHT + Fore.YELLOW}коммутаторы в City17 (Cisco)\n' \
                f'\t{Style.RESET_ALL}2. Найти неуправляемые {Style.BRIGHT + Fore.YELLOW}коммутаторы в City17 (H3C)\n' \
                f'\t{Style.RESET_ALL}3. Найти порт коммутатора по {Style.BRIGHT + Fore.YELLOW}MAC в City17 (Cisco)\n' \
                f'\t{Style.RESET_ALL}4. Найти порт коммутатора по {Style.BRIGHT + Fore.YELLOW}MAC в City17 (H3C)\n' \
                f'\t{Style.RESET_ALL}5. Найти неуправляемые {Style.BRIGHT + Fore.YELLOW}коммутаторы в City18 (D-Link)\n' \
                f'\t{Style.RESET_ALL}6. Найти неуправляемые {Style.BRIGHT + Fore.YELLOW}коммутаторы в City18 (Cisco)\n' \
                f'\t{Style.RESET_ALL}7. Найти порт коммутатора по {Style.BRIGHT + Fore.YELLOW}MAC в City18 (D-Link)\n' \
                f'\t{Style.RESET_ALL}8. Найти порт коммутатора по {Style.BRIGHT + Fore.YELLOW}MAC в City18 (Cisco)\n' \
                f'\t{Style.RESET_ALL}9. Найти неуправляемые {Style.BRIGHT + Fore.YELLOW}коммутаторы в City19 (Cisco)\n' \
                f'\t{Style.RESET_ALL}10. Найти порт коммутатора по {Style.BRIGHT + Fore.YELLOW}MAC в City19 (Cisco)\n' \
                f'\t{Style.RESET_ALL}100. Найти IP адрес по {Style.BRIGHT + Fore.YELLOW}MAC в City17\n' \
                f'\t{Style.RESET_ALL}101. Найти IP адрес по {Style.BRIGHT + Fore.YELLOW}MAC в City18\n' \
                f'\t{Style.RESET_ALL}102. Найти IP адрес по {Style.BRIGHT + Fore.YELLOW}MAC в City19\n' \
                f'\t{Style.RESET_ALL}103. Найти IP адрес по {Style.BRIGHT + Fore.YELLOW}MAC в City20\n' \
    while True:
        print(Style.RESET_ALL + main_menu)
        choice = input(f'{Style.RESET_ALL}Ваш выбор: ')

        if choice == '1':
            print(Fore.YELLOW + Style.BRIGHT + '\nПоиск неуправляемых коммутаторов в City17 (Cisco)')
            search_double_ports_City17_cisco()

        elif choice == '2':
            print(Fore.YELLOW + Style.BRIGHT + '\nПоиск неуправляемых коммутаторов в City17 (H3C)')
            search_double_ports_City17_H3C()

        elif choice == '3':
            print(Fore.YELLOW + Style.BRIGHT + '\nПоиск порта по mac-адресу на коммутаторах в City17 (Cisco)')
            search_mac_City17_cisco()

        elif choice == '4':
            print(Fore.YELLOW + Style.BRIGHT + '\nПоиск порта по mac-адресу на коммутаторах в City17 (H3C)')
            search_mac_City17_H3C()

        elif choice == '5':
            print(Fore.YELLOW + Style.BRIGHT + '\nПоиск неуправляемых коммутаторов в City18 (D-Link)')
            search_double_ports_City18_DLINK()

        elif choice == '6':
            print(Fore.YELLOW + Style.BRIGHT + '\nПоиск неуправляемых коммутаторов в City18 (Cisco)')
            search_double_ports_City18_cisco()

        elif choice == '7':
            print(Fore.YELLOW + Style.BRIGHT + '\nПоиск порта по mac-адресу на коммутаторах в City18 (D-Link)')
            search_mac_City18_DLINK()

        elif choice == '8':
            print(Fore.YELLOW + Style.BRIGHT + '\nПоиск порта по mac-адресу на коммутаторах в City18 (Cisco)')
            search_mac_City18_cisco()

        elif choice == '9':
            print(Fore.YELLOW + Style.BRIGHT + '\nПоиск неуправляемых коммутаторов в City19 (Cisco)')
            search_double_ports_City19_cisco()

        elif choice == '10':
            print(Fore.YELLOW + Style.BRIGHT + '\nПоиск порта по mac-адресу на коммутаторах в City19 (Cisco)')
            search_mac_City19_cisco()

        elif choice == '100':
            print(Fore.YELLOW + Style.BRIGHT + '\nПоиск IP адреса по mac-адресу в City17')
            search_ip_City17()

        elif choice == '101':
            print(Fore.YELLOW + Style.BRIGHT + '\nПоиск IP адреса по mac-адресу в City18')
            search_ip_City18()

        elif choice == '102':
            print(Fore.YELLOW + Style.BRIGHT + '\nПоиск IP адреса по mac-адресу в City19')
            search_ip_City19()

        elif choice == '103':
            print(Fore.YELLOW + Style.BRIGHT + '\nПоиск IP адреса по mac-адресу в City20')
            search_ip_City20()

        else:
            pass
        input(f'{Style.RESET_ALL}Для продолжения нажмите {Style.BRIGHT + Fore.YELLOW}ENTER ')
        
if __name__ == "__main__":
    main()
