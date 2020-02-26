#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""Raffle game with lot of variation and customization to fit most streamers"""
#---------------------------------------
# Libraries and references
#---------------------------------------
import codecs
import json
import os
import winsound
import ctypes
import random
import time
#---------------------------------------
# [Required] Script information
#---------------------------------------
ScriptName = "Raffle"
Website = "https://www.twitch.tv/generalpattonbs"
Creator = "GeneralRommel"
Version = "1.2"
Description = "Raffle minigame"
#---------------------------------------
# Variables
#---------------------------------------
settingsfile = os.path.join(os.path.dirname(__file__), "settings.json")
MessageBox = ctypes.windll.user32.MessageBoxW
MB_YES = 6
#---------------------------------------
# Classes
#---------------------------------------
class Settings:
    """" Loads settings from file if file is found if not uses default values"""

    # The 'default' variable names need to match UI_Config
    def __init__(self, settingsfile=None):
        if settingsfile and os.path.isfile(settingsfile):
            with codecs.open(settingsfile, encoding='utf-8-sig', mode='r') as f:
                self.__dict__ = json.load(f, encoding='utf-8-sig')

        else: #set variables if no custom settings file is found
            self.OnlyLive = False
            self.Command = "!raffle"
            self.JoinCommand = "!join"
            self.Permission = "Caster"
            self.PermissionInfo = ""
            self.Usage = "Stream Chat"
            self.BadInputMessage = "Inputs to the command have to be numbers. Bad input given."
            self.WinResponse = "{0} won {1} {3} and now has {2} {3}."
            self.MultiWinResponse = "{0} are the winners of the raffle! They each get {1} {2}."
            self.MultiNotEnoughEntryResponse = "Not enough players joined the raffle to have {0} winners. " \
                                               "Defaulting to one winner."
            self.StartResponse = "A raffle for {0} {1} has started! There will be {2} winner(s). Type !join to join."
            self.NoJoinResponse = "Nobody joined the raffle so nobody wins, try again another day."
            self.JoinMessage = "$user has joined the raffle."
            self.PermissionResp = "$user -> only $permission ($permissioninfo) and higher can use this command."
            self.RaffleTime = 30.0
            self.AllowMultiJoin = False

    # Reload settings on save through UI
    def Reload(self, data):
        """Reload settings on save through UI"""
        self.__dict__ = json.loads(data, encoding='utf-8-sig')

    def Save(self, settingsfile):
        """ Save settings contained within to .json and .js settings files. """
        try:
            with codecs.open(settingsfile, encoding="utf-8-sig", mode="w+") as f:
                json.dump(self.__dict__, f, encoding="utf-8", ensure_ascii=False)
            with codecs.open(settingsfile.replace("json", "js"), encoding="utf-8-sig", mode="w+") as f:
                f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8', ensure_ascii=False)))
        except ValueError:
            Parent.Log(ScriptName, "Failed to save settings to file.")

#---------------------------------------
# Settings functions
#---------------------------------------
def SetDefaults():
    """Set default settings function"""
    winsound.MessageBeep()
    returnValue = MessageBox(0, u"You are about to reset the settings, "
                                "are you sure you want to contine?"
                             , u"Reset settings file?", 4)
    if returnValue == MB_YES:
        returnValue = MessageBox(0, u"Settings successfully restored to default values"
                                 , u"Reset complete!", 0)
        global MySet
        Settings.Save(MySet, settingsfile)

def ReloadSettings(jsonData):
    """Reload settings on pressing the save button"""
    global MySet
    MySet.Reload(jsonData)

def SaveSettings():
    """Save settings on pressing the save button"""
    Settings.Save(MySet, settingsfile)

#---------------------------------------
# Optional functions
#---------------------------------------
def OpenReadMe():
    """Open the readme.txt in the scripts folder"""
    location = os.path.join(os.path.dirname(__file__), "README.txt")
    os.startfile(location)

def SendResp(data, Usage, Message):
    """Sends message to Stream or discord chat depending on settings"""
    Message = Message.replace("$user", data.UserName)
    Message = Message.replace("$currencyname", Parent.GetCurrencyName())
    Message = Message.replace("$target", data.GetParam(1))
    Message = Message.replace("$permissioninfo", MySet.PermissionInfo)
    Message = Message.replace("$permission", MySet.Permission)

    l = ["Stream Chat", "Chat Both", "All", "Stream Both"]
    if not data.IsFromDiscord() and (Usage in l) and not data.IsWhisper():
        Parent.SendStreamMessage(Message)

    l = ["Stream Whisper", "Whisper Both", "All", "Stream Both"]
    if not data.IsFromDiscord() and data.IsWhisper() and (Usage in l):
        Parent.SendStreamWhisper(data.User, Message)

    l = ["Discord Chat", "Chat Both", "All", "Discord Both"]
    if data.IsFromDiscord() and not data.IsWhisper() and (Usage in l):
        Parent.SendDiscordMessage(Message)

    l = ["Discord Whisper", "Whisper Both", "All", "Discord Both"]
    if data.IsFromDiscord() and data.IsWhisper() and (Usage in l):
        Parent.SendDiscordDM(data.User, Message)

#---------------------------------------
# [Required] functions
#---------------------------------------
def Init():
    """data on Load, required function"""
    global MySet
    MySet = Settings(settingsfile)

    if MySet.Usage == "Twitch Chat":
        MySet.Usage = "Stream Chat"
        Settings.Save(MySet, settingsfile)

    elif MySet.Usage == "Twitch Whisper":
        MySet.Usage = "Stream Whisper"
        Settings.Save(MySet, settingsfile)

    elif MySet.Usage == "Twitch Both":
        MySet.Usage = "Stream Both"
        Settings.Save(MySet, settingsfile)

    global State
    State = 0

    global JoinedPlayers
    JoinedPlayers = []

    global WinAmount
    WinAmount = 0

    global NumWinners
    NumWinners = 1

    global StartTime
    StartTime = None
    global StartData
    StartData = None

def Execute(data):
    """Required Execute data function"""
    global State
    global WinAmount
    global JoinedPlayers
    global StartTime
    global StartData
    global NumWinners

    if State == 0 and data.IsChatMessage() and data.GetParam(0).lower() == MySet.Command.lower():

        if not HasPermission(data):
            return

        if not MySet.OnlyLive or Parent.IsLive():
            State = 1
            WinAmount = data.GetParam(1)
            NumWinners = data.GetParam(2)

            try:
                WinAmount = int(WinAmount)

                # Default to 1 winner if not specified
                if NumWinners == "":
                    NumWinners = 1
                else:
                    NumWinners = int(NumWinners)
            except ValueError:
                State = 0
                message = MySet.BadInputMessage.format()
                SendResp(data, MySet.Usage, message)
                return

            message = MySet.StartResponse.format(WinAmount, Parent.GetCurrencyName(), NumWinners)
            SendResp(data, MySet.Usage, message)
            StartTime = time.time()
            StartData = data
            return

    if State == 1 and data.IsChatMessage() and data.GetParam(0).lower() == MySet.JoinCommand.lower():
        # If multi-join is not allowed check to see if the user has already joined and return
        if not MySet.AllowMultiJoin:
            for ExistingPlayer in JoinedPlayers:
                if ExistingPlayer.UserName.lower() == data.UserName.lower():
                    return

        # Append user to list of joined players
        JoinedPlayers.append(data)
        SendResp(data, MySet.Usage, MySet.JoinMessage)
        return
    return

def PickWinner(data):
    global State
    global JoinedPlayers
    global StartTime
    global WinAmount
    global NumWinners

    State = 0
    StartTime = None
    if not JoinedPlayers:
        SendResp(data, MySet.Usage, MySet.NoJoinResponse)
        return

    Random = random.WichmannHill()

    # Check to see if there are enough people for multiple winners, if not go to 1 winner
    if len(JoinedPlayers) < NumWinners:
        notEnoughPlayersMessage = MySet.MultiNotEnoughEntryResponse.format(NumWinners)
        NumWinners = 1
        SendResp(data, MySet.Usage, notEnoughPlayersMessage)

    # If there is one winner perform normal processing
    currency = Parent.GetCurrencyName()
    if NumWinners == 1:
        PickedPlayer = Random.choice(JoinedPlayers)
        Parent.AddPoints(PickedPlayer.User, PickedPlayer.UserName, WinAmount)
        points = Parent.GetPoints(PickedPlayer.User)
        winMessage = MySet.WinResponse.format(PickedPlayer.UserName, WinAmount, points, currency)
        SendResp(data, MySet.Usage, winMessage)
    else:
        winnersMessage = ""
        winners = []
        winAmountPerPlayer = WinAmount / NumWinners
        for x in range(NumWinners):
            PickedPlayer = Random.choice(JoinedPlayers)
            winnersMessage = winnersMessage + PickedPlayer.UserName + ","
            winners.append(PickedPlayer)
            Parent.AddPoints(PickedPlayer.User, PickedPlayer.UserName, winAmountPerPlayer)
            JoinedPlayers.remove(PickedPlayer)
        winnersMessage = winnersMessage[:-1]
        winMessage = MySet.MultiWinResponse.format(winnersMessage, winAmountPerPlayer, currency)
        SendResp(data, MySet.Usage, winMessage)

    JoinedPlayers = []
    return

def Tick():
    """Required tick function"""
    global StartTime
    global StartData

    if StartTime is not None:
        elapsedTime = time.time() - StartTime
        if elapsedTime > MySet.RaffleTime:
            PickWinner(StartData)

    return

def HasPermission(data):
    """Returns true if user has permission and false if user doesn't"""
    if not Parent.HasPermission(data.User, MySet.Permission, MySet.PermissionInfo):
        message = MySet.PermissionResp.format(data.UserName, MySet.Permission, MySet.PermissionInfo)
        SendResp(data, MySet.Usage, message)
        return False
    return True
