import requests
from lxml import etree
from bs4 import BeautifulSoup
from prettytable import PrettyTable
from datetime import datetime, timedelta
import smtplib, ssl
import os

# Get's the current month & appends it to the URL 
month = datetime.now().strftime("%B")

# Fox sports website that pull the inter-miami team schedule (when I scrape I just get the current months schedule)
URL  = "https://www.foxsports.com/soccer/inter-miami-cf-team-schedule?month=" + month

# Mandatory libraries I am using to extract the html & dom tree so I can use look for specific Xpaths
page = requests.get(URL)
soup = BeautifulSoup(page.text, "html.parser")
dom =  etree.HTML(str(soup))

# Converts the UTC time scraped from the web to local time and in this case pacific time zone so it minuses 7 hours
def to_local_datetime(utc_dt):
 
    my_date = datetime.strptime(utc_dt, "%I:%M%p")
    
    return ((my_date - timedelta(hours=7)).time()).strftime("%I:%M %p")

i = 1
dataFromXpath=[]
while(True):
    try:
        # After a while of scraping and looking this was the smartest way or laziest way to iterate over the data to get the game time, game day, and team they are facing
        trdata = "tr["+str(i)+"]"
        teamName = dom.xpath('//*[@id="table-1"]/tbody/' +trdata+ '/td[2]/div/a[2]')[0].text.strip()
        dataFromXpath.append(teamName)
        gameDate = dom.xpath('//*[@id="table-1"]/tbody/' +trdata+  '/td[1]/div/text()')[0].strip()
        dataFromXpath.append(gameDate)
        gameTime = dom.xpath('//*[@id="table-1"]/tbody/' +trdata+ '/td[3]/div/a/text()')[0].strip()
        dataFromXpath.append(to_local_datetime(gameTime))        
        i+=1
    except IndexError:
        break


# Got this from stackoverflow, but it turns my list of data I scraped from the website into sublists of the number of items I want.
# I'm doing this because I want the data to be formatted into a readable table later
def divide_chunks(l, n): 
    # looping till length l
    for i in range(0, len(l), n): 
        yield l[i:i + n]

# We are using a prettyTable library to create a nice table
# this creates the headers for table.
dataTable = PrettyTable(["The Team InterMiami is facing", "Game Date", "GAME TIME"])

# Adds the data to the table.
dataRows = list(divide_chunks(dataFromXpath, 3))
dataTable.add_rows(dataRows)

#sending an email so email related info
port = 465
smtp_server = "smtp.gmail.com"
USER_EMAIL = os.environ.get("USER_EMAIL")
USER_PASSWORD = os.environ.get("USER_PASSWORD")
context = ssl.create_default_context()
server = smtplib.SMTP_SSL(smtp_server, port, context=context)
server.login(USER_EMAIL, USER_PASSWORD)


try:
    ## Might be a poor man's solution but, this is my way of checking if the table actually has data when printing or if the scrapper is broken.
    if dataTable[0][0]:
        print ("*******************************************************************" + " INTER-MIAMI'S SCHEDULE " + "*******************************************************************")
        print(dataTable)
        server.sendmail(USER_EMAIL, USER_EMAIL, dataTable)
        print ("*******************************************************************" + " LET's GOO!!! & HAPPY WATCHING " + "*******************************************************************")
except:
    print ("*******************************************************************" + "SORRY SCRAPPER NEEDS UPDATING OR IS BROKEN" + "*******************************************************************")





