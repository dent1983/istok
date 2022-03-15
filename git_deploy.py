#!/usr/bin/python3.8


""" Скрипт автоматической установки ВПО (BMC, Uboot) на Сервисный маршрутизатор (SR-BE)
BMC:
подключение - STM/bin/STM32_Programmer_CLI -c port=SW
очистка flash- STM/bin/STM32_Programmer_CLI -c port=SWD -e all
загрузка ВПО- STM/bin/STM32_Programmer_CLI -c port=SWD -w fw/RU.07622667.00007-01.bin 0x08000000
запуск- STM/bin/STM32_Programmer_CLI -c port=SWD -s 0x08000000
Uboot:
считать и записать в файл- flashrom -p ft2232_spi:type=arm-usb-tiny-h,port=a,divisor=8 -r file1.rom
запись- flashrom -p ft2232_spi:type=arm-usb-tiny-h,port=a,divisor=8 -w file2.rom (RU.07622667.00006-01.rom.bin)
очистить- flashrom -p ft2232_spi:type=arm-usb-tiny-h,port=a,divisor=8 -E

при multiple, указать -с 'имя чипа'
"""

import os, re, time, logging, keyboard
from datetime import datetime, timedelta

# PROGRAMMATORS NAMEs
arm = 'ARM-USB-TINY-H'
stm = 'STMicroelectronics ST-LINK/V2'

# BMC messages
error_bmc = 'Error: No STM32 target found!'
success_erase = 'Mass erase successfully achieved'
error_download = 'File does not exist'
success_download = 'File download complete'
error_start = 'Warning: The core is locked up'
success_start = 'Application is running'
# Uboot messages
error_uboot = 'No EEPROM/flash device found'
file_uboot = 'Error: opening file'
read_uboot = 'Reading old flash chip contents... done'
erase_uboot = 'Erasing and writing flash chip... Erase/write done'
verified_uboot = 'Verifying flash... VERIFIED'
copy_uboot = 'Warning: Chip content is identical to the requested image'
mult_uboot = 'Multiple flash chip definitions match the detected chip(s)'
# DATE
current_datetime = datetime.now()
current_time = current_datetime.time()
date_log = time.strftime("%Y%m%d-%H%M%S")

# COLORS LOG
class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKCYAN = '\033[96m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'

