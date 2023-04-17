# This is a sample Python script.
import csv
import os

import firebase_admin
from firebase_admin import storage, credentials
from sympy.strategies.core import switch

import manager



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    cred = credentials.Certificate("./key.json")
    app = firebase_admin.initialize_app(cred, {'storageBucket': 'final-project-cb673.appspot.com'})
    loop = True
    renamed = False
    while loop is not False:
        dig = input("\nchoose what to start\n"
                    "1 - Start program\n"
                    "2 - exit\n")
        if dig == '1':
            address = input("Please enter destination address \n")
            manager.manager(address)
            # manager.manager("1151 Centre Street Southeast, Calgary AB T2G Calgary Alberta Canada")
            # manager.manager("263 McLeod Street, Ottawa ON K2P 1A1 Ottawa Ontario Canada")
        elif dig == '2':
            print("Thanks for using our system. \nTal Cohen - 208687913\nDan Carvajel - 216510511")
            loop = False



        # rename imgs for testing (they will uoload to the server)
        # elif dig == '3':
        #      pics_path = input("Please enter picture path: \n")
        #      renamed = manager.rename_jpg_files('Searching_for_parking.csv', pics_path)
        #      renamed = manager.rename_jpg_files('Searching_for_parking.csv', 'C:/Users/talco/Desktop/parking')

