from tkinter import *
import time
from random import randint
import threading

root = Tk()

root.title("Learn To Code at Codemy.com")
root.geometry("500x400")

def update_var(text_value):
    time.sleep(5)
    text_value = 'After update'
    print('ran update_var')
    print(text_value)
    return text_value


def print_label(text_value):
    print(text_value)

text_value = 'Button has been pressed before update'
print(text_value)
text_value = threading.Thread(target=update_var, args=(text_value,)).start()
print(text_value)


my_label_1 = Label(root, text='Press to print text')
my_label_1.pack(pady=20)
my_label_1.bind('<Button-1>', lambda e: print_label(text_value))




root.mainloop()

'''
What I want:
1. Create a function that prints text when I press the button
2. In another thread, wait for 5 secs then change the text
3. Press button again and see what happens

'''