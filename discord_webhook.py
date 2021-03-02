from discord_webhooks import DiscordWebhooks
import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('keys.env')

load_dotenv(dotenv_path=dotenv_path)


webhook_url = os.getenv('DISCORD_WEBHOOK_URL')


def send_msg(class_name,status,start_time,end_time,t_date):

    WEBHOOK_URL = webhook_url 

    webhook = DiscordWebhooks(WEBHOOK_URL)


    if(status=="joined"):

      webhook.set_content(title='Class Joined Succesfully',
                          description="Here's your report :zap:")

      # Appends a field
      webhook.add_field(name='Class', value=class_name)
      webhook.add_field(name='Status', value=status)
      webhook.add_field(name='Joined at', value=start_time)
      webhook.add_field(name='Leaving at', value=end_time)
      webhook.add_field(name='Date',value=t_date)
      

    elif(status=="left"):
      webhook.set_content(title='Class Left Succesfully',
                          description="Here's your report :comet:")

      # Appends a field
      webhook.add_field(name='Class', value=class_name)
      webhook.add_field(name='Status', value=status)
      webhook.add_field(name='Joined at', value=start_time)
      webhook.add_field(name='Left at', value=end_time)
      webhook.add_field(name='Date',value=t_date)


    elif(status=="noclass"):
      webhook.set_content(title='Seems Like No Class Today',
                          description="Class Link Not Found! Assuming no class :sunglasses:")

      # Appends a field
      webhook.add_field(name='Class', value=class_name)
      webhook.add_field(name='Status', value=status)
      webhook.add_field(name='Expected Join time', value=start_time)
      webhook.add_field(name='Expected Leave time', value=end_time)
      webhook.add_field(name='Date',value=t_date)



    elif(status=="G-learn down"):
      webhook.set_content(title='G-learn Is Not Responding',
                          description="Zoom bot failed to join :boom:")

      # Appends a field
      webhook.add_field(name='Status', value=status)




    elif(status=="zoom_link down"):
      webhook.set_content(title='Zoom Link Is Not Working',
                          description="Zoom bot failed to join :boom:")

      # Appends a field
      webhook.add_field(name='Class', value=class_name)
      webhook.add_field(name='Status', value=status)
      webhook.add_field(name='Expected Join time', value=start_time) 
      webhook.add_field(name='Expected Leave time', value=end_time)
      webhook.add_field(name='Date',value=t_date)



    # Attaches a footer
    webhook.set_footer(text='-- Zoom Classes')

    webhook.send()

    print("Sent message to discord")