def logs(mes):
	logging.basicConfig(filename=(f'log/log-{date_log}.log'), format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
	logging.warning(mes)

def master():
	os.system ('clear')
	logs("------------------------------- START NEW DEVICE LOG ----------------------------------------------------")
	logs(current_datetime)
	logs("---------------------------------------------------------------------------------------------------------")
	print(bcolors.HEADER + "----------------Начало работы установщика ВПО (BMC,Uboot) SR-BE------------------------")
	print()
	print("Дата - " + bcolors.ENDC, current_datetime)
	print(bcolors.OKCYAN + "---------------------------------------------------------------------------------------" + bcolors.ENDC)
	print(bcolors.WARNING + "Step 1 - Подключение к контроллеру BMC" + bcolors.ENDC)
	print()

	cmd_usb = os.popen('lsusb').read()
	if stm not in cmd_usb:
		logs(cmd_usb)
		print(bcolors.FAIL + "ОШИБКА !!!! ПРОГРАММАТОР ST-LINK/V2 НЕ ПОДКЛЮЧЕН К КОМПЬЮТЕРУ (ПОРТ USB) !!!")
		print("1. ОТКЛЮЧИТЕ ПИТАНИЕ ОТ УСТРОЙСТВА. ПОДКЛЮЧИТЕ ШЛЕЙФ ОТ ПРОГРАММАТОРА !!! ВКЛЮЧИТЕ УСТРОЙСТВО !!!")
		print("2. ПРИ ПОВТОРНОМ ПОЯВЛЕНИИ ОШИБКИ - ЗАМЕНИТЕ ШЛЕЙФ, КАБЕЛЬ USB ИЛИ ПРОГРАММАТОР !!!")
		print()
		print("  ПОВТОРНАЯ ПРОВЕРКА КАЖДЫЕ 5 СЕКУНД (закрыть программу - Ctrl+C) ..." + bcolors.ENDC)
		print()
		while stm not in cmd_usb:
			time.sleep(5)
			cmd_usb = os.popen('lsusb').read()
			if stm in cmd_usb:
				print(bcolors.OKGREEN + "Программатор ST-LINK подключен" + bcolors.ENDC)
				break
			else:
				pass
	else:
		logs(cmd_usb)
		print(bcolors.OKGREEN + "Программатор ST-LINK подключен" + bcolors.ENDC)
		print()

	if arm not in cmd_usb:
		logs(cmd_usb)
		print(bcolors.FAIL + "ОШИБКА !!!! ПРОГРАММАТОР ARM-USB НЕ ПОДКЛЮЧЕН К КОМПЬЮТЕРУ (ПОРТ USB) !!!")
		print("1. ОТКЛЮЧИТЕ ПИТАНИЕ ОТ УСТРОЙСТВА. ПОДКЛЮЧИТЕ ШЛЕЙФ ОТ ПРОГРАММАТОРА !!! ВКЛЮЧИТЕ УСТРОЙСТВО !!!")
		print("2. ПРИ ПОВТОРНОМ ПОЯВЛЕНИИ ОШИБКИ - ЗАМЕНИТЕ ШЛЕЙФ, КАБЕЛЬ USB ИЛИ ПРОГРАММАТОР !!!")
		print()
		print("  ПОВТОРНАЯ ПРОВЕРКА КАЖДЫЕ 5 СЕКУНД (закрыть программу - Ctrl+C) ..." + bcolors.ENDC)
		print()
		while arm not in cmd_usb:
			time.sleep(5)
			cmd_usb = os.popen('lsusb').read()
			if arm in cmd_usb:
				logs(cmd_usb)
				print(bcolors.OKGREEN + "Программатор ARM-USB подключен" + bcolors.ENDC)
				break
			else:
				logs(cmd_usb)
				pass
	else:
		logs(cmd_usb)
		print(bcolors.OKGREEN + "Программатор ARM-USB подключен" + bcolors.ENDC)
		print()

	cmd_connect = os.popen('STM/bin/STM32_Programmer_CLI -c port=SWD').read()
	if error_bmc in cmd_connect:
		logs(cmd_connect)
		print(bcolors.FAIL + "ОШИБКА !!!! ПОДКЛЮЧЕНИЕ К КОНТРОЛЛЕРУ BMC ОТСУТСТВЕТ !!!")
		print("1. ПРОВЕРЬТЕ ПОДКЛЮЧЕНИЕ ПРОГРАММАТОРА ST-LINK К КОНТРОЛЛЕРУ BMC !!! ")
		print("2. ПРОВЕРЬТЕ НАЛИЧИЕ ПИТАНИЯ НА УСТРОЙСТВЕ !!!")
		print()
		print(" ПОВТОРНАЯ ПРОВЕРКА КАЖДЫЕ 5 СЕКУНД (закрыть программу - Ctrl+C) ..." + bcolors.ENDC)
		print()
		while error_bmc in cmd_connect:
			time.sleep(5)
			cmd_connect = os.popen('STM/bin/STM32_Programmer_CLI -c port=SWD').read()
			if error_bmc in cmd_connect:
				logs(cmd_connect)
				pass
			else:
				logs(cmd_connect)
				print(bcolors.OKGREEN + "Контроллер BMC подключен." + bcolors.ENDC)
				print()
				break
	else:
		logs(cmd_connect)
		print(bcolors.OKGREEN + "Контроллер BMC подключен." + bcolors.ENDC)
		print()

	time.sleep(1)

	print(bcolors.OKCYAN + "---------------------------------------------------------------------------------------" + bcolors.ENDC)
	print(bcolors.WARNING + "Step 2 - Очистка BMC (Mass erase)" + bcolors.ENDC)
	print()

	cmd_erase = os.popen('STM/bin/STM32_Programmer_CLI -c port=SWD -e all').read()
	if success_erase in cmd_erase:
		logs(cmd_erase)
		print(bcolors.OKGREEN + "Flash память контроллера BMC очищена (Mass erase successfully achieved)." + bcolors.ENDC)
		print()
	else:
		logs(cmd_erase)
		print(bcolors.OKCYAN + "Внимание ! Flash память контроллера BMC не очищена. Повторная попытка позже - при загрузке ВПО BMC." + bcolors.ENDC)
		print()

	time.sleep(1)

	print(bcolors.OKCYAN + "---------------------------------------------------------------------------------------" + bcolors.ENDC)
	print(bcolors.WARNING + "Step 3 - Загрузка ВПО (BMC)" + bcolors.ENDC)
	print()

	cmd_download = os.popen('STM/bin/STM32_Programmer_CLI -c port=SWD -w fw/RU.07622667.00007-01.bin 0x08000000').read()
	if success_download in cmd_download:
		logs(cmd_download)
		print (bcolors.OKGREEN + "Загрузка ВПО (BMC) завершена" + bcolors.ENDC)
	else:
		logs(cmd_download)
		print(bcolors.FAIL + "ОШИБКА !!!! Прошивка контроллера BMC не найдена или повреждена !!!")
		print("1. ПРОВЕРЬТЕ НАЛИЧИЕ ПРОШИВКИ В ПАПКЕ НА РАБОЧЕМ СТОЛЕ - STM/fw/RU.07622667.00007-01.bin !!! ")
		print("2. ПРИ ПОВТОРНОМ ПОЯВЛЕНИИ ОШИБКИ - СВЯЖИТЕСЬ С РАЗРАБОТЧИКОМ УСТРОЙСТВА !!!")
		print()
		print(" ПОВТОРНАЯ ПРОВЕРКА И ПОПЫТКА ЗАГРУЗКИ ВПО (BMC) КАЖДЫЕ 5 СЕКУНД (закрыть программу - Ctrl+C) ..." + bcolors.ENDC)
		print()
		while success_download not in cmd_download:
			time.sleep(5)
			cmd_download = os.popen('STM/bin/STM32_Programmer_CLI -c port=SWD -w fw/RU.07622667.00007-01.bin 0x08000000').read()
			if error_download in cmd_download:
				logs(cmd_download)
				pass
			elif success_download in cmd_download:
				logs(cmd_download)
				print(bcolors.OKGREEN + "Загрузка ВПО (BMC) завершена (File download complet)." + bcolors.ENDC)
				break
			else:
				logs(cmd_download)
				continue

	time.sleep(1)

	print(bcolors.OKCYAN + "---------------------------------------------------------------------------------------" + bcolors.ENDC)
	print(bcolors.WARNING + "Step 4 - Старт ВПО (BMC)" + bcolors.ENDC)
	print()

	cmd_start = os.popen('STM/bin/STM32_Programmer_CLI -c port=SWD -s 0x08000000').read()
	if success_start in cmd_start:
		logs(cmd_start)
		print(bcolors.OKGREEN + "ВПО (BMC) успешно запущено." + bcolors.ENDC)
		print()
	else:
		logs(cmd_start)
		print(bcolors.FAIL + "ОШИБКА !!!! ВПО (BMC) не может произвести запуск !!!")
		print("1. ПРОВЕРЬТЕ НАЛИЧИЕ ПРОШИВКИ В ПАПКЕ НА РАБОЧЕМ СТОЛЕ - STM/fw/RU.07622667.00007-01.bin !!! ")
		print("2. ЗАКРОЙТЕ (Ctrl+C) И ЗАПКУСТИТЕ ЗАНОВО ПРОГРАММУ (run.py)")
		print(" ПРИ ПОВТОРНОМ ПОЯВЛЕНИИ ОШИБКИ - СВЯЖИТЕСЬ С РАЗРАБОТЧИКОМ УСТРОЙСТВА !!!")
		print()
		print("ВНИМАНИЕ !!! ПРОГРАММА ЗАВЕРШЕНА С ОШИБКОЙ !!!! ДАЛЬНЕЙШАЯ НАСТРОЙКА ИЗДЕЛИЯ НЕВОЗМОЖНА !!!" + bcolors.ENDC)
		time.sleep(20)
		exit()

	print(bcolors.OKCYAN + "---------------------------------------------------------------------------------------" + bcolors.ENDC)
	print(bcolors.WARNING + "Step 5 - Установка ВПО (Uboot)" + bcolors.ENDC)
	print()

	time.sleep(2)

	cmd_uboot = os.popen('flashrom -p ft2232_spi:type=arm-usb-tiny-h,port=a,divisor=8 -w fw/RU.07622667.00006-01.rom.bin').read()
	if error_uboot in cmd_uboot:
		logs(cmd_uboot)
		print(bcolors.FAIL + "ОШИБКА !!!! ПРОГРАММАТОР ARM-USB НЕ ПОДКЛЮЧЕН К ПРОШИВАЕМОМУ УСТРОЙСТВУ !!!")
		print("1. ОТКЛЮЧИТЕ ПИТАНИЕ ОТ УСТРОЙСТВА. ПОДКЛЮЧИТЕ ШЛЕЙФ ОТ ПРОГРАММАТОРА !!! ВКЛЮЧИТЕ УСТРОЙСТВО !!!")
		print("2. ПРИ ПОВТОРНОМ ПОЯВЛЕНИИ ОШИБКИ - ЗАМЕНИТЕ ШЛЕЙФ, КАБЕЛЬ USB ИЛИ ПРОГРАММАТОР !!!")
		print()
		print("  ПОВТОРНАЯ ПРОВЕРКА КАЖДЫЕ 5 СЕКУНД (закрыть программу - Ctrl+C) ..." + bcolors.ENDC)
		print()
		while error_uboot in cmd_uboot:
			time.sleep(5)
			cmd_uboot = os.popen('flashrom -p ft2232_spi:type=arm-usb-tiny-h,port=a,divisor=8 -w fw/RU.07622667.00006-01.rom.bin').read()
			if error_uboot not in cmd_uboot:
				logs(cmd_uboot)
				break
			else:
				logs(cmd_uboot)
				pass

	if file_uboot in cmd_uboot:
		logs(cmd_uboot)
		print(bcolors.FAIL + "ОШИБКА !!!! Прошивка контроллера Uboot не найдена или повреждена !!!")
		print("1. ПРОВЕРЬТЕ НАЛИЧИЕ ПРОШИВКИ В ПАПКЕ НА РАБОЧЕМ СТОЛЕ - STM/fw/RU.07622667.00006-01.rom.bin !!! ")
		print("2. ПРИ ПОВТОРНОМ ПОЯВЛЕНИИ ОШИБКИ - СВЯЖИТЕСЬ С РАЗРАБОТЧИКОМ УСТРОЙСТВА !!!")
		print()
		print(" ПОВТОРНАЯ ПРОВЕРКА И ПОПЫТКА УТСТАНОВКИ ВПО (Uboot) КАЖДЫЕ 5 СЕКУНД (закрыть программу - Ctrl+C) ..." + bcolors.ENDC)
		print()
		while file_uboot in cmd_uboot:
			time.sleep(5)
			cmd_uboot = os.popen('flashrom -p ft2232_spi:type=arm-usb-tiny-h,port=a,divisor=8 -w fw/RU.07622667.00006-01.rom.bin').read()
			if file_uboot in cmd_uboot:
				logs(cmd_uboot)
				pass
			else:
				logs(cmd_uboot)
				break

# принудительное обновление ВПО Uboot
	if mult_uboot in cmd_uboot:
		print(bcolors.WARNING + "ВНИМАНИЕ !!! В Uboot уже установлено ВПО !!!" + bcolors.ENDC)
		print()
		print(cmd_uboot)
		logs(cmd_uboot)
		print(bcolors.WARNING + "Принудительное обновление ВПО Uboot !!!" + bcolors.ENDC)
		print()
		cmd_uboot = os.popen('flashrom -p ft2232_spi:type=arm-usb-tiny-h,port=a,divisor=8 -w fw/RU.07622667.00006-01.rom.bin -c S25FL128S......0').read()
		print(cmd_uboot)
		print()
		logs(cmd_uboot)
	if verified_uboot in cmd_uboot:
		logs(cmd_uboot)
		print(bcolors.OKGREEN + "Загрузка ВПО (Uboot) завершена (VERIFIED)." + bcolors.ENDC)
		print()
	elif copy_uboot in cmd_uboot:
		logs(cmd_uboot)
		print(bcolors.OKGREEN + "Загрузка ВПО (Uboot) завершена (Actual release)." + bcolors.ENDC)
		print()
	else:
		logs(cmd_uboot)
		logs("BUG ERROR !!! SOFTWARE IS STOP!!!")
		print(bcolors.FAIL + "ОШИБКА !!! ВПО (Uboot) НЕ ЗАГРУЖЕНО !!!" + bcolors.ENDC)
		print(bcolors.FAIL + "ВНИМАНИЕ !!! ПРОГРАММА ЗАВЕРШЕНА С ОШИБКОЙ !!!! ДАЛЬНЕЙШАЯ НАСТРОЙКА ИЗДЕЛИЯ НЕВОЗМОЖНА !!!" + bcolors.ENDC)
		print(bcolors.FAIL + "СВЯЖИТЕСЬ С РАЗРАБОТЧИКОМ ИЗДЕЛИЯ !!!" + bcolors.ENDC)
		print()
		time.sleep(20)
		exit()

	print(bcolors.HEADER + "=========== Завершение работы установки ВПО (BMC, Uboot) на SR-BE =========" + bcolors.ENDC)
	print()
	logs("-------------------------------END DEVICE ---------------------------------------")
	logs("\n")
	print(bcolors.WARNING + "Для повторного запуска установки ВПО (BMC, Uboot) нажмите ENTER!" + bcolors.ENDC)
	print(bcolors.WARNING + "Для выхода из программы нажмите Ctrl+C !" + bcolors.ENDC)
	print()

while True:
	master()
	keyboard.wait("Enter")
