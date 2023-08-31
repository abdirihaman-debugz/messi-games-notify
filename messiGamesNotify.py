import requests
from lxml import etree
from bs4 import BeautifulSoup
from prettytable import PrettyTable
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
# Get's the current month & appends it to the URL 
month = datetime.now().strftime("%B")

# Fox sports website that pull the inter-miami team schedule (when I scrape I just get the current months schedule)
URL1  = "https://www.foxsports.com/soccer/inter-miami-cf-team-schedule?month=" + month
URL2 = "https://www.foxsports.com/soccer/inter-miami-cf-team-schedule"

# Mandatory libraries I am using to extract the html & dom tree so I can use look for specific Xpaths
page = requests.get(URL2)
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

#sending an email with table in it

# Convert the PrettyTable to HTML format
table_html = dataTable.get_html_string()

# Email configuration
USER_EMAIL = os.environ.get("USER_EMAIL")
USER_PASSWORD = os.environ.get("USER_PASSWORD")
sender_email = USER_EMAIL
receiver_email = USER_EMAIL  # Use the same email address for sender and receiver
password = USER_PASSWORD
subject = "Inter Miami Schedule"

# Create a MIMEText object for the email content
email_body = MIMEMultipart()
email_body.attach(MIMEText(table_html, "html"))

# Set the email headers
email_body["From"] = sender_email
email_body["To"] = receiver_email
email_body["Subject"] = subject

# Connect to the SMTP server
smtp_server = "smtp.gmail.com"  # Example for Gmail
smtp_port = 587  # Gmail uses port 587 for TLS
smtp_username = sender_email

try:
    # Establish a connection to the SMTP server
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()  # Upgrade the connection to secure (TLS)

    # Log in to your email account
    server.login(smtp_username, password)

    # Send the email
    server.sendmail(sender_email, receiver_email, email_body.as_string())

    # Close the SMTP server connection
    server.quit()
    print("Email with table data sent to yourself successfully!")

except Exception as e:
    print(f"An error occurred: {str(e)}")


# printing out so make sure we can see the data in the github actions pipeline 
print(dataTable.get_formatted_string)





