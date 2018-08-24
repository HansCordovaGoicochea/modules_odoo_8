from selenium import webdriver
from selenium.webdriver.common.keys import Keys

driver = webdriver.Firefox()
driver.get("http://www.google.com/")

#open tab
driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't')

# Load a page
# driver.get('http://stackoverflow.com/')
# Make the tests...
driver.execute_script('''window.open("http://bings.com","_blank");''')
# close the tab
driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 'w')
# driver.close()