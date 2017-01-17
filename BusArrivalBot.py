import logging
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

import requests
from datetime import datetime
from os import environ
import dateutil.parser
import json
from geopy.distance import vincenty

from credentials import APP_URL, TOKEN, ACCOUNTKEY

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

#non-bot stuff
def getBusses(busStopID):
    #API parameters
    target = 'http://datamall2.mytransport.sg/ltaodataservice/BusArrival'

    #Build query string
    headers = { 'AccountKey': ACCOUNTKEY,
    'accept': 'application/json'}
    params = { 'BusStopID': busStopID,
    'SST': 'TRUE'}

    #Obtain results
    return requests.get(target, headers = headers, params = params)


def arrivals(bot, update):
    chat_id = update.message.chat_id
    busStopID = update.message.text.replace("/arrivals ", "")
    if (busStopID == ''):
        bot.sendMessage(chat_id=chat_id, text="Please enter a valid stop ID")
        return
    else:
        text = getArrivalsText(busStopID)

    if (text == ""): #if text is empty, indicates that bus services array was empty (due to invalid stop ID)
        bot.sendMessage(chat_id=chat_id, text="Please enter a valid stop ID")
    else:
        bot.sendMessage(chat_id=chat_id, text=text)

#gets the text to be printed to the user
def getArrivalsText(busStopID):

    stopInfo = getBusses(busStopID)
    text = '' #text to be printed to user

    #format result
    stopInfo = stopInfo.json()
    listOfBusses = stopInfo["Services"]
    currentTime = datetime.utcnow() #get current time

    for bus in listOfBusses:
        text += bus["ServiceNo"] + "\n"
        nextArrival = bus["NextBus"]["EstimatedArrival"] #gets ISO 8601-formatted date
        subsequentArrival = bus["SubsequentBus"]["EstimatedArrival"]
        text += "Next: "

        if (nextArrival == ''): #no busses
            text += "-\n"
        else:
            nextArrivalTime = dateutil.parser.parse(nextArrival)
            #format to naive datetime in order to do comparison
            nextArrivalTime = nextArrivalTime.replace(tzinfo=None)
            arrival = nextArrivalTime - currentTime
            arrivalTime = int(arrival.total_seconds() / 60) #get arrival time in minutes
            if (arrivalTime == 0):
                text += "arriving...\n"
            else:
                text = text + str(int(arrival.total_seconds() / 60)) + "m\n"

            text += "Subsequent: "
            if(subsequentArrival == ''):
                text += "-\n"
            else:
                subsequentArrivalTime = dateutil.parser.parse(subsequentArrival)
                #format to naive datetime in order to do comparison
                subsequentArrivalTime = subsequentArrivalTime.replace(tzinfo=None)
                arrival = subsequentArrivalTime - currentTime
                arrivalTime = int(arrival.total_seconds() / 60) #get arrival time in minutes
                if (arrivalTime == 0):
                    text += "arriving...\n"
                else:
                    text = text + str(int(arrival.total_seconds() / 60)) + "m\n"
        text += "\n"
    text = text.rstrip() #rstrip removes the additional \n characters from the back of the string

    if text != "": #if the query was successful
        #append stopID to the top
        text = "Arrival timings for [" + stopInfo["BusStopID"] + "]:\n\n" + text

    return text

class Node:
    def __init__(self, data):
        self.left = None
        self.right = None
        self.data = data
    
    def getData(self):
        return self.data

