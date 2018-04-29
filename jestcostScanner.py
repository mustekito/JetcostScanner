#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: https://github.com/mustekito

import sys
import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

import datetime

ACCESS_KEY = "INSERT_HERE_YOUR_FIXER.IO_KEY"

def journey_div_to_text(div1, div2):
	divs1 = div1.find_all("div")
	divs2 = div2.find_all("div")

	texto = divs1[0].text + u" " + divs1[1].text + u" -------> " + divs2[1].text + u" " + divs2[0].text
	return texto

def chamadaAPI(fromm, to, data_init, data_fin):
	profile = webdriver.FirefoxProfile()
	profile.set_preference("general.useragent.override", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/63.0.3239.84 Chrome/63.0.3239.84 Safari/537.36")
	# Deshabilitamos imagenes
	profile.set_preference('permissions.default.image', 2)
	profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')

	binary = FirefoxBinary('/usr/bin/firefox')
	driver = webdriver.Firefox(profile, firefox_binary=binary)
	driver.get("https://www.jetcost.com.co")

	delta = data_fin - data_init
	dias=delta.days

	r = requests.get("http://data.fixer.io/api/latest?access_key=" + ACCESS_KEY)
	json = r.json()
	cop2eur = json["rates"]["COP"]

	date2 = "%d-%02d-%02d" %(data_fin.year, data_fin.month, data_fin.day)
	for i in range (0, dias+1):
		new_date = data_init + datetime.timedelta(days=i)
		date1 = "%d-%02d-%02d" %(new_date.year, new_date.month, new_date.day)
		driver.get("https://www.jetcost.com.co/wait.php?roundtrip=false&from=" + fromm + "&to=" + to + "&date1=" + date1 + "&date2=" + date2 + "&adults=1&children=0&infants=0&class=0")

		WebDriverWait(driver, timeout=60).until(
 		 lambda x: x.find_element_by_class_name('plusminus__pre__title'))
		
		html = driver.page_source
		soup = BeautifulSoup(html, 'html.parser')
		departures = soup.find_all("div", {"class": "departure"})
		arrives = soup.find_all("div", {"class": "arrive"})
		prices = soup.find_all("span", {"class": "price"})

		#journey_div_to_text(departures[0], arrives[0])
		print("%s: %.2f €" %(new_date.strftime("%d/%m/%Y"), float(prices[0].text)/cop2eur ))
	driver.close()

if __name__ == "__main__":
	if len(sys.argv)==5:
		data_init = datetime.datetime.strptime(sys.argv[3], "%d/%m/%Y")
		data_fin = datetime.datetime.strptime(sys.argv[4], "%d/%m/%Y")
		chamadaAPI(sys.argv[1], sys.argv[2], data_init, data_fin)
	else:
		print("Error. Use: python jestcostScanner.py MAD BCN 01/08/2018 31/08/2018")
