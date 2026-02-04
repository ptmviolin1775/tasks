from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup
import csv
from os.path import exists
import os
import logging
import platform
import mysql.connector
import pytz
from datetime import datetime
import re
import string
from datetime import date

def breakApartAddress(address):
    address_line_array = {
        "AddressLine1":None,
        "AddressLine2":None,
        "AddressLine3":None,
        "AddressLine4":None,
        "AddressLine5":None,
        "AddressLine6":None
    }
    if('\n' in address):
        print("New Lines Found")
        lines = address.split("\n")
        for count,line in enumerate(lines):
            address_line_array['AddressLine' + str(count+1)] = line.strip()
        if(len(lines) > 5):
            print("More lines than address fields")
            exit()
    else:
        print("No Lines Found")
    
    return address_line_array

def getProfileInformation(html):
    persondictionary = {}
    soup = BeautifulSoup(html, 'html.parser')
    maindiv = soup.find('div',attrs={'id':'ctl01_TemplateBody_WebPartManager1_gwpciDirectoryResults_ciDirectoryResults__Body'})
    rowdivs = maindiv.find_all('div',attrs={'class':'ReadOnly PanelField Left'})
    for rowdiv in rowdivs:
        label = rowdiv.find('span',attrs={'class':'Label'}).text.strip()
        value = rowdiv.find('div',attrs={'class':'PanelFieldValue'}).get_text(separator="\n").strip()
        if(label == 'Address'):
            #This makes sure we only have one line break for when we split one line breaks up above.
            value = re.sub(r'\n\s*\n', '\n', value)
        persondictionary[label] = value
    print(persondictionary)
    address_array = breakApartAddress(persondictionary['Address'])
    persondictionary.update(address_array)
    return persondictionary

def writeToCSV(lawyers,filename):
    filepath = "HSBA_Directories/" + filename
    fileexists = exists(filepath)
    with open(filepath, 'a', newline='') as csvfile:
        fieldnames = lawyers[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if fileexists == False:
            writer.writeheader()
        for lawyer in lawyers:
            writer.writerow(lawyer)

def insertSQL(attorney):
    try:
        #Insert the new record into the sql table.
        #This function only inserts one at a time.
        #Insert Person
        logging.debug("Inserting %s",attorney['Name'])

        mydb = mysql.connector.connect(
            host=os.environ['host'],
            user=os.environ['user'],
            password=os.environ['password'],
            database=os.environ['database']
        )
        mycursor = mydb.cursor(dictionary=True)
        timestamp = datetime.now(pytz.timezone('Pacific/Honolulu'))
        
        if(attorney['Admitted HI Bar'] != ""):
            admitted_hawaii_bar = datetime.strptime(attorney['Admitted HI Bar'],'%m/%d/%Y')
        else:
            admitted_hawaii_bar = None
        
        
        sql = "INSERT INTO `HSBA 1-27-2023` (Name, `JD Number`,`License Type`,Employer,Address,AddressLine1,AddressLine2,AddressLine3,AddressLine4,AddressLine5,AddressLine6,Country,Phone,Fax, Email, `Law School`, Graduated, `Admitted HI Bar`, `HSBA ID`, `Internal ID`,Letter,ScrapedTimestamp) " \
                "VALUES (%s, %s,%s, %s,%s, %s, %s,%s, %s,%s,%s, %s,%s, %s,%s,%s,%s,%s,%s,%s,%s,%s)"
        val = (
        attorney['Name'],attorney['JD Number'],attorney['License Type'], attorney['Employer'], attorney['Address'],attorney['AddressLine1'],attorney['AddressLine2'],attorney['AddressLine3'],
        attorney['AddressLine4'],attorney['AddressLine5'],attorney['AddressLine6'],attorney['Country'],attorney['Phone'],attorney['Fax'],attorney['Email'],
        attorney['Law School'],attorney['Graduated'],admitted_hawaii_bar,attorney['HSBA ID'],attorney['Internal ID'],attorney['Letter'],timestamp)
        mycursor.execute(sql, val)
        mydb.commit()
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))
        os.exit()

logger = logging.getLogger('HSBA Logger')
if('logger' in os.environ and os.environ['logger'] == 'debug'):
    logger.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.WARNING)

print("Starting HSBA Scraper")
logger.debug(platform.system())
service = Service()

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=service, options=options)

#driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
 
letters = list(string.ascii_uppercase)

