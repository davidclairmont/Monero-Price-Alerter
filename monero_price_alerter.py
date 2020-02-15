import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup

monero_low_threshold = 80
monero_high_threshold = 100
## if a user wanted to make this work with their own IFTTT account, they would have to create 2 events
## called monero_price_emergency and monero_price_update both events would take a value called value1
## the user would have to replace the key at the end of the ifttt_url with their own account key and download the IFTTT phone app
ifttt_url = "https://maker.ifttt.com/trigger/{}/with/key/nlzvcL0AYpmG6i8_KIXMUn8PZzXCbMZpqCeaQvghR8_"

## function to get the current price of monero
def getCurrentPrice():
    ## gets a request from the site that contains the current price of monero
    r = requests.get("https://www.livecoinwatch.com/price/Monero-XMR")
    ## compresses all the text from the site into a variable called data
    data = r.text
    ## creates a beautiful soup object with the site data in order to parse it and calls the prettify method on it
    soup = BeautifulSoup(data, "html.parser")
    ## the prettify method turns the parsed website data into a formatted string
    soup.prettify()
    ## finds the <span class="price"> html line which contains the text needed for the price
    price = str(soup.find("span", class_="price").text)
    ## removes the $ sign from the price text
    price = float(price[1:])
    return price

## function to create the HTTP POST request to the IFTTT site
def ifttt(event, price):
    ## creates a dictionary called data and stores the price with the key name value1
    data = {'value1': price}
    # formats the ifttt url variable with the event that is occuring
    ifttt_event_url = ifttt_url.format(event)
    # Sends a HTTP POST request to the webhook URL
    requests.post(ifttt_event_url, json=data)

def main():
    monero_history = []
    while True:
        price = getCurrentPrice()
        date = datetime.now()
        monero_history.append({'date': date, 'price': price})

        ## if the price is above or below the set thresholds then an emergency notifiction is sent
        if price > monero_high_threshold or price < monero_low_threshold:
            ifttt('monero_price_emergency', price)
        
        ## if there are 4 price/time stamps within the list, the notification is sent
        if len(monero_history) == 4:
            rows = []
            ## for loop that formats the date and time into a neat line
            for monero_price in monero_history:
                date = monero_price['date'].strftime('%m-%d-%Y %I:%M %p')
                price = monero_price['price']
                row = '\n{}: ${}'.format(date, price)
                rows.append(row)
            monero_history = '\n'.join(rows)
            ifttt('monero_price_update', monero_history)
            monero_history = []
        ## every 5 minutes, the price of monero will be added to the monero history list
        time.sleep(60*5)

if __name__ == '__main__':
    main()