class KDTree:
    #with presorted lists
    def __init__(self, X, Y):
        self.root = self.BuildKDTreePre(X, Y, True)

    def BuildKDTreePre(self, X, Y, isOdd):
        if (len(X) == 1):
            return Node(X[0])

        xLeft = [] #to store points before and after the reference point
        xRight = []
        yLeft = []
        yRight = []
        if (isOdd): #if on the odd level, split according to longitude
            if (len(X) == 0):
                return None

            m = len(X) // 2 #find middle index
            root = Node(X[m])
            xLeft = X[:m]
            xRight = X[m+1:]
            for point in Y:
                if point["Longitude"] < root.data["Longitude"]:
                    yLeft.append(point)
                elif point["Longitude"] == root.data["Longitude"]: #ignore same point
                    continue
                else:
                    yRight.append(point)
            root.left = self.BuildKDTreePre(xLeft, yLeft, False)
            root.right = self.BuildKDTreePre(xRight, yRight, False)

        else: #change X with Y, split according to latitude
            if (len(Y) == 0):
                return None

            m = len(Y) // 2
            root = Node(Y[m])
            yLeft = Y[:m]
            yRight = Y[m+1:]
            for point in X:
                if point["Latitude"] < root.data["Latitude"]:
                    xLeft.append(point)
                elif point["Latitude"] == root.data["Latitude"]: #ignore same point
                    continue
                else:
                    xRight.append(point)
            root.left = self.BuildKDTreePre(xLeft, yLeft, True)
            root.right = self.BuildKDTreePre(xRight, yRight, True)

        return root

    #returns True if data is not found in blacklist
    def notPresent(self, blacklist, data):
        for item in blacklist:
            if item["BusStopCode"] == data["BusStopCode"]:
                return False
        return True

    #intermediary user function that calls getNearestH function
    #querypoint should be a dictionary consisting of
    #Latitude, Longitude, and Coordinates
    def getNearest(self, queryPoint):
        infinite = float("inf")
        nearestStops = []
        while len(nearestStops) != 5:
            champion = self.getNearestH(self.root, True, queryPoint, 
            {"Object": None, "Distance": infinite}, nearestStops)
            nearestStops.append(champion["Object"])

        return nearestStops

    #Helper function for the getNearest function
    #isOdd should start as true (counting first level as 1)
    #curNode starts from root
    #searches for nearest stop to query that is not already in the blacklist
    def getNearestH(self, curNode, isOdd, queryPoint, champion, blacklist):

        if curNode == None: #base case
            return champion
        else: #get distance of queryPoint to current stop
            stopLocation = (curNode.data["Latitude"], curNode.data["Longitude"])
            curDist = vincenty(queryPoint["Coordinates"], stopLocation).meters
            #print(curNode.data)

        #update champion
        if curDist < champion["Distance"] and self.notPresent(blacklist, curNode.data):
            champion["Distance"] = curDist
            champion["Object"] = curNode.data

        #check which plane to compare the point and traverse roots of current node
        if isOdd: #compare longitude
            #check if hypersphere intersects axis of current node
            borderCoord = (queryPoint["Latitude"], curNode.data["Longitude"])
            borderDist = vincenty(queryPoint["Coordinates"], borderCoord).meters
            if queryPoint["Longitude"] < curNode.data["Longitude"]:
                #go left if queryPoint is left of node
                champion = self.getNearestH(curNode.left, False, queryPoint, champion, blacklist)

                #if hypersphere intersects plane
                if champion["Distance"] > borderDist:
                    #go right branch
                    champion = self.getNearestH(curNode.right, False, queryPoint, champion, blacklist)
            else:
                #go right
                champion = self.getNearestH(curNode.right, False, queryPoint, champion, blacklist)

                if champion["Distance"] > borderDist:
                    #go left branch
                    champion = self.getNearestH(curNode.left, False, queryPoint, champion, blacklist)

        else: #compare latitude
            borderCoord = (queryPoint["Longitude"], curNode.data["Latitude"])
            borderDist = vincenty(queryPoint["Coordinates"], borderCoord).meters
            if queryPoint["Latitude"] < curNode.data["Latitude"]:
                #go left
                champion = self.getNearestH(curNode.left, True, queryPoint, champion, blacklist)

                if champion["Distance"] > borderDist:
                    #go right branch
                    champion = self.getNearestH(curNode.right, True, queryPoint, champion, blacklist)

            else:
                #go right
                champion = self.getNearestH(curNode.right, True, queryPoint, champion, blacklist)

                if champion["Distance"] > borderDist:
                    #go left branch
                    champion = self.getNearestH(curNode.left, True, queryPoint, champion, blacklist)

        return champion

#bot functions
def start(bot, update):
    chat_id = update.message.chat_id
    text = "Use /arrivals StopID to retrieve bus arrival timings for a particular stop.\n"
    text = text + "e.g. /arrivals 16189\n"
    text = text + "You can also send your location to the bot to find the nearest stops!\n\n"
    text = text + "Do note that this is still a work in progress, so bugs may be present\n"
    text = text + "Please report any bugs you find to shaohui@u.nus.edu"
    bot.sendMessage(chat_id=chat_id, text=text)

def location(bot, update):
    chat_id = update.message.chat_id
    latitude = update.message.location.latitude
    longitude = update.message.location.longitude

    queryPoint = {"Latitude": latitude,
                  "Longitude": longitude,
                  "Coordinates": (latitude, longitude)}

    nearestStops = stopsTree.getNearest(queryPoint) #this gets an array of busstop objects

    #craft the inlinekeyboard buttons
    keyboard = []
    for stop in nearestStops:
        buttonText = "[" + stop["BusStopCode"] + "] " + stop["Description"]
        keyboard.append([InlineKeyboardButton(buttonText, callback_data=stop["BusStopCode"])])
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = "Here are the 5 closest bus stops:"
    bot.sendMessage(chat_id=chat_id, text=text, reply_markup=reply_markup)

def help(bot, update):
    start(bot, update) #print start message as placeholder since I can't think of anything

def error(bot, update, error):
    logging.warning('Update "%s" caused error "%s"' % (update, error))

def button(bot, update):
    query = update.callback_query
    chat_id = query.message.chat_id

    text = getArrivalsText(query.data)

    bot.editMessageText(chat_id=query.message.chat_id,
                    text=text,
                    message_id=query.message.message_id)

def main():
    #initialise KD Tree for bus stop searching
    with open('stops.json') as json_data:
        stopsList = json.load(json_data)
    latSorted = stopsList["latSorted"]
    longSorted = stopsList["longSorted"]

    #using global variable so that it only needs to be initialised once
    global stopsTree
    stopsTree = KDTree(longSorted, latSorted)

    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Initialise bot
    global bot
    bot = Bot(token=TOKEN)

    # setup webhook
    PORT = int(environ.get('PORT', '5000'))
    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
    updater.bot.setWebhook(APP_URL + TOKEN)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('arrivals', arrivals))
    updater.dispatcher.add_handler(MessageHandler(Filters.location, location))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_error_handler(error)

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()

if __name__ == "__main__":
    main()
