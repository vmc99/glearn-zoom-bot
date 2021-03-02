#Importing Libraries
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By 
import time
from datetime import datetime
from datetime import date
import os.path
from os import path
import re     #regualar Expressions
import sqlite3
import pyautogui
import schedule
from webdriver_manager.chrome import ChromeDriverManager 
import discord_webhook
from dotenv import load_dotenv
from pathlib import Path 
from imageMatch import ImageDetection
from fetch import sched_link_bot




# option 3 to restrict all downloads
prefs = {"download_restrictions":3,}

opt = Options()
opt.add_argument("start-maximized")
opt.add_argument("--disable-extensions")
opt.add_argument("--disable-infobars")
opt.add_argument("--headless")


opt2 = Options()
opt2.add_argument("start-maximized")
opt2.add_argument("--disable-extensions")
opt2.add_argument("--disable-infobars")
opt2.add_experimental_option("prefs",prefs)




# Path for key.env file
dotenv_path = Path('keys.env')


driver = None
driver2 = None



load_dotenv(dotenv_path=dotenv_path)

user = os.getenv('USER_ID')
password = os.getenv('PASSWORD')
URL = os.getenv('URL')




def login():

    global driver
    count = 0

    #Logging in
    print("logging in")
    user_id = driver.find_element_by_id("txtusername")
    user_id.send_keys(user)
    paswd = driver.find_element_by_id("password")
    paswd.send_keys(password)
    
    time.sleep(1)
    driver.find_element_by_id("Submit").click()


    # Enter into G-learn 


    class_table = None
    while True:
        try:
            if ("https://login.gitam.edu/studentapps.aspx" in driver.current_url):
                glearn_btn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "G-Learn")))
                glearn_btn.click()


            class_table = WebDriverWait(driver,60).until(EC.presence_of_element_located((By.XPATH,"//div[@id='ContentPlaceHolder1_divlblonline']")))
            class_table.location_once_scrolled_into_view

            if not(type(class_table) == type(None)): 
                break
        except:
            if count>15:
                print('Looks like G-learn is down') 

                # G-learn down send msg to discord
                discord_webhook.send_msg(class_name='-',status="G-learn down",start_time='-',end_time='-')
                return
            time.sleep(15)
            print("trying again")
            count = count+1
            driver.refresh()
    
    print('Logged in')
    time.sleep(5)     
    






def create_Database():
	conn = sqlite3.connect('custom_timetable.db')
	c=conn.cursor()
	# Create table
	c.execute('''CREATE TABLE custom_timetable(class_name text, start_time text, end_time text, day text)''')
	conn.commit()
	conn.close()
	print("Created custom_timetable Database")







def view_timetable():

    print("\nChoose to view \n")
    view_opt = int(input('1. Custom Timetable \n2. Glearn Timetable\n3. Exit\n\nEnter option : '))

    if view_opt == 1: 

        if not(path.exists('custom_timetable.db')):
            print('\nError : No Such Timetable')
            return
        conn = sqlite3.connect('custom_timetable.db')
        c=conn.cursor()
        day = 'monday'
        # Display all rows in the table
        for row in c.execute('SELECT * FROM custom_timetable'):

            if not day==row[3]:
                print('\n')
            print(row)
            day = row[3]
        
        conn.close()

    if view_opt == 2:

        if not(path.exists('glearn_timetable.db')):
            print('\nError : No Such Timetable')
            return
        conn = sqlite3.connect('glearn_timetable.db')
        c=conn.cursor()
        day = 'monday'
        # Display all rows in the table
        for row in c.execute('SELECT * FROM glearn_timetable'):

            if not day==row[3]:
                print('\n')
            print(row)
            day = row[3]
        
        conn.close()

    if view_opt == 3:
        exit()







def validate_day(inp):
    days = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']

    if inp.lower() in days:
        return True
    else:
        return False




def validate_input(regex,inp):

    if not re.match(regex,inp):
        return False
    else:
        return True





