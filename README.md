# glearn-zoom-bot
This bot attends online zoom classes according to the timetable by fetching class links from glearn (our student portal) 

### Dependencies :package:

- Make sure that python is pre-installed in your system if not [Click Here](https://www.python.org/downloads/) to download and install the latest python version.

- Install all the requirements using `pip install -r requirements.txt` command in cmd.

- Compatible Browsers : *Chrome*
  - Most of the time chrome runs in *headless mode*.

- ***Zoom desktop*** application.


### Setup & Run :rocket:
- **Zoom settings**
    -  Settings -> General -> Always show meeting controls : ON :heavy_check_mark: 
    - Settings -> Audio -> Automatically join audio by computer when joining a meeting : OFF :x:
 <br />




- Enter your G-learn credentials and Discord webhook url in **keys.env** file.
```
 USER_ID=
 PASSWORD=
 DISCORD_WEBHOOK_URL=
```
- Navigate to *glearn-zoom-bot* folder and run the bot `python bot.py`
- Make sure that _meeting controls_ are clearly visible on screen when zoom app is running.
