import subprocess
from netmiko import ConnectHandler
from threading import Thread
from tqdm import tqdm
import tabulate
import getpass
import numpy as np
from colorama import Fore, Style, init
import re
from collections import Counter


# Initialize colorama
init()
firstpassword = getpass.getpass(f"{Fore.YELLOW}Введите пароль пользователя user для подключения к коммутаторам: {Style.RESET_ALL}")
UPLINK_VLAN_1 = "1"
UPLINK_VLAN = "2"

def normalize_mac(mac: str) -> str:
    return re.sub(r'[^0-9A-Fa-f]', '', mac).lower()

def port_key(row):
    return (row[0], row[2], row[4])

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

def connect_to_switch_with_mac_cisco(switch_ip, username, password, table, pbar):
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
                    table.append([switch_ip, elements[1], elements[0], elements[2], elements[3]])
    pbar.update(1)

def connect_to_switch_search_double_H3C(switch_ip, username, password, table, pbar):
    try:
        net_connect = ConnectHandler(ip=switch_ip, device_type='generic', username=username, password=password)
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

def connect_to_switch_with_mac_H3C(switch_ip, username, password, table, pbar):
    try:
        net_connect = ConnectHandler(ip=switch_ip, device_type='generic', username=username, password=password)
        output = net_connect.send_command(f"dis mac-address")
        net_connect.disconnect()
    except:
        print(f"{Fore.RED} Не удалось подключиться к указанному IP адресу: {switch_ip}{Style.RESET_ALL}")
        pbar.update(1)
        return

    for line in output.split("\n"):
        if "    " in line:
            elements = line.split()
            if elements[0] not in ["MAC"]:
                #Исключаем основные аплинки
                if elements[3] not in ["BAGG1", "BAGG2", "BAGG3", "BAGG4", "XGE1/0/24", "XGE1/0/52", "XGE1/0/1", "XGE1/0/2", "XGE1/0/3", "XGE1/0/4", "XGE1/0/5", "XGE1/0/6", "XGE1/0/7", "XGE1/0/8"]:
                    table.append([switch_ip, elements[0], elements[1], elements[2], elements[3]])
    pbar.update(1)

def connect_to_switch_with_mac_H3C_comware(switch_ip, username, password, table, pbar):
    try:
        net_connect = ConnectHandler(ip=switch_ip, device_type='hp_comware', username=username, password=password)
        output = net_connect.send_command(f"dis mac-address")
        net_connect.disconnect()
    except:
        print(f"{Fore.RED} Не удалось подключиться к указанному IP адресу: {switch_ip}{Style.RESET_ALL}")
        pbar.update(1)
        return

    for line in output.split("\n"):
        if "    " in line:
            elements = line.split()
            if elements[0] not in ["MAC"]:
                #Исключаем основные аплинки
                if elements[3] not in ["BAGG1", "BAGG2", "BAGG3", "BAGG4", "XGE1/0/24", "XGE1/0/52", "XGE1/0/1", "XGE1/0/2", "XGE1/0/3", "XGE1/0/4", "XGE1/0/5", "XGE1/0/6", "XGE1/0/7", "XGE1/0/8"]:
                    table.append([switch_ip, elements[0], elements[1], elements[2], elements[3]])
    pbar.update(1)

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

def connect_to_switch_with_mac_DLINK(switch_ip, username, password, table, pbar):
    try:
        net_connect = ConnectHandler(ip=switch_ip, device_type='dlink_ds', username=username, password=password)
        output = net_connect.send_command(f"show fdb")
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

def search_double_ports_City17_cisco():
        username = "user"
        password = firstpassword
        #password = getpass.getpass(f"{Fore.YELLOW}Enter Password: {Style.RESET_ALL}")
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

        # Сортируем таблицу по номеру порта для сравнения в будущем, что если адрес коммутатора и номер порта совпадает
        # с предыдущим значением в массиве, то на порту больше одного мак адреса.
        # А это потенциально неуправляйка.
        sorted_table = sorted(table, key=lambda x: x[4])

# Фильтруем аплинки, чтобы исключить их из таблицы

        # (коммутатор, интерфейс), на которых виден MAC из VLAN 2
        uplinks = {(row[0], row[4]) for row in sorted_table if row[2] == UPLINK_VLAN}

        # убираем все строки, относящиеся к этим интерфейсам
        sorted_table = [row for row in sorted_table if (row[0], row[4]) not in uplinks]

# Конец фильтрации UPLINK

        # Фильтруем массив, исключая все порты UPLINK
        # Помечаем порт как MARK

        sorted_table = sorted(sorted_table, key=lambda x: x[4])
        # Считаем, сколько записей (MAC-адресов) на каждом порту
        counts = Counter(port_key(row) for row in sorted_table)
        HOLD = 2  # если MAC-адресов БОЛЬШЕ этого значения
        result = []
        for row in sorted_table:
            row = list(row)
            if counts[port_key(row)] > HOLD:
                row[4] = "MARK"
            result.append(row)

        print(f"{Fore.GREEN}Результат поиска:{Style.RESET_ALL}")
        sorted_result = sorted(result, key=lambda x: x[0])
        sorted_result = list(filter(lambda x: 'MARK' in x[4], sorted_result))

        print(tabulate.tabulate(sorted_result, headers="firstrow", tablefmt="fancy_grid"))

def search_double_ports_City17_H3C():
        username = "user"
        password = firstpassword
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

# Фильтруем аплинки, чтобы исключить их из таблицы

        # (коммутатор, интерфейс), на которых виден MAC из VLAN 2
        uplinks = {(row[0], row[4]) for row in sorted_table if row[2] == UPLINK_VLAN}

        # убираем все строки, относящиеся к этим интерфейсам
        sorted_table = [row for row in sorted_table if (row[0], row[4]) not in uplinks]

# Конец фильтрации UPLINK

        sorted_table = sorted(sorted_table, key=lambda x: x[4])
        counts = Counter(port_key(row) for row in sorted_table)
        HOLD = 2
        result = []
        for row in sorted_table:
            row = list(row)
            if counts[port_key(row)] > HOLD:
                row[4] = "MARK"
            result.append(row)

        print(f"{Fore.GREEN}Результат поиска:{Style.RESET_ALL}")
        sorted_result = sorted(result, key=lambda x: x[0])
        sorted_result = list(filter(lambda x: 'MARK' in x[4], sorted_result))

        print(tabulate.tabulate(sorted_result, headers="firstrow", tablefmt="fancy_grid"))

def search_mac_City17():
    username = "user"
    password = firstpassword
    mac_address = input(f"{Fore.CYAN}Введите MAC-адрес устройства (например последний октет): {Style.RESET_ALL}").strip()

    # City17 Cisco search mac strat 
    headers = ["Switch IP", "MAC Address", "Vlan", "Type", "Ports"]
    table = []
    with open("ip_list_City17_cisco.txt", "r") as f:
        ip_list = f.read().splitlines()

    pbar = tqdm(total=len(ip_list), desc="🔗 Подключение к коммутаторам")

    threads = []
    for switch_ip in ip_list:
        t = Thread(target=connect_to_switch_with_mac_cisco, args=(switch_ip, username, password, table, pbar))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    pbar.close()

    sorted_table = sorted(table, key=lambda x: x[4])

# Фильтруем аплинки, чтобы исключить их из таблицы

    # (коммутатор, интерфейс), на которых виден MAC из VLAN 2
    uplinks = {(row[0], row[4]) for row in sorted_table if row[2] == UPLINK_VLAN}

    # убираем все строки, относящиеся к этим интерфейсам
    sorted_table = [row for row in sorted_table if (row[0], row[4]) not in uplinks]

# Конец фильтрации UPLINK

    target = normalize_mac(mac_address)

    sorted_result = [
        row for row in sorted_table
        if normalize_mac(row[1]).endswith(target)
    ]

    print(f"{Fore.GREEN}Результат поиска на коммутаторах Cisco City17:{Style.RESET_ALL}")
    print(tabulate.tabulate(sorted_result, headers=headers, tablefmt="fancy_grid"))
    # City17 Cisco search mac end 

    # City17 H3C search mac strat 
    table = []
    with open("ip_list_City17_H3C.txt", "r") as f:
        ip_list = f.read().splitlines()

    pbar = tqdm(total=len(ip_list), desc="🔗 Подключение к коммутаторам")

    threads = []
    for switch_ip in ip_list:
        t = Thread(target=connect_to_switch_with_mac_H3C, args=(switch_ip, username, password, table, pbar))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    pbar.close()

    sorted_table = sorted(table, key=lambda x: x[4])

# Фильтруем аплинки, чтобы исключить их из таблицы

    # (коммутатор, интерфейс), на которых виден MAC из VLAN 2
    uplinks = {(row[0], row[4]) for row in sorted_table if row[2] == UPLINK_VLAN}

    # убираем все строки, относящиеся к этим интерфейсам
    sorted_table = [row for row in sorted_table if (row[0], row[4]) not in uplinks]

# Конец фильтрации UPLINK

    target = normalize_mac(mac_address)

    sorted_result = [
        row for row in sorted_table
        if normalize_mac(row[1]).endswith(target)
    ]

    print(f"{Fore.GREEN}Результат поиска на коммутаторах H3C City17:{Style.RESET_ALL}")
    print(tabulate.tabulate(sorted_result, headers=headers, tablefmt="fancy_grid"))
    # City17 H3C search mac end 

def search_double_ports_City18_DLINK():
        username = "user"
        password = firstpassword
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

        sorted_table = sorted(table, key=lambda x: x[0])

    # Фильтруем аплинки, чтобы исключить их из таблицы

        # (коммутатор, интерфейс), на которых виден MAC из VLAN 2
        uplinks = {(row[0], row[4]) for row in sorted_table if row[2] == UPLINK_VLAN_1}

        # убираем все строки, относящиеся к этим интерфейсам
        sorted_table = [row for row in sorted_table if (row[0], row[4]) not in uplinks]

        # (коммутатор, интерфейс), на которых виден MAC из VLAN 2
        uplinks = {(row[0], row[4]) for row in sorted_table if row[2] == UPLINK_VLAN}

        # убираем все строки, относящиеся к этим интерфейсам
        sorted_table = [row for row in sorted_table if (row[0], row[4]) not in uplinks]

# Конец фильтрации UPLINK

        sorted_table = sorted(sorted_table, key=lambda x: x[4])
        counts = Counter(port_key(row) for row in sorted_table)
        HOLD = 2
        result = []
        for row in sorted_table:
            row = list(row)
            if counts[port_key(row)] > HOLD:
                row[4] = "MARK"
            result.append(row)

        print(f"{Fore.GREEN}Результат поиска:{Style.RESET_ALL}")
        sorted_result = sorted(result, key=lambda x: x[0])
        sorted_result = list(filter(lambda x: 'MARK' in x[4], sorted_result))

        print(tabulate.tabulate(sorted_result, headers="firstrow", tablefmt="fancy_grid"))

def search_double_ports_City18_cisco():
        username = "user"
        password = firstpassword
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

# Фильтруем аплинки, чтобы исключить их из таблицы

        # (коммутатор, интерфейс), на которых виден MAC из VLAN 2
        uplinks = {(row[0], row[4]) for row in sorted_table if row[2] == UPLINK_VLAN}

        # убираем все строки, относящиеся к этим интерфейсам
        sorted_table = [row for row in sorted_table if (row[0], row[4]) not in uplinks]

# Конец фильтрации UPLINK

        sorted_table = sorted(sorted_table, key=lambda x: x[4])
        counts = Counter(port_key(row) for row in sorted_table)
        HOLD = 2
        result = []
        for row in sorted_table:
            row = list(row)
            if counts[port_key(row)] > HOLD:
                row[4] = "MARK"
            result.append(row)

        print(f"{Fore.GREEN}Результат поиска:{Style.RESET_ALL}")
        sorted_result = sorted(result, key=lambda x: x[0])
        sorted_result = list(filter(lambda x: 'MARK' in x[4], sorted_result))

        print(tabulate.tabulate(sorted_result, headers="firstrow", tablefmt="fancy_grid"))

def search_mac_City18_DLINK():
    username = "user"
    password = firstpassword
    mac_address = input(f"{Fore.CYAN}Введите MAC-адрес устройства (например последний октет): {Style.RESET_ALL}").strip()

    headers = ["Switch IP", "MAC Address", "VLAN", "NAME", "Port"]
    table = []
    with open("ip_list_City18_DLINK.txt", "r") as f:
        ip_list = f.read().splitlines()

    pbar = tqdm(total=len(ip_list), desc="🔗 Подключение к коммутаторам")

    threads = []
    for switch_ip in ip_list:
        t = Thread(target=connect_to_switch_with_mac_DLINK, args=(switch_ip, username, password, table, pbar))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    pbar.close()

    sorted_table = sorted(table, key=lambda x: x[4])

# Фильтруем аплинки, чтобы исключить их из таблицы

    # (коммутатор, интерфейс), на которых виден MAC из VLAN 2
    uplinks = {(row[0], row[4]) for row in sorted_table if row[2] == UPLINK_VLAN}

    # убираем все строки, относящиеся к этим интерфейсам
    sorted_table = [row for row in sorted_table if (row[0], row[4]) not in uplinks]

# Конец фильтрации UPLINK

    target = normalize_mac(mac_address)

    sorted_result = [
        row for row in sorted_table
        if normalize_mac(row[1]).endswith(target)
    ]

    print(f"{Fore.GREEN}Результат поиска на коммутаторах D-Link City18:{Style.RESET_ALL}")
    print(tabulate.tabulate(sorted_result, headers=headers, tablefmt="fancy_grid"))

def search_mac_City18():
    username = "user"
    password = firstpassword
    mac_address = input(f"{Fore.CYAN}Введите MAC-адрес устройства (например последний октет): {Style.RESET_ALL}").strip()

    # City18 Cisco search start
    headers = ["Switch IP", "MAC Address", "Vlan", "Type", "Ports"]
    table = []
    with open("ip_list_City18_cisco.txt", "r") as f:
        ip_list = f.read().splitlines()

    pbar = tqdm(total=len(ip_list), desc="🔗 Подключение к коммутаторам")

    threads = []
    for switch_ip in ip_list:
        t = Thread(target=connect_to_switch_with_mac_cisco, args=(switch_ip, username, password, table, pbar))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    pbar.close()

    sorted_table = sorted(table, key=lambda x: x[4])

# Фильтруем аплинки, чтобы исключить их из таблицы

    # (коммутатор, интерфейс), на которых виден MAC из VLAN 2
    uplinks = {(row[0], row[4]) for row in sorted_table if row[2] == UPLINK_VLAN}

    # убираем все строки, относящиеся к этим интерфейсам
    sorted_table = [row for row in sorted_table if (row[0], row[4]) not in uplinks]

# Конец фильтрации UPLINK

    target = normalize_mac(mac_address)

    sorted_result = [
        row for row in sorted_table
        if normalize_mac(row[1]).endswith(target)
    ]

    print(f"{Fore.GREEN}Результат поиска на коммутаторах Cisco City18:{Style.RESET_ALL}")
    print(tabulate.tabulate(sorted_result, headers=headers, tablefmt="fancy_grid"))
    # City18 Cisco search end

    # City18 H3C search start
    table = []
    with open("ip_list_City18_H3C.txt", "r") as f:
        ip_list = f.read().splitlines()

    pbar = tqdm(total=len(ip_list), desc="🔗 Подключение к коммутаторам")

    threads = []
    for switch_ip in ip_list:
        t = Thread(target=connect_to_switch_with_mac_H3C, args=(switch_ip, username, password, table, pbar))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    pbar.close()

    sorted_table = sorted(table, key=lambda x: x[4])

# Фильтруем аплинки, чтобы исключить их из таблицы

    # (коммутатор, интерфейс), на которых виден MAC из VLAN 2
    uplinks = {(row[0], row[4]) for row in sorted_table if row[2] == UPLINK_VLAN}

    # убираем все строки, относящиеся к этим интерфейсам
    sorted_table = [row for row in sorted_table if (row[0], row[4]) not in uplinks]

# Конец фильтрации UPLINK

    matrix = np.array(sorted_table)
    result = matrix.copy()
    for i in range(len(matrix)):
        c = matrix[i][4]

        if matrix[i][1].endswith(mac_address):
            result[i][4] = c
        else:
            result[i][4] = "NOTMAC"

    sorted_table = list(filter(lambda x: 'NOTMAC' not in x[4], result))

    sorted_result = sorted(sorted_table, key=lambda x: x[0])

    print(f"{Fore.GREEN}Результат поиска на коммутаторах H3C City18:{Style.RESET_ALL}")
    print(tabulate.tabulate(sorted_result, headers=headers, tablefmt="fancy_grid"))
    # City18 H3C search end

    # City18 D-Link search start
    headersdlink = ["Switch IP", "MAC Address", "VLAN", "NAME", "Port"]
    table = []
    with open("ip_list_City18_DLINK.txt", "r") as f:
        ip_list = f.read().splitlines()

    pbar = tqdm(total=len(ip_list), desc="🔗 Подключение к коммутаторам")

    threads = []
    for switch_ip in ip_list:
        t = Thread(target=connect_to_switch_with_mac_DLINK, args=(switch_ip, username, password, table, pbar))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    pbar.close()

    sorted_table = sorted(table, key=lambda x: x[4])

# Фильтруем аплинки, чтобы исключить их из таблицы

    # (коммутатор, интерфейс), на которых виден MAC из VLAN 2
    uplinks = {(row[0], row[4]) for row in sorted_table if row[2] == UPLINK_VLAN}

    # убираем все строки, относящиеся к этим интерфейсам
    sorted_table = [row for row in sorted_table if (row[0], row[4]) not in uplinks]

# Конец фильтрации UPLINK

    target = normalize_mac(mac_address)

    sorted_result = [
        row for row in sorted_table
        if normalize_mac(row[1]).endswith(target)
    ]

    print(f"{Fore.GREEN}Результат поиска на коммутаторах D-Link City18:{Style.RESET_ALL}")
    print(tabulate.tabulate(sorted_result, headers=headersdlink, tablefmt="fancy_grid"))
    # City18 D-Link search end

def search_double_ports_City19_cisco():
        username = "user"
        password = firstpassword
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