def add_timetable():
    
    if not(path.exists('custom_timetable.db')):
        create_Database()
    
    op = int(input("\n1. Add class\n2. Done adding\n\nEnter option : "))

    while(op==1):
        class_name = input("Enter class name : ")
        start_time = input("Enter class start time in 24 hour format (HH:MM) : ") 
        while not(validate_input("\d\d:\d\d",start_time)):
            print("Invalid input, trying again")
            start_time = input("Enter class start time in 24 hour format (HH:MM) : ")


        end_time = input("Enter class end time in 24 hour format (HH:MM) : ") 
        while not(validate_input("\d\d:\d\d",end_time)):
            print("Invalid input, trying again")
            end_time = input("Enter class end time in 24 hour format (HH:MM) : ")
        
        day = input("Enter Day (monday/tuesday/wednesday...etc) : ")
        while not(validate_day(day.strip())):
            print("Invalid input, trying again")
            day = input("Enter Day (monday/tuesday/wednesday...etc) : ")

        conn = sqlite3.connect('custom_timetable.db')
        c = conn.cursor()

        # Inserting a row of data

        c.execute("INSERT INTO custom_timetable VALUES ('%s','%s','%s','%s')"%(class_name,start_time,end_time,day))

        conn.commit()
        conn.close() 

        print("\nClass added to Database\n")

        op = int(input("1. Add class\n2. Done adding\n\nEnter option : "))







def modify_timetable():
    if not(path.exists('custom_timetable.db')):
        print('\nError : Custom Timetable Not Created')
        return
    
    opt =  int(input('\n1. Delete a class\n2. Delete Timetable\n\nEnter option : '))
    
    conn = sqlite3.connect('custom_timetable.db')
    c = conn.cursor()

    if(opt==1):
        print('\nTo Delete a class from the the Timetable, Enter classname and day\n\n')
        print("((Catuion! this action Removes all classes with same Classname and Day))\n\n")

        name = input("Class name : ")

        d = input("Day (monday/tuesday/wednesday...etc) : ")
        while not(validate_day(d.strip())):
            print("Invalid input, trying again")
            d = input("Day (monday/tuesday/wednesday...etc) : ")

        

        # Will return 1 if class is found else 0
        x = c.execute('''SELECT EXISTS (SELECT * FROM custom_timetable WHERE  class_name = ? and day = ?)''',(name,d)).fetchone()[0]
        
        if x==1:

            # Deleting a row 

            c.execute('''DELETE from custom_timetable WHERE class_name = ? and day = ?''',(name,d))
            print("\nClass successfully deleted from the timetable")
        else:
            print("\nClass not found in timetable, Deletion of Class Unsuccessful")

    

    if(opt==2):
        print("\nAre you sure ? This action deletes all the contents in the timetable\n\n")
        ans = int(input("1. YES\n2. NO\n\nEnter option : "))

        if(ans==1):

            # Deleting table

            c.execute('DELETE FROM custom_timetable')
            print("Timetable Successfully Deleted")

        if(ans==2):
            print("Deletion of Timetable Unsuccessful")



    conn.commit()
    conn.close()





def join_audio(class_name,start_time,end_time,date_string):
    global driver
    count = 0

    while True:

        time.sleep(5)
        join_audio_btn = ImageDetection('Images/join_audio.png',0.75,'grayscale')
        if not(type(join_audio_btn) == type(None)):
            pyautogui.moveTo(join_audio_btn)
            pyautogui.click()
            break 

        else:

            if(count>30):
                #Class Cancelled Exiting from function
                return False 

            count+=1
            print('Join audio button not found, trying again')
            time.sleep(15)

    
    time.sleep(5)


    # Stop Video
    stop_video_btn = ImageDetection('Images/stop_video.png',0.95,'grayscale')
    if not(type(stop_video_btn) == type(None)):
        pyautogui.moveTo(stop_video_btn)
        pyautogui.click()


    # Mute Mic
    mute_btn = ImageDetection('Images/mute.png',0.8,'grayscale')
    if not(type(mute_btn) == type(None)):
        pyautogui.moveTo(mute_btn)
        pyautogui.click()


    
    # Moving mouse away from the meeting controls 
    pyautogui.moveTo(x=960,y=540) 
    

    tmp = "%H:%M"

    t = time.localtime()
    current_start_time = time.strftime(tmp, t) # Current time

    print('Joined class')

    # Class joined send msg to discord
    discord_webhook.send_msg(class_name=class_name,status="joined",start_time=current_start_time,end_time=end_time,t_date=date_string) 

    
    class_running_time = datetime.strptime(end_time,tmp) - datetime.strptime(current_time,tmp)
    
    # Sleep till class end time
    print("Waiting till the class ends")
    waiting_time = class_running_time.seconds   
    time.sleep(waiting_time)




    leave_btn = ImageDetection('Images/leave.png',0.8,'grayscale')
    if not(type(leave_btn) == type(None)):
        pyautogui.moveTo(leave_btn)
        pyautogui.click()
    else:
        print('leave button not found')

    time.sleep(1)
    leave_meeting_btn = ImageDetection('Images/leave_meeting.png',0.8,'grayscale')
    if not(type(leave_meeting_btn) == type(None)):
        pyautogui.moveTo(leave_meeting_btn)
        pyautogui.click()   
    else:
        print('leave meeting button not found')


    print("Class left")

    t = time.localtime()
    current_end_time = time.strftime(tmp, t) # Current time
    
    # Class left send msg to discord
    discord_webhook.send_msg(class_name=class_name,status="left",start_time=current_start_time,end_time=current_end_time,t_date=date_string)


    return True






# Extracting time
def extract_time(date_time):
    str = date_time
    time = str.split()
    tmp = time[4].split(':')
    tmp2 = []
    tmp2 = tmp[1] +":"+ tmp[2]
    return tmp2



# Conversion 12hr to 24hr
def convert_time(timing):
    in_time = datetime.strptime(timing, "%I:%M%p")
    out_time = datetime.strftime(in_time, "%H:%M")
    return out_time






def join_class(class_name,start_time,end_time):
    global driver
    global driver2
    
    try:
        driver.refresh()
        time.sleep(10)

        glearn_url = 'http://glearn.gitam.edu/student/welcome.aspx'
        if not((glearn_url).lower() == (driver.current_url).lower()):
            print('glearn not loaded')
            login()



    except:
        driver.close()
        time.sleep(10)
        print('browser closed, opening again')
        start_browser()

    # Today's date
    today_date = date.today()
    # Today's date converted to string
    date_string = today_date.strftime("%d-%b-%Y") 
    count = 0
    check = False

    while True:

        # List is created
        classes_available = driver.find_elements_by_xpath("//table[@id='ContentPlaceHolder1_GridViewonline']/tbody/tr") # List is created

        for i in range(len(classes_available)):

            # Class name
            x_path1 = f"//*[@id='ContentPlaceHolder1_GridViewonline']/tbody/tr[{i+1}]/td/a/div/h4" 
            # date and time 
            x_path2 = f"//table[@id='ContentPlaceHolder1_GridViewonline']/tbody/tr[{i+1}]/td/a/div/h6"  

            className = driver.find_element_by_xpath(x_path1).text
            date_time = driver.find_element_by_xpath(x_path2).text


            # Extract Time
            timing = extract_time(date_time) 
            converted_time = convert_time(timing)
            
            # Extract Day
            temp = date_time.split()
            class_date = (temp[2].split("-"))[0]
            class_date = int(class_date)







            if start_time == converted_time and today_date.day == class_date:

                check = True
                print("JOINING :",className)

                link = f"//tbody/tr[{i+1}]/td[1]/a" 
                zoom_link = driver.find_element_by_xpath(link).get_attribute('href')
                time.sleep(5)

                # Using driver2 for opening zoom link 
                
                driver2 = webdriver.Chrome(ChromeDriverManager().install(),options=opt2,service_log_path='NUL')
                driver2.get(zoom_link)
                WebDriverWait(driver2,10000).until(EC.visibility_of_element_located((By.TAG_NAME,'body')))

                break

        if check == False:

            if count>15:
                print("No class")

                # NO class send msg to discord
                discord_webhook.send_msg(class_name=class_name,status="noclass",start_time=start_time,end_time=end_time,t_date=date_string)
                return

            print("Class not found, trying again")
            time.sleep(60)
            driver.refresh()
            count +=1
            time.sleep(3)

        if check == True:
            break 
    

    time.sleep(5)

    # open zoom 

    loop_var = 0
    while loop_var<10:

        open_zoom_btn =  ImageDetection('Images/open_zoom.png',0.75,'grayscale')

        if type(open_zoom_btn) == type(None):
            open_zoom_btn =  ImageDetection('Images/open_zoom_dark.png',0.75,'grayscale')

        if not(type(open_zoom_btn) == type(None)):
            pyautogui.moveTo(open_zoom_btn)
            pyautogui.click()
            break
        else:
            loop_var+=1
            time.sleep(1)

    
    if type(open_zoom_btn) == type(None):
        open_zoom_btn =  ImageDetection('Images/open_zoom.png',0.75,'edged')
    
        if not(type(open_zoom_btn) == type(None)):
            pyautogui.moveTo(open_zoom_btn)
            pyautogui.click()


    
    # To join a new meeting if the previous meeting is still going on  

    loop_var = 0
    while loop_var<3:
        leave_join_btn = ImageDetection('Images/leave_join.png',0.75,'grayscale')
        if not(type(leave_join_btn) == type(None)):
            pyautogui.moveTo(leave_join_btn)
            pyautogui.click()
            break
        else:
            loop_var+=1
            time.sleep(1)



    time.sleep(5)
    driver2.close()

    # after opening zoom desktop app

    Entered_class = join_audio(className,start_time,end_time,date_string)

    if Entered_class == False:
        print("looks like class is cancelled") 

        # Class Cancelled send msg to discrod
        discord_webhook.send_msg(class_name=class_name,status="zoom_link down",start_time=start_time,end_time=end_time,t_date=date_string)
        return






