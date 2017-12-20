from matrix_bot_api.mcommand_handler import MCommandHandler
import urllib.request
import urllib.parse
import json
from datetime import datetime
import requests

HELP_DESC = ("!pot\t\t\t\t\t\t\t-\tDisplays the current meal at Pot.")

#pot url
link = "https://pot.stusta.de/plan.json"

#search url
imageSearch = "https://api.qwant.com/api/search/images?count=1&offset=1&q=%s"

#determinates the month of day from the given argument
def getDate(args, room):
    #if an argument was passed
    if args:
        dateStr = args[0]
        #if the arg is confertable to an int
        if isinstance(dateStr, int):
            return int(dateStr)
        else:
            if args[0] == "morgen":
                return datetime.now().day
            elif dateStr == "übermorgen" or dateStr == "uebermorgen":
                return datetime.now().day + 1

            elif dateStr == "heute":
                return datetime.now().day - 1
            elif dateStr == "gestern":
                return datetime.now().day - 2
            else:
                try:
                    return datetime.strptime(dateStr, '%d.%m.').day - 1
                except:
                    #if it is not confertible show error massage
                    room.send_text("Usage: !pot <date>, date as dd.mm., dd or heute/morgen/übermorgen")

    else:
        return datetime.now().day - 1


def register_to(bot):
    def pot_handler(room, event):
        potJson = urllib.request.urlopen(link).read()
        data = json.loads(potJson.decode())

        args = event['content']['body'].split()
        args.pop(0)

        indexDay = getDate(args, room)

        currentDayInfo = data[indexDay]

        strToSend = "Hey " + event['sender'] + ", heute gibt es <strong>" + str(
            currentDayInfo["meal"]) + "</strong> im Pot. Komm doch im O-Haus vorbei :)<br>" + \
                    "Küche: " + currentDayInfo["kitchen"] + "; Bar: " + currentDayInfo["bar"]

        #if the day is not today, change "heute"
        if indexDay != datetime.now().day - 1:
            strToSend = strToSend.replace("heute", str(indexDay + 1) + "." + str(datetime.now().month) + ".")
        #if there is an event
        if currentDayInfo["event"]:
            strToSend += "<br>Außerdem findet heute folgendes Event statt: <strong>" + currentDayInfo[
                "event"] + "</strong>"

        strToSend += "<br><br>Weitere Infos findest du auf https://pot.stusta.de"

        #url for the image search
        webimgstr = imageSearch.replace("%s", urllib.parse.quote_plus(currentDayInfo["meal"]))
        #http request object
        img = urllib.request.Request(
            webimgstr,
            headers={'User-Agent': 'Mozilla/5.0'})
        img = urllib.request.urlopen(img).read()
        img = json.loads(img.decode())

        # Abort image upload, if no image for the meal was found
        try:
            imgData = img["data"]["result"]["items"][0]["media"]
            #request meal image
            r = requests.get(imgData)
        except IndexError as e:
            r = None

        #if request was successful
        if r:
            #upöoad and display image
            img = r.content
            typ = r.headers['content-type']
            print('Downloaded', typ)
            up = room.client.api.media_upload(img, typ)
            print('Uploaded', up)
            uri = up['content_uri']
            room.send_image(uri, currentDayInfo["meal"])

        #send information text
        room.send_html(strToSend)

    pot_handler = MCommandHandler("pot", pot_handler)
    bot.add_handler(pot_handler)
