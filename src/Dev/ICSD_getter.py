import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.select import Select

download = 0
begin_search_download = 0
t_end = 0
redo_counter = 0
download_row = 0
rows_in_table = 0
failed_file = open("failed_structure_downloads_binaries.txt", mode="a", encoding="utf-8")
fractional_file = open("fractional_binaries.txt", mode="a", encoding="utf-8")

s = Service("chromedriver.exe")
driver = webdriver.Chrome(service = s)
#driver.get('https://icsd.fiz-karlsruhe.de/search/basic.xhtml')
#driver.get('https://icsd.products.fiz-karlsruhe.de/')
driver.get('https://icsd-fiz-karlsruhe-de.libproxy.mit.edu/search/basic.xhtml')
#AVV9002248
#n2W9u5

time.sleep(30)

number_of_elements = driver.find_element(by=By.XPATH, value='//*[@id="content_form:uiChemistrySearchElCount:input:input"]')
number_of_elements.click()
number_of_elements.send_keys("2")

Structure_type_menu = driver.find_element(by=By.LINK_TEXT, value="Structure Type")
Structure_type_menu.click()

time.sleep(2)

Structure_type_searchbar = driver.find_element(by=By.XPATH, value='//*[@id="content_form:uiPreDefinedStructureTypes:input_input"]')
Structure_type_searchbar.click()

try:
	structure_type_file = open("./structure_type_list_checkpoint.txt", mode="r", encoding="utf-8")
	structure_types = structure_type_file.readlines()
	Structure_type_searchbar.send_keys(structure_types[0])

	time.sleep(2)

	try:
		Run_query = driver.find_element(by=By.XPATH, value='//*[@id="content_form:btnRunQuery"]')
		Run_query.click()
	except:
		pass

	time.sleep(2)

	sel = Select(driver.find_element(by=By.XPATH, value='//*[@id="display_form:listViewTable:j_id12"]'))
	sel.select_by_visible_text("50")

	time.sleep(2)


	t_end = time.time() + 10
	while download == 0 and t_end > time.time():
		try:
			for row in range(50):
				formula_column = driver.find_element(by=By.XPATH, value='//*[@id="display_form:listViewTable_data"]/tr[' + str(row + 1) + ']/td[3]')
				print(formula_column.text + str("." not in formula_column.text))
				if "." not in formula_column.text and download == 0:
					download = 1
					download_row = row
		except:
			pass


	if download == 0:
		Download_cif = driver.find_element(by=By.XPATH, value='//*[@id="display_form:listViewTable:0:btnEntryDownloadCif"]')
		Download_cif.click()
		fractional_file.write(structure_types[0])

	else:
		Download_cif = driver.find_element(by=By.XPATH, value='//*[@id="display_form:listViewTable:' + str(download_row) + ':btnEntryDownloadCif"]')
		Download_cif.click()
	download = 0

	time.sleep(2)

	backtoquery = driver.find_element(by=By.XPATH, value='//*[@id="display_form:btnBackToQuery"]')
	backtoquery.click()

	time.sleep(2)

except:
	try:
		print(structure_types[0].encode("utf-8") + "\n")
	except:
		pass
	failed_file.write(structure_types[0])

for i in range(10030):
	try:
		download = 0
		begin_search_download = 0
		Structure_type_searchbar = driver.find_element(by=By.XPATH, value='//*[@id="content_form:uiPreDefinedStructureTypes:input_input"]')
		Structure_type_searchbar.click()
		Structure_type_searchbar.clear()
		Structure_type_searchbar.send_keys(structure_types[1+i-redo_counter])

		print("fail1")

		time.sleep(2)

		try:
			print("fail2")
			Run_query = driver.find_element(by=By.XPATH, value='//*[@id="content_form:btnRunQuery"]')
			Run_query.click()
			print("fail3")
		except:
			pass

		time.sleep(2)

		print("fail4")
		sel = Select(driver.find_element(by=By.XPATH, value='//*[@id="display_form:listViewTable:j_id12"]'))
		begin_search_download = 1
		sel.select_by_visible_text("50")

		print("fail5")

		time.sleep(2)

		t_end = time.time() + 10
		while download == 0 and t_end > time.time():
			try:
				for row in range(50):
					print("fail6")
					formula_column = driver.find_element(by=By.XPATH, value='//*[@id="display_form:listViewTable_data"]/tr[' + str(row + 1) + ']/td[3]')
					print(formula_column.text + str("." not in formula_column.text))
					if "." not in formula_column.text and download == 0:
						download = 1
						download_row = row
						print("fail7")
			except Exception as e:
				print(e)
				pass

		print("fail8")
		if download == 0:
			Download_cif = driver.find_element(by=By.XPATH, value='//*[@id="display_form:listViewTable:0:btnEntryDownloadCif"]')
			Download_cif.click()
			fractional_file.write(structure_types[1+i-redo_counter])
		else:
			try:
				print("fail11")
				Download_cif = driver.find_element(by=By.XPATH, value='//*[@id="display_form:listViewTable:' + str(download_row) + ':btnEntryDownloadCif"]')
				print("fail12")
				Download_cif.click()
			except:
				time.sleep(5)
				print("fail14")
				Download_cif = driver.find_element(by=By.XPATH, value='//*[@id="display_form:listViewTable:' + str(download_row) + ':btnEntryDownloadCif"]')
				print("fail15")
				Download_cif.click()

		print("fail13")

		time.sleep(2)

		print("fail9")
		backtoquery = driver.find_element(by=By.XPATH, value='//*[@id="display_form:btnBackToQuery"]')
		print("fail10")
		backtoquery.click()

	except Exception as e2:
		print("begin_search_download = " + str(begin_search_download))
		print("redo_counter = " + str(redo_counter))
		if begin_search_download == 0:
			try:
				print(structure_types[1+i-redo_counter].encode("utf-8") + "\n")
			except:
				pass
			failed_file.write(structure_types[1+i-redo_counter])
		else:
			print(e2)
			time.sleep(20)
			redo_counter = redo_counter + 1
			try:
				backtoquery = driver.find_element(by=By.XPATH, value='//*[@id="display_form:btnBackToQuery"]')
				backtoquery.click()
			except:
				pass


failed_file.close()