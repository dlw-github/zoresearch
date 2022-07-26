from threading import Thread
import time
from tkinter import *

# all threads can access this global variable

def update_data():
    global database_value # needed to modify the global value
    global dummy
    
    # get a local copy (simulate data retrieving)
    # local_copy = database_value
        
    # simulate some modifying operation
    time.sleep(5)
    database_value = "MODIFIED"
    dummy = True
        
    # write the calculated new value into the global variable
    # database_value = local_copy


def print_data(database_value, dummy):
    print(f'Dummy: {dummy}')
    print(f'Value: {database_value}')
    print()

if __name__ == "__main__":

    dummy = False
    database_value = 'INITIAL'

    # print('BEFORE:')
    # print_data(database_value, dummy)

    # Start background thread
    t1 = Thread(target=update_data)
    t1.start()

    # Set up TKinter GUI
    root = Tk()
    root.title("Testo")
    root.geometry("500x400")

    # Add button
    my_label_1 = Label(root, text='TESTO') 
    my_label_1.bind('<Button-1>', lambda e: print_data(database_value, dummy))
    my_label_1.pack(pady=20)
   
    # Run GUI
    root.mainloop()

    # Have thread join
    # t1.join()
    # print('\nAFTER:')
    # print_data(database_value, dummy)
