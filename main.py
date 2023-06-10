# This is a sample Python script.
import csv
import os

import firebase_admin
import telebot as telebot
from firebase_admin import storage, credentials
from sympy.strategies.core import switch

import APIs
import manager

#for the bot
Telegram_Bot_API_TOKEN = APIs.Telegram_Bot_API_TOKEN

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    cred = credentials.Certificate("./key.json")
    app = firebase_admin.initialize_app(cred, {'storageBucket': 'final-project-cb673.appspot.com'})

    # If you want to use it with console:

    # loop = True
    # renamed = False
    # while loop is not False:
    #     dig = input("\nchoose what to start\n"
    #                 "1 - Start program\n"
    #                 "2 - exit\n")
    #     if dig == '1':
    #         address = input("Please enter destination address \n")
    #         manager.manager(address)
    #         # manager.manager("1151 Centre Street Southeast, Calgary AB T2G Calgary Alberta Canada")
    #         # manager.manager("263 McLeod Street, Ottawa ON K2P 1A1 Ottawa Ontario Canada")
    #     elif dig == '2':
    #         print("Thanks for using our system. \nTal Cohen - 208687913\nDan Carvajel - 216510511")
    #         loop = False
    # rename imgs for testing (they will uoload to the server)
    # elif dig == '3':
    #      pics_path = input("Please enter picture path: \n")
    #      renamed = manager.rename_jpg_files('Searching_for_parking.csv', pics_path)
    #      renamed = manager.rename_jpg_files('Searching_for_parking.csv', 'C:/Users/talco/Desktop/parking')




    # For using the project with the telegram bot only:

    bot = telebot.TeleBot(Telegram_Bot_API_TOKEN)

    @bot.message_handler(commands=["start"])
    def start(message):
        bot.send_message(message.chat.id, "Hello! I am the telegram bot. \nTo get started - send an address:")

        @bot.message_handler(func=lambda message: message.text.startswith("address: "))
        def greet(message):
            address_from_bot = message.text[9:]
            bot.send_message(message.chat.id, "We are searchig for the best parking for you..... Please wait.  ")
            bot.send_animation(message.chat.id, "https://media.tenor.com/7NX24XoJX0MAAAAM/loading-fast.gif")
            text = "The best parking for you available in: "+ str(manager.manager(address_from_bot))
            bot.send_message(message.chat.id, text)

    bot.polling()










