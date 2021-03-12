import csv
import datetime
import requests
from lxml import html
from datetime import datetime

URL = 'https://www.ab.bluecross.ca/news/covid-19-immunization-program-information.php'
XPATH_TO_PHARMACIES = "/html/body/main/section/div[2]/div/div/div/div"
CITY_FILTER = 'EDMONTON'

page = requests.get(URL)
tree = html.fromstring(page.content)
datetime_as_str = datetime.now().strftime('%Y%m%d-%H%M%S') # Being lazy and not dealing with timezones

pharmacies = tree.xpath(XPATH_TO_PHARMACIES)

# Given the childern of the HTML element for a pharmacy return a row for the CSV 
# i.e. a dictionary where the keys are the column names
def get_row(elements):
    row = {}
    
    row['name'] = elements[0].text

    # There are two address lines, the second may be empty
    address_line_1 = elements[1].text.lstrip() # remove a leading space
    address_line_2 = elements[2].text 
    row['address'] = address_line_1 if address_line_2==' ' else address_line_1 + ',' + address_line_2

    row['city'] = elements[3].text
    
    # Hardcoded element in the HTML before the date (assert on its presence)
    assert elements[4].text == 'Next date available to book an appointment:' 
    row['date'] = elements[5].text

    row['phone'] = elements[6].getchildren()[0].text

    row['link'] = elements[7].getchildren()[0].get('href')

    return row

# Build a list of all the pharmacies
rows = []
for pharmacy in pharmacies:
    elements = pharmacy.getchildren()
    row = get_row(elements)
    rows.append(row)

# Output the data as a CSV (filtering for the desired city)
col_names = rows[0].keys()
output_file_name = 'pharmacies-%s-%s.csv' % (CITY_FILTER.lower(), datetime_as_str)
with open(output_file_name, 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, col_names)
    dict_writer.writeheader()
    dict_writer.writerows( [r for r in rows if r['city']==CITY_FILTER] )