# Фильтруем аплинки, чтобы исключить их из таблицы

        # (коммутатор, интерфейс), на которых виден MAC из VLAN 2
        uplinks = {(row[0], row[4]) for row in sorted_table if row[2] == UPLINK_VLAN}

        # убираем все строки, относящиеся к этим интерфейсам
        sorted_table = [row for row in sorted_table if (row[0], row[4]) not in uplinks]

# Конец фильтрации UPLINK

        sorted_table = sorted(sorted_table, key=lambda x: x[4])
        counts = Counter(port_key(row) for row in sorted_table)
        HOLD = 2
        result = []
        for row in sorted_table:
            row = list(row)
            if counts[port_key(row)] > HOLD:
                row[4] = "MARK"
            result.append(row)

        print(f"{Fore.GREEN}Результат поиска:{Style.RESET_ALL}")
        sorted_result = sorted(result, key=lambda x: x[0])
        sorted_result = list(filter(lambda x: 'MARK' in x[4], sorted_result))

        print(tabulate.tabulate(sorted_result, headers="firstrow", tablefmt="fancy_grid"))

def search_double_ports_City19_H3C():
        username = "user"
        password = firstpassword
        table = []
        with open("ip_list_City19_H3C.txt", "r") as f:
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

# Фильтруем аплинки, чтобы исключить их из таблицы

        # (коммутатор, интерфейс), на которых виден MAC из VLAN 2
        uplinks = {(row[0], row[4]) for row in sorted_table if row[2] == UPLINK_VLAN}

        # убираем все строки, относящиеся к этим интерфейсам
        sorted_table = [row for row in sorted_table if (row[0], row[4]) not in uplinks]

# Конец фильтрации UPLINK

        sorted_table = sorted(sorted_table, key=lambda x: x[4])
        counts = Counter(port_key(row) for row in sorted_table)
        HOLD = 2
        result = []
        for row in sorted_table:
            row = list(row)
            if counts[port_key(row)] > HOLD:
                row[4] = "MARK"
            result.append(row)

        print(f"{Fore.GREEN}Результат поиска:{Style.RESET_ALL}")
        sorted_result = sorted(result, key=lambda x: x[0])
        sorted_result = list(filter(lambda x: 'MARK' in x[4], sorted_result))

        print(tabulate.tabulate(sorted_result, headers="firstrow", tablefmt="fancy_grid"))

def search_mac_City19():
    username = "user"
    password = firstpassword
    mac_address = input(f"{Fore.CYAN}Введите MAC-адрес устройства (например последний октет): {Style.RESET_ALL}").strip()

    # City19 cisco search start
    headers = ["Switch IP", "MAC Address", "Vlan", "Type", "Ports"]
    table = []
    with open("ip_list_City19_cisco.txt", "r") as f:
        ip_list = f.read().splitlines()

    pbar = tqdm(total=len(ip_list), desc="🔗 Подключение к коммутаторам")

    threads = []
    for switch_ip in ip_list:
        t = Thread(target=connect_to_switch_with_mac_cisco, args=(switch_ip, username, password, table, pbar))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    pbar.close()

    sorted_table = sorted(table, key=lambda x: x[4])

# Фильтруем аплинки, чтобы исключить их из таблицы

    # (коммутатор, интерфейс), на которых виден MAC из VLAN 2
    uplinks = {(row[0], row[4]) for row in sorted_table if row[2] == UPLINK_VLAN}

    # убираем все строки, относящиеся к этим интерфейсам
    sorted_table = [row for row in sorted_table if (row[0], row[4]) not in uplinks]

# Конец фильтрации UPLINK

    target = normalize_mac(mac_address)

    sorted_result = [
        row for row in sorted_table
        if normalize_mac(row[1]).endswith(target)
    ]

    print(f"{Fore.GREEN}Результат поиска на коммутаторах Cisco City19:{Style.RESET_ALL}")
    print(tabulate.tabulate(sorted_result, headers=headers, tablefmt="fancy_grid"))
    # City19 cisco search end

    # City19 H3C search start
    table = []
    with open("ip_list_City19_H3C.txt", "r") as f:
        ip_list = f.read().splitlines()

    pbar = tqdm(total=len(ip_list), desc="🔗 Подключение к коммутаторам")

    threads = []
    for switch_ip in ip_list:
        t = Thread(target=connect_to_switch_with_mac_H3C, args=(switch_ip, username, password, table, pbar))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    pbar.close()

    sorted_table = sorted(table, key=lambda x: x[4])

# Фильтруем аплинки, чтобы исключить их из таблицы

    # (коммутатор, интерфейс), на которых виден MAC из VLAN 2
    uplinks = {(row[0], row[4]) for row in sorted_table if row[2] == UPLINK_VLAN}

    # убираем все строки, относящиеся к этим интерфейсам
    sorted_table = [row for row in sorted_table if (row[0], row[4]) not in uplinks]

