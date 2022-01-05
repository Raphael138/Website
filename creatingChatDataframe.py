import sqlite3
import time 
import datetime
import json
import random

# This is used to create a new chat table following the chatName
def createChat(cursor, chatName):
    cursor.execute("CREATE TABLE IF NOT EXISTS "+chatName+" (time REAL, datestamp TEXT, sender TEXT, texts TEXT) ")

# This prints the list of all the existing chat tables, not used in the website
def getDBInfo(cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    for row in cursor.fetchall():
        print(row)

# This determines whether the chat table exists or not 
def chatExist(cursor, chatName):
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{chatName}'")
    if len(cursor.fetchall())==1:
        return True
    else:
        return False

# This outputs the dictionary form of the chat table
def getChatInfo(cursor, chatName):
    cursor.execute("SELECT time, datestamp, sender, texts FROM "+chatName)
    chatDict = []
    for row in cursor.fetchall():
        tempdict = {
            "time" : row[0],
            "time/date"  : row[1],
            "sender" : row[2],
            "content": row[3]
        }
        chatDict.append(tempdict)
    return chatDict

# This function is not used in the website but allows you to delete a chat table
def deleteChat(cursor, chatName):
    cursor.execute("DROP TABLE "+chatName)

# When someone is texted, add it to the chat table
def addToChat(cursor, connection, text, sender, chatName):
    date = str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    time1 = round(time.time(), 2)
    cursor.execute("INSERT INTO "+chatName+" (time, datestamp, sender, texts) VALUES (?, ?, ?, ?)",
            (time1, date, sender, text))
    connection.commit()

# When we write a message and post it, we have to add it to the database and to the current dictionary
def getPostText(cursor, connection, chatName, chatDict, sender, request):
    # Current text
    tempdict = {
        "time/date"  : datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "sender" : sender,
        "content": request.form['text']
    }
    chatDict.append(tempdict)
    addToChat(cursor, connection, tempdict['content'], sender, chatName)
    # Limiting the length of chats stored so database stays at a normal size
    if len(chatDict)>50:
        cursor.execute("DELETE FROM chat0 WHERE time= (SELECT MIN(time) FROM chat0)")
        connection.commit()