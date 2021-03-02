#Importing Libraries
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By 
import time
from datetime import datetime, timedelta
from datetime import date
import schedule
from webdriver_manager.chrome import ChromeDriverManager 
import discord_webhook 
import os
import os.path
from os import path
import sqlite3
from dotenv import load_dotenv
from pathlib import Path


dotenv_path = Path('keys.env')



opt = Options()

opt.add_argument("start-maximized")
opt.add_argument("--disable-extensions")
opt.add_argument("--disable-infobars")
opt.add_argument("--headless")


link_driver = None




load_dotenv(dotenv_path=dotenv_path)

user = os.getenv('USER_ID')
password = os.getenv('PASSWORD')
URL = os.getenv('URL')




def login():

    global link_driver
    count = 0

    #Logging in
    print("logging in")
    user_id = link_driver.find_element_by_id("txtusername")
    user_id.send_keys(user)
    paswd = link_driver.find_element_by_id("password")
    paswd.send_keys(password)
    
    time.sleep(1)
    link_driver.find_element_by_id("Submit").click()
    


    # Enter into G-learn 
    

    timetable_btn = None
    while True:
        try:

            if ("https://login.gitam.edu/studentapps.aspx" in link_driver.current_url):
                glearn_btn = WebDriverWait(link_driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "G-Learn")))
                glearn_btn.click()

            timetable_btn = WebDriverWait(link_driver, 60).until(EC.presence_of_element_located((By.LINK_TEXT, "My timetable")))
            timetable_btn.location_once_scrolled_into_view

            if not(type(timetable_btn) == type(None)):
                timetable_btn.click()
                break

        except:
            if count>15:
                print('Looks like G-learn is down') 

                # send msg to discord
                discord_webhook.send_msg(class_name='-',status="G-learn down",start_time='-',end_time='-',t_date='-')
                return

            time.sleep(15)
            print("trying again")
            count = count+1
            link_driver.refresh()
    
    print('Logged in\n')
    time.sleep(5)   






def create_Database():
    conn = sqlite3.connect('glearn_timetable.db')
    c=conn.cursor()
    # Create table
    c.execute('''CREATE TABLE glearn_timetable(class_name text, start_time text, end_time text, day text)''')
    conn.commit()
    conn.close()
    print("Created glearn_timetable Database")








def sched_link_bot():

    opti = 1
    if not(path.exists('glearn_timetable.db')):
        create_Database()
    else:
        print('\nDo you want to fetch new data (timtable) from glearn or use old data ?\n')
        opti = int(input('1. Want new timetable (fetch again) \n2. Continue with old timetable \n3. Exit\n\nEnter option : '))
        if opti == 2:
            return
        if opti == 3:
            exit()


    if opti == 1:
        # Start browser
        start_browser()

        conn = sqlite3.connect('glearn_timetable.db')
        c = conn.cursor()
        
        c.execute('DELETE FROM glearn_timetable')
        conn.commit()

        # fetch all classes
        timetable = link_driver.find_elements_by_xpath("//table[@id='ContentPlaceHolder1_grd1']/tbody/tr") 
        columns = timetable[0].find_elements_by_tag_name('th')

        for i in range(len(timetable)+1):


            for j in range(2,len(columns)):

                if i>1:

                    class_name_xpath = f"//table[@id='ContentPlaceHolder1_grd1']/tbody/tr[{i}]/td[{j}]"
                    class_name = link_driver.find_element_by_xpath(class_name_xpath).text
                    if not class_name == "":

                        
                        day_xpath = f"//table[@id='ContentPlaceHolder1_grd1']/tbody/tr[{i}]/td[{1}]"
                        day = link_driver.find_element_by_xpath(day_xpath).text

                        timings_xpath = f"//table[@id='ContentPlaceHolder1_grd1']/tbody/tr[{1}]/th[{j}]"
                        timings = link_driver.find_element_by_xpath(timings_xpath).text
                        timings_split = timings.split('to')
                        start_time = timings_split[0].strip()
                        end_time = timings_split[1].strip()

                        # Inserting a row of data

                        c.execute("INSERT INTO glearn_timetable VALUES ('%s','%s','%s','%s')"%(class_name,start_time,end_time,day))
                        conn.commit()


                    else:
                        continue

    

        conn.commit()
        conn.close() 

        print("\nAll Classes added into glearn_timetable.db\n")

        link_driver.close()

        print('Browser Closed\n')

    else:
        exit()






def start_browser():

    print('Browser started')

    global link_driver
    link_driver = webdriver.Chrome(ChromeDriverManager().install(),options=opt,service_log_path='NUL')

    link_driver.get(URL)

    WebDriverWait(link_driver,10000).until(EC.visibility_of_element_located((By.TAG_NAME,'body')))

    login()