#ABCDEFGHIJKLMNOPQRSTUVWXYZ
# letters = list("Z")
#driver = webdriver.Chrome(executable_path=r'C:\Dropbox\Projects\HawaiiSele\chromedriver_win32 (1)\chromedriver.exe')
driver.get("https://hsba.org/HSBA_2020/For_the_Public/Find_a_Lawyer/HSBA_2020/Public/Find_a_Lawyer.aspx")
internal_id = 1 #TODO: This will start over at 1 if the program fails halfway. A better way would be to grab the last number from the csv if it exists.

#TODO: Add a link to the profile page as one of the columns.

#We have to delcare the filename here because otherwise if the scraper continues overnight it'll be in two filenames if generated each time it saves to the csv which is each letter.
today = date.today()
filename = f"HSBA_{today.strftime('%Y-%m-%d')}.csv"
for letter in letters:
    print("Searching ",letter)
    max_retries = 3
    retry_count = 0
    while retry_count < max_retries:
        try:
            WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, 'txtDirectorySearchLastName'))).send_keys(letter)
            WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, 'btnDirectorySearch'))).click()
            time.sleep(1)
            WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, 'ctl01_TemplateBody_WebPartManager1_gwpciNewQueryMenuCommon_ciNewQueryMenuCommon_ResultsGrid_Grid1_ctl00')))
            break  # Exit the loop if the code executes successfully
        except:
            driver.get("https://hsba.org/HSBA_2020/For_the_Public/Find_a_Lawyer/HSBA_2020/Public/Find_a_Lawyer.aspx")
            retry_count += 1
            print(f"Retry {retry_count} of {max_retries}")
            time.sleep(1)  # Wait for a moment before retrying

    if retry_count == max_retries:
        print("Max retries exceeded. Unable to execute the code.")

    html = driver.page_source
    soup = BeautifulSoup(html,'html.parser')
    table = soup.find('table',attrs={'id':'ctl01_TemplateBody_WebPartManager1_gwpciNewQueryMenuCommon_ciNewQueryMenuCommon_ResultsGrid_Grid1_ctl00'})
    rows = table.find_all('tr') #Returns something similar to a list with all row tags
    #Search for no rows
    #This happens with the letter X
    if(len(rows) == 2):
        #No names exist for this letter (see X)
        logger.debug("No names exist for letter " + letter)
        continue

    #Check to see if there is a show all button.
    try:
        show_all_link = driver.find_element(By.PARTIAL_LINK_TEXT, "Show all")
        show_all_link.click()
        show20link = "javascript:__doPostBack('ctl01$TemplateBody$WebPartManager1$gwpciNewQueryMenuCommon$ciNewQueryMenuCommon$ResultsGrid$Grid1$ctl02','')"
        WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href="' + show20link + '"]')))
    except:
        #Means there is no show all link like with Q
        print("No show all link text")

    html = driver.page_source
    soup = BeautifulSoup(html,'html.parser')
    table = soup.find('table',attrs={'id':'ctl01_TemplateBody_WebPartManager1_gwpciNewQueryMenuCommon_ciNewQueryMenuCommon_ResultsGrid_Grid1_ctl00'})
    rows = table.find_all('tr') #Returns something similar to a list with all row tags
    listofurls = []
    for index,row in enumerate(rows):
        #print(row.text)
        if(index == 0):
            #First row are headers
            continue
        atag = row.find('a')
        #We make sure it's a link for a person and not
        #an atag['href'][0:15] == '/HSBA/Directory'
        if(atag != None):
            listofurls.append(atag['href'])


    lawyers = []
    for x,link in enumerate(listofurls):
        logger.debug("Getting Attorney: " + str(id))
        driver.get("https://hsba.org" + link)
        id = link[link.find('ID=')+3:]

        WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.ID, 'ctl01_TemplateBody_WebPartManager1_gwpciDirectoryResults_ciDirectoryResults__Body')))
        time.sleep(1)
        profile_page_html = driver.page_source
        lawyerprofile = getProfileInformation(profile_page_html)
        lawyerprofile['HSBA ID'] = id
        lawyerprofile['Internal ID'] = str(internal_id)
        lawyerprofile['Letter'] = letter
        internal_id += 1
        lawyers.append(lawyerprofile)
        
        #insertSQL(lawyerprofile)
    writeToCSV(lawyers,filename)
    driver.get("https://hsba.org/HSBA_2020/For_the_Public/Find_a_Lawyer/HSBA_2020/Public/Find_a_Lawyer.aspx")

driver.close()
