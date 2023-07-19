from playsound import playsound
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import UserUtteranceReverted
from typing import Any, Text, Dict, List
import requests
import socket
import threading
import appliances_control as ac
import VolumeHandControl as vc



import subprocess

import psutil

def get_python_pid(script_name):
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if proc.info['name'] == 'python.exe' and len(proc.info['cmdline']) > 1 and script_name in proc.info['cmdline'][1]:
            return proc.info['pid']
    return None

def stop_task_by_pid(pid):
    try:
        process = psutil.Process(pid)
        process.terminate()
        print(f"Successfully stopped task with PID: {pid}")
    except psutil.NoSuchProcess:
        print(f"No running task found with PID: {pid}")






def play_song():
    playsound('new.mp3')



def volume_control():
    vc.main()

def gesture_control():
    ac.main()

t1 = threading.Thread(target=play_song)
t2 = threading.Thread(target=volume_control)
t3 = threading.Thread(target=gesture_control)



dictionary = {
    "room": 0,
    "kitchen": 1,
    "compound": 2,
    "toilet": 3,
    "socket": 4,
    "step": 7,
    "balcony": 5,
    "shower": 6
}

lights = [0, 1, 2, 3, 4, 5, 6, 7]

ip = "192.168.224.52"
port = 80


class ActionControlAppliance(Action):

    def name(self) -> Text:
        return "action_control_appliance"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        status = tracker.get_slot('status').replace("'", "").replace(" ", "").lower()
        location = tracker.get_slot('location').replace("'", "").replace(" ", "").lower()
        print(f'This is the {location}')
        msg = ""
        if 'all' in location and status == "on":
            for light in lights:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((ip, port))
                s.send(f"{light},1".encode())
                s.close()
            msg = "I have turned on all the lights"
        elif 'all' in location and status == "off":
            for light in lights:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((ip, port))
                s.send(f"{light},0".encode())
                s.close()
            msg = "I have turned off all the lights"

        elif location == 'socket' and status == "off":
            value = dictionary['socket']
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
            s.send(f"{value},0".encode())
            s.close()
            msg = "I have turned off the sockets"

        elif location == 'socket' and status == "on":
            value = dictionary['socket']
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
            s.send(f"{value},1".encode())
            s.close()
            msg = "I have turned on the socket"

        elif location != "all" and status == "off":
            value = dictionary[location]
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
            s.send(f"{value},0".encode())
            s.close()
            msg = f"I have turned off the {location} light"
        elif location != "all" and status == "on":
            value = dictionary[location]
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
            s.send(f"{value},1".encode())
            s.close()
            msg = f"I have turned on the {location} light"
        else:
            msg = "Error in turning on the lights, please check your internet connection properly"
        dispatcher.utter_message(text=msg)
        return []

class ActionResetSlots(Action):

    def name(self):
        return "action_reset_slots"

    def run(self, dispatcher, tracker, domain):
        return [SlotSet("status", None),
                SlotSet("location", None),
                ]


class ActionDefaultFallback(Action):
    """Executes the fallback action and goes back to the previous state
    of the dialogue"""

    def name(self) -> Text:
        return "action_default_fallback"

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(template="my_custom_fallback_template")

        # Revert user message which led to fallback.
        return [UserUtteranceReverted()]


class ValidateGestureControlForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_gesture_control_form"

    def validate_password(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validates value of 'password' slot"""
        return {"password": slot_value}

class ActionGestureControl(Action):
    """Gesture Control"""

    def name(self) -> Text:
        """Unique identifier of the action"""
        return "action_gesture_control"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        password = tracker.get_slot("password").replace("'", "").replace(" ", "")
        if 'automation' in password:
            t3.start()
            t3.join()
            msg = "Thank you. Gesture Control Enabled"
        else:
            msg = "Authentication failed, reversing to safe state"

        dispatcher.utter_message(text=msg)
        return []


class ActionDisableGestureControl(Action):

    def name(self) -> Text:
        return "action_disable_gesture_control"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        pid = get_python_pid("appliances_control.py")
        pid2 = get_python_pid("VolumeHandControl.py")
        stop_task_by_pid(pid)
        stop_task_by_pid(pid2)
        msg = "Successfully disabled gesture control"
        dispatcher.utter_message(text=msg)
        return []

class ActionPlayMusic(Action):

    def name(self) -> Text:
        return "action_play_music"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        msg = "Playing Nice Music"
        t1.start()
        t2.start()
        t2.join()
        dispatcher.utter_message(text=msg)
        return []