# Конец фильтрации UPLINK

    target = normalize_mac(mac_address)

    sorted_result = [
        row for row in sorted_table
        if normalize_mac(row[1]).endswith(target)
    ]

    print(f"{Fore.GREEN}Результат поиска на коммутаторах H3C City19:{Style.RESET_ALL}")
    print(tabulate.tabulate(sorted_result, headers=headers, tablefmt="fancy_grid"))
    # City19 H3C search end

def search_mac_full():
    username = "user"
    password = firstpassword
    mac_address = input(f"{Fore.CYAN}Введите MAC-адрес устройства (например последний октет): {Style.RESET_ALL}").strip()

    ############ City17 Cisco
    headers = ["Switch IP", "MAC Address", "Vlan", "Type", "Ports"]
    table = []
    with open("ip_list_City17_cisco.txt", "r") as f:
        ip_list = f.read().splitlines()

    pbar = tqdm(total=len(ip_list), desc="🔗 Подключение к коммутаторам")

    threads = []
    for switch_ip in ip_list:
        t = Thread(target=connect_to_switch_with_mac_cisco, args=(switch_ip, username, password, table, pbar))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    pbar.close()

    sorted_table = sorted(table, key=lambda x: x[4])

# Фильтруем аплинки, чтобы исключить их из таблицы

    # (коммутатор, интерфейс), на которых виден MAC из VLAN 2
    uplinks = {(row[0], row[4]) for row in sorted_table if row[2] == UPLINK_VLAN}

    # убираем все строки, относящиеся к этим интерфейсам
    sorted_table = [row for row in sorted_table if (row[0], row[4]) not in uplinks]

# Конец фильтрации UPLINK

    target = normalize_mac(mac_address)

    sorted_result = [
        row for row in sorted_table
        if normalize_mac(row[1]).endswith(target)
    ]

    print(f"{Fore.GREEN}Результат поиска City17 Cisco:{Style.RESET_ALL}")
    print(tabulate.tabulate(sorted_result, headers=headers, tablefmt="fancy_grid"))

    ############ City17 H3C
    table = []
    with open("ip_list_City17_H3C.txt", "r") as f:
        ip_list = f.read().splitlines()

    pbar = tqdm(total=len(ip_list), desc="🔗 Подключение к коммутаторам")

    threads = []
    for switch_ip in ip_list:
        t = Thread(target=connect_to_switch_with_mac_H3C, args=(switch_ip, username, password, table, pbar))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    pbar.close()

    sorted_table = sorted(table, key=lambda x: x[4])

# Фильтруем аплинки, чтобы исключить их из таблицы

    # (коммутатор, интерфейс), на которых виден MAC из VLAN 2
    uplinks = {(row[0], row[4]) for row in sorted_table if row[2] == UPLINK_VLAN}

    # убираем все строки, относящиеся к этим интерфейсам
    sorted_table = [row for row in sorted_table if (row[0], row[4]) not in uplinks]

# Конец фильтрации UPLINK

    target = normalize_mac(mac_address)

    sorted_result = [
        row for row in sorted_table
        if normalize_mac(row[1]).endswith(target)
    ]

    print(f"{Fore.GREEN}Результат поиска City17 H3C:{Style.RESET_ALL}")
    print(tabulate.tabulate(sorted_result, headers=headers, tablefmt="fancy_grid"))

    ############ City18 DLINK
    table = []
    with open("ip_list_City18_DLINK.txt", "r") as f:
        ip_list = f.read().splitlines()

    pbar = tqdm(total=len(ip_list), desc="🔗 Подключение к коммутаторам")

    threads = []
    for switch_ip in ip_list:
        t = Thread(target=connect_to_switch_with_mac_DLINK, args=(switch_ip, username, password, table, pbar))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    pbar.close()

    sorted_table = sorted(table, key=lambda x: x[4])

# Фильтруем аплинки, чтобы исключить их из таблицы

    # (коммутатор, интерфейс), на которых виден MAC из VLAN 2
    uplinks = {(row[0], row[4]) for row in sorted_table if row[2] == UPLINK_VLAN}

    # убираем все строки, относящиеся к этим интерфейсам
    sorted_table = [row for row in sorted_table if (row[0], row[4]) not in uplinks]