def sched(timetable_choice):

    query = f'SELECT * FROM {timetable_choice}'

    if(timetable_choice == 'custom_timetable'):

        if not(path.exists('custom_timetable.db')):
            print('\nError : No Such Timetable')
            return

        conn = sqlite3.connect('custom_timetable.db')
        c=conn.cursor()
    
    if(timetable_choice == 'glearn_timetable'):
        
        # call sched_link_bot for generating glearn_timetable
        sched_link_bot()
        if not(path.exists('glearn_timetable.db')):
            print('\nError : No Such Timetable')
            return

        conn = sqlite3.connect('glearn_timetable.db')
        c=conn.cursor()


    for row in c.execute(query):

        # Schedule all classes
        name = row[0]
        start_time = row[1]
        end_time = row[2]
        day = row[3]



        if day.lower()=="monday":
            schedule.every().monday.at(start_time).do(join_class,name,start_time,end_time)
            print(f"Scheduled class {name} on {day} at {start_time}")
        if day.lower()=="tuesday":
            schedule.every().tuesday.at(start_time).do(join_class,name,start_time,end_time)
            print(f"Scheduled class {name} on {day} at {start_time}")
        if day.lower()=="wednesday":
            schedule.every().wednesday.at(start_time).do(join_class,name,start_time,end_time)
            print(f"Scheduled class {name} on {day} at {start_time}")
        if day.lower()=="thursday":
            schedule.every().thursday.at(start_time).do(join_class,name,start_time,end_time)
            print(f"Scheduled class {name} on {day} at {start_time}")
        if day.lower()=="friday":
            schedule.every().friday.at(start_time).do(join_class,name,start_time,end_time)
            print(f"Scheduled class {name} on {day} at {start_time}")
        if day.lower()=="saturday":
            schedule.every().saturday.at(start_time).do(join_class,name,start_time,end_time)
            print(f"Scheduled class {name} on {day} at {start_time}")
        if day.lower()=="sunday":
            schedule.every().sunday.at(start_time).do(join_class,name,start_time,end_time)
            print(f"Scheduled class {name} on {day} at {start_time}")





    # Start browser
    start_browser()
    while True:
        # Checks whether a scheduled task is pending to run or not
        schedule.run_pending()
        time.sleep(1)







def start_browser():

    global driver 

    driver = webdriver.Chrome(ChromeDriverManager().install(),options=opt,service_log_path='NUL')

    driver.get(URL)

    WebDriverWait(driver,10000).until(EC.visibility_of_element_located((By.TAG_NAME,'body')))

    print('browser started')

    login()






if __name__=="__main__":
   
    while True:
        print('\n1. Start Bot\n2. Add Timetable (Custom Timetable)\n3. Modify Timetable (Custom Timetable) \n4. View Timetables\n5. Exit\n\n')
        op = int(input(("Enter option : ")))
    
        if(op==1):
            print('\nChoose timetable')
            op2 = int(input(("\n1. Custom Timetable\n2. Glearn Timetable (fetches directly from glearn)\n3. Exit\n\nEnter option : ")))
            if(op2==1):
                sched('custom_timetable')
            if(op2==2):
                sched('glearn_timetable')
            if(op2==3):
            	exit()

        if(op==2):
            add_timetable()

        if(op==3):
            modify_timetable()

        if(op==4):
            view_timetable()

        if(op==5):
            exit()