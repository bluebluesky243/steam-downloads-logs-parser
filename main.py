import datetime
import time
import requests
import winreg
import sys
import re

printed_rate_counter = 0

def exit_func(printed_rate_counter):
    if printed_rate_counter > 4:
        time.sleep(3)
        sys.exit()

def get_steam_path():
    paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam", "InstallPath"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam", "InstallPath"),
        (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam", "SteamPath"),
        (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam", "InstallPath"),
    ]

    for hkey, reg_path, value in paths:
        try:
            key = winreg.OpenKey(hkey, reg_path)
            path, type = winreg.QueryValueEx(key, value)
            winreg.CloseKey(key)
            if path:
                return path
        except FileNotFoundError:
            continue
    return None

logs_file_path = fr'{get_steam_path()}\logs\content_log.txt'
workshop_update = False

def get_game_name(app_id):
    try:
        url = f'https://store.steampowered.com/api/appdetails?appids={app_id}'
        game_name = requests.get(url).json()[str(app_id)]['data']['name']
        return game_name
    except:
        return f'с AppId:{app_id}'


with open(logs_file_path) as file:
    while True:
        log = file.readline().strip()
        now = str(datetime.datetime.now().replace(microsecond=0))
        if not log:
            continue
        rate_pos = 45
        if now in log and 'Current download rate:' in log:
            print(now + ' ' + 'Скорость загрузки - ' + log[rate_pos:])
            printed_rate_counter += 1

        exit_func(printed_rate_counter)

        if 'Workshop update changed : Running Update' in log:
            workshop_update = True
        if 'Workshop update changed : None' in log:
            workshop_update = False


        game_id_pos = 28

        if now in log and re.search(r'update started : download 0', log):
            if workshop_update:
                continue
            match = re.match(r'\d+', log[game_id_pos:])
            app_id = match.group()
            game_name = get_game_name(app_id)
            print(now + ' ' + 'Начало загрузки игры ' + game_name)

        if now in log and re.search(r'update started', log) \
        and not re.search('update started : download 0', log):
            match = re.match(r'\d+',log[game_id_pos:])
            app_id = match.group()
            game_name = get_game_name(app_id)
            print(now + ' ' + 'Продолжение загрузки игры ' + game_name)

        if now in log and re.search(r'update canceled : Disabled', log):
            match = re.match(r'\d+', log[game_id_pos:])
            app_id = match.group()
            game_name = get_game_name(app_id)
            print(now + ' ' + 'Загрузка игры ' + game_name + ' на паузе')

        if now in log and re.search(r'update canceled : Uninstall \(Canceled\)', log):
            match = re.match(r'\d+', log[game_id_pos:])
            app_id = match.group()
            game_name = get_game_name(app_id)
            print(now + ' ' + 'Загрузка игры ' + game_name + ' отменена')

        if now in log and re.search(r'state changed : Update Required,Fully Installed,Files Missing,Uninstalling', log):
            match = re.match(r'\d+', log[game_id_pos:])
            app_id = match.group()
            game_name = get_game_name(app_id)
            print(now + ' ' + 'Игра ' + game_name + ' удалена')

        if now in log and re.search(r'scheduler finished : removed from schedule \(result No Error, state 0xc\)', log):
            match = re.match(r'\d+', log[game_id_pos:])
            app_id = match.group()
            game_name = get_game_name(app_id)
            print(now + ' ' + 'Загрузка игры ' + game_name + ' завершена')