# Конец фильтрации UPLINK

    target = normalize_mac(mac_address)

    sorted_result = [
        row for row in sorted_table
        if normalize_mac(row[1]).endswith(target)
    ]

    print(f"{Fore.GREEN}Результат поиска на коммутаторах D-Link City18:{Style.RESET_ALL}")
    print(tabulate.tabulate(sorted_result, headers=headers, tablefmt="fancy_grid"))


    ############ City18 Cisco
    table = []
    with open("ip_list_City18_cisco.txt", "r") as f:
        ip_list = f.read().splitlines()

    pbar = tqdm(total=len(ip_list), desc="🔗 Подключение к коммутаторам")

    threads = []
    for switch_ip in ip_list:
        t = Thread(target=connect_to_switch_with_mac_cisco, args=(switch_ip, username, password, table, pbar))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    pbar.close()

    sorted_table = sorted(table, key=lambda x: x[4])

# Фильтруем аплинки, чтобы исключить их из таблицы

    # (коммутатор, интерфейс), на которых виден MAC из VLAN 2
    uplinks = {(row[0], row[4]) for row in sorted_table if row[2] == UPLINK_VLAN}

    # убираем все строки, относящиеся к этим интерфейсам
    sorted_table = [row for row in sorted_table if (row[0], row[4]) not in uplinks]

# Конец фильтрации UPLINK

    target = normalize_mac(mac_address)

    sorted_result = [
        row for row in sorted_table
        if normalize_mac(row[1]).endswith(target)
    ]

    print(f"{Fore.GREEN}Результат поиска City18 Cisco:{Style.RESET_ALL}")
    print(tabulate.tabulate(sorted_result, headers=headers, tablefmt="fancy_grid"))

    ############ City18 H3C
    table = []
    with open("ip_list_City18_H3C.txt", "r") as f:
        ip_list = f.read().splitlines()

    pbar = tqdm(total=len(ip_list), desc="🔗 Подключение к коммутаторам")

    threads = []
    for switch_ip in ip_list:
        t = Thread(target=connect_to_switch_with_mac_H3C, args=(switch_ip, username, password, table, pbar))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    pbar.close()

    sorted_table = sorted(table, key=lambda x: x[4])

# Фильтруем аплинки, чтобы исключить их из таблицы

    # (коммутатор, интерфейс), на которых виден MAC из VLAN 2
    uplinks = {(row[0], row[4]) for row in sorted_table if row[2] == UPLINK_VLAN}

    # убираем все строки, относящиеся к этим интерфейсам
    sorted_table = [row for row in sorted_table if (row[0], row[4]) not in uplinks]

# Конец фильтрации UPLINK

    target = normalize_mac(mac_address)

    sorted_result = [
        row for row in sorted_table
        if normalize_mac(row[1]).endswith(target)
    ]

    print(f"{Fore.GREEN}Результат поиска City18 H3C:{Style.RESET_ALL}")
    print(tabulate.tabulate(sorted_result, headers=headers, tablefmt="fancy_grid"))

    ############ City19 Cisco
    table = []
    with open("ip_list_City19_cisco.txt", "r") as f:
        ip_list = f.read().splitlines()

    pbar = tqdm(total=len(ip_list), desc="🔗 Подключение к коммутаторам")

    threads = []
    for switch_ip in ip_list:
        t = Thread(target=connect_to_switch_with_mac_cisco, args=(switch_ip, username, password, table, pbar))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    pbar.close()

    sorted_table = sorted(table, key=lambda x: x[4])

# Фильтруем аплинки, чтобы исключить их из таблицы

    # (коммутатор, интерфейс), на которых виден MAC из VLAN 2
    uplinks = {(row[0], row[4]) for row in sorted_table if row[2] == UPLINK_VLAN}

    # убираем все строки, относящиеся к этим интерфейсам
    sorted_table = [row for row in sorted_table if (row[0], row[4]) not in uplinks]

# Конец фильтрации UPLINK

    target = normalize_mac(mac_address)

    sorted_result = [
        row for row in sorted_table
        if normalize_mac(row[1]).endswith(target)
    ]

    print(f"{Fore.GREEN}Результат поиска City19 Cisco:{Style.RESET_ALL}")
    print(tabulate.tabulate(sorted_result, headers=headers, tablefmt="fancy_grid"))

    ############ City19 H3C
    table = []
    with open("ip_list_City19_H3C.txt", "r") as f:
        ip_list = f.read().splitlines()

    pbar = tqdm(total=len(ip_list), desc="🔗 Подключение к коммутаторам")

    threads = []
    for switch_ip in ip_list:
        t = Thread(target=connect_to_switch_with_mac_H3C, args=(switch_ip, username, password, table, pbar))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    pbar.close()

    sorted_table = sorted(table, key=lambda x: x[4])

# Фильтруем аплинки, чтобы исключить их из таблицы

    # (коммутатор, интерфейс), на которых виден MAC из VLAN 2
    uplinks = {(row[0], row[4]) for row in sorted_table if row[2] == UPLINK_VLAN}

    # убираем все строки, относящиеся к этим интерфейсам
    sorted_table = [row for row in sorted_table if (row[0], row[4]) not in uplinks]

# Конец фильтрации UPLINK

    target = normalize_mac(mac_address)

    sorted_result = [
        row for row in sorted_table
        if normalize_mac(row[1]).endswith(target)
    ]

    print(f"{Fore.GREEN}Результат поиска City19 H3C:{Style.RESET_ALL}")
    print(tabulate.tabulate(sorted_result, headers=headers, tablefmt="fancy_grid"))


def main():
    print(f"{Fore.CYAN}MAC address Tool{Style.RESET_ALL}")
    
    main_menu = f'Выберете действие:\n' \
                f'\t{Style.RESET_ALL}1. Найти неуправляемые {Style.BRIGHT + Fore.YELLOW}коммутаторы в City17 (Cisco, H3C)\n' \
                f'\t{Style.RESET_ALL}11. Найти порт коммутатора по {Style.BRIGHT + Fore.YELLOW}MAC в City17\n' \
                f'\t \n' \
                f'\t{Style.RESET_ALL}2. Найти неуправляемые {Style.BRIGHT + Fore.YELLOW}коммутаторы в City18 (D-Link, Cisco, H3C)\n' \
                f'\t{Style.RESET_ALL}21. Найти порт коммутатора по {Style.BRIGHT + Fore.YELLOW}MAC в City18\n' \
                f'\t \n' \
                f'\t{Style.RESET_ALL}3. Найти неуправляемые {Style.BRIGHT + Fore.YELLOW}коммутаторы в City19 (Cisco, H3C)\n' \
                f'\t{Style.RESET_ALL}31. Найти порт коммутатора по {Style.BRIGHT + Fore.YELLOW}MAC в City19\n' \
                f'\t \n' \
                f'\t{Style.RESET_ALL}99. Найти порт коммутатора по {Style.BRIGHT + Fore.YELLOW}всем филиалам\n' \
                f'\t \n' \
                f'\t{Style.RESET_ALL}100. Найти IP адрес по {Style.BRIGHT + Fore.YELLOW}MAC в City17\n' \
                f'\t{Style.RESET_ALL}101. Найти IP адрес по {Style.BRIGHT + Fore.YELLOW}MAC в City18\n' \
                f'\t{Style.RESET_ALL}102. Найти IP адрес по {Style.BRIGHT + Fore.YELLOW}MAC в City19\n' 
    while True:
        
        print(Style.RESET_ALL + main_menu)
        choice = input(f'{Style.RESET_ALL}Ваш выбор: ')

        if choice == '1':
            print(Fore.YELLOW + Style.BRIGHT + '\nПоиск неуправляемых коммутаторов в City17 (Cisco, H3C)')
            search_double_ports_City17_cisco()
            search_double_ports_City17_H3C()

        elif choice == '11':
            print(Fore.YELLOW + Style.BRIGHT + '\nПоиск порта по mac-адресу на коммутаторах в City17')
            search_mac_City17()

        elif choice == '2':
            print(Fore.YELLOW + Style.BRIGHT + '\nПоиск неуправляемых коммутаторов в City18 (D-Link, Cisco, H3C)')
            search_double_ports_City18_DLINK()
            search_double_ports_City18_cisco()

        elif choice == '21':
            print(Fore.YELLOW + Style.BRIGHT + '\nПоиск порта по mac-адресу на коммутаторах в City18')
            search_mac_City18()

        elif choice == '3':
            print(Fore.YELLOW + Style.BRIGHT + '\nПоиск неуправляемых коммутаторов в City19 (Cisco, H3C)')
            search_double_ports_City19_cisco()
            search_double_ports_City19_H3C()

        elif choice == '31':
            print(Fore.YELLOW + Style.BRIGHT + '\nПоиск порта по mac-адресу на коммутаторах в City19')
            search_mac_City19()

        elif choice == '99':
            print(Fore.YELLOW + Style.BRIGHT + '\nПоиск порта по mac-адресу на коммутаторах всех филиалов')
            search_mac_full()

        elif choice == '100':
            print(Fore.YELLOW + Style.BRIGHT + '\nПоиск IP адреса по mac-адресу в City17')
            search_ip_City17()

        elif choice == '101':
            print(Fore.YELLOW + Style.BRIGHT + '\nПоиск IP адреса по mac-адресу в City18')
            search_ip_City18()

        elif choice == '102':
            print(Fore.YELLOW + Style.BRIGHT + '\nПоиск IP адреса по mac-адресу в City19')
            search_ip_City19()

        else:
            pass
        input(f'{Style.RESET_ALL}Для продолжения нажмите {Style.BRIGHT + Fore.YELLOW}ENTER ')
        
if __name__ == "__main__":
    main()
