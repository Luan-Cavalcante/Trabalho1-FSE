from gpiozero import Button
from signal import pause

def say_hello():
    print("Hello!")

button = Button(1,pull_up = False)

button.wait_for_press()
