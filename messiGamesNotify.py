import requests
from lxml import etree
from bs4 import BeautifulSoup
from prettytable import PrettyTable



#Fox sports website that pull the inter-miami team schedule (when I scrape I just get the current months schedule)
URL  = "https://www.foxsports.com/soccer/inter-miami-cf-team-schedule"

#mandatory libraries I am using to extract the html & dom tree so I can use look for specific Xpaths
page = requests.get(URL)
soup = BeautifulSoup(page.text, "html.parser")
dom =  etree.HTML(str(soup))


i = 1
dataFromXpath=[]
while(True):
    try:
        #After a while of scraping and looking this was the smartest way or laziest way to iterate over the data to get the game time, game day, and team they are facing
        trdata = "tr["+str(i)+"]"
        teamName = dom.xpath('//*[@id="table-1"]/tbody/' +trdata+ '/td[2]/div/a[2]')[0].text.strip()
        dataFromXpath.append(teamName)
        gameDate = dom.xpath('//*[@id="table-1"]/tbody/' +trdata+  '/td[1]/div/text()')[0].strip()
        dataFromXpath.append(gameDate)
        gameTime = dom.xpath('//*[@id="table-1"]/tbody/' +trdata+ '/td[3]/div/a/text()')[0].strip()
        dataFromXpath.append(gameTime)        
        i+=1
    except IndexError:
        break
# Got this from stackoverflow, but it turns my list of data I scraped from the website into sublists of the number of items I want.
# I'm doing this because I want the data to be formatted into a readable table later
def divide_chunks(l, n): 
    # looping till length l
    for i in range(0, len(l), n): 
        yield l[i:i + n]

#We are using a prettyTable library to create a nice table
#this creates the headers for table.
myTable = PrettyTable(["The Team InterMiami is facing", "The Date", "UTC TIME"]) #future work - add library to change UTC to current time.

#Adds the data to the table.
x = list(divide_chunks(dataFromXpath, 3))
myTable.add_rows(x)

print(myTable)