import discord
import os
from datetime import datetime
from pytz import timezone
from replit import db
import numpy as np
import asyncio
from keep_alive import keep_alive

db.clear()
client = discord.Client()

#not used
def timeCompare(startHour, startMinute, stopHour, stopMinute):
  if startHour > stopHour:
    return False
  elif startHour < stopHour:
    return True
  else:
    if int(startMinute) <= int(stopMinute):
      return True
    else:
      return False

@client.event
async def hydrateMessage():
  PST = timezone("US/Pacific")
  while True:

    now = datetime.now(PST)

    current_time = now.strftime("%H:%M")
    if current_time[0:1] == "0":
      current_time = current_time[1:]

    print("Current Time =", current_time)
    if "on" in db.keys():
      print(db["on"])


    if "on" in db.keys() and db["on"] and "sendTimes" in db.keys() and current_time in db["sendTimes"]:
      waterChannel = client.get_channel(db["channel"])
      waterRole = waterChannel.guild.get_role(db["role"])
      await waterChannel.send("{a} Time to hydrate!".format(a = waterRole.mention))

    await asyncio.sleep(60)

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))
  client.loop.create_task(hydrateMessage())

@client.event
async def on_message(message):
  msg = message.content
  if message.author == client.user:
    return

  if msg.startswith('!setStart'):
    ampmIndex = max(msg.find("am"),msg.find("pm"))
    colonIndex = msg.find(":")

    if(msg[9:10] == ' ' and ampmIndex != -1 and colonIndex != -1 and colonIndex - 10 <= 2 and ampmIndex - colonIndex <= 3 and msg[10:colonIndex].isnumeric() and msg[colonIndex+1:ampmIndex].isnumeric()):

      startHour = int(msg[10:colonIndex])
      if msg[ampmIndex:] == "pm" and startHour != 12:
        startHour += 12
      if msg[ampmIndex:] == "am" and startHour == 12:
        startHour = 0
      db["startHour"] = startHour
      db["startMinute"] = msg[colonIndex+1:ampmIndex]
      await message.channel.send("Start time set at {h}:{m} PST.".format(h = db["startHour"], m = db["startMinute"]))

    else:
      await message.channel.send("Sorry, the correct use of this command is !setStart [hour]:[minutes][am/pm].")

  if msg.startswith('!setStop'):
    ampmIndex = max(msg.find("am"),msg.find("pm"))
    colonIndex = msg.find(":")

    if(msg[8:9] == ' ' and ampmIndex != -1 and colonIndex != -1 and colonIndex - 9 <= 2 and ampmIndex - colonIndex <= 3 and msg[9:colonIndex].isnumeric() and msg[colonIndex+1:ampmIndex].isnumeric()):

      stopHour = int(msg[9:colonIndex])
      if msg[ampmIndex:] == "pm" and stopHour != 12:
        stopHour += 12
      if msg[ampmIndex:] == "am" and stopHour == 12:
        stopHour = 0
      db["stopHour"] = stopHour
      db["stopMinute"] = msg[colonIndex+1:ampmIndex]
      await message.channel.send("Stop time set at {h}:{m} PST.".format(h = db["stopHour"], m = db["stopMinute"]))

    else:
      await message.channel.send("Sorry, the correct use of this command is !setStop [hour]:[minutes][am/pm].")

  if msg.startswith('!setInterval'):
    if(msg[12:13] == ' ' and msg[13:].isnumeric()):
      db["interval"] = int(msg[13:])
      await message.channel.send("Interval set at every {h} hour(s).".format(h = db["interval"]))
    else:
      await message.channel.send("Sorry, the correct use of this command is !setInterval [interval(in hours)].")

  if msg == "!waterStart":

    if "startHour" in db.keys() and "startMinute" in db.keys() and "stopHour" in db.keys() and "stopMinute" in db.keys() and "interval" in db.keys() and "channel" in db.keys() and "role" in db.keys():

      db["on"] = True

      sendTimes = np.array(["{h}:{m}".format(h = db["startHour"], m = db["startMinute"])])
      hourCursor = db["startHour"]+1
      while hourCursor != db["stopHour"]:
        sendTimes = np.append(sendTimes, "{h}:{m}".format(h = hourCursor, m = db["startMinute"]))
        hourCursor += 1
        if hourCursor == 24:
          hourCursor = 0
      if db["startMinute"] <= db["stopMinute"]:
        sendTimes = np.append(sendTimes, "{h}:{m}".format(h = hourCursor, m = db["startMinute"]))

      sendTimes = sendTimes[0::db["interval"]]
      print(sendTimes)
      db["sendTimes"] = sendTimes.tolist()

      await message.channel.send("Starting up!")

    else:
      missing = np.array([])
      if "startHour" not in db.keys():
        missing = np.append(missing,"Starting Time")
      if "stopHour" not in db.keys():
        missing = np.append(missing,"Stopping Time")
      if "interval" not in db.keys():
        missing = np.append(missing,"Interval")
      if "channel" not in db.keys():
        missing = np.append(missing,"Channel")
      if "role" not in db.keys():
        missing = np.append(missing,"Role")

      print(missing)
      await message.channel.send("Sorry, you need to set up the following information: {l}. Please set the info up using the !set commands.".format(l = missing))

  if msg == "!waterStop":
    db["on"] = False
    await message.channel.send("I am now off. Keep hydrating though!")
  
  if msg.startswith('!setChannel'):
    if msg[11:12] == ' ' and msg[14:len(msg)-1].isnumeric():
      db["channel"] = int(msg[14:len(msg)-1])
      waterChannel = client.get_channel(int(msg[14:len(msg)-1]))
      if waterChannel == None:
        await message.channel.send("Sorry, channel not found.")
      else: 
        await waterChannel.send("I will now remind you to hydrate in this channel!")
    else:
      await message.channel.send("Sorry, the correct use of this command is !setChannel #[channel name]. You either used the command wrong or did not input a valid channel name.")

  if msg.startswith('!setRole'):
    if msg[8:9] == ' ':
      db["role"] = int(msg[12:len(msg)-1])
      waterRole = message.guild.get_role(int(msg[12:len(msg)-1]))
      if waterRole == None:
        await message.channel.send("Sorry, role not found.")
      else: 
        await message.channel.send("I will now remind {a} to hydrate!".format(a = waterRole.mention))

    else:
      await message.channel.send("Sorry, the correct use of this command is !setRole @[role name]. You either used the command wrong or did not input a valid role name.")


      


keep_alive()
client.run(os.getenv('TOKEN'))
