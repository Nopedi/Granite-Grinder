import tkinter as tk
from tkinter import ttk
import simplepyble
import sys
from bleak import uuids as uuid_util
import time
from tkinter import messagebox
import threading
import pygame
import configparser
import os


MODEL_SPEED_UUID = uuid_util.normalize_uuid_str("1111")
MODEL_STEP_UUID = uuid_util.normalize_uuid_str("1112")
MODEL_SLIDE_L_UUID = uuid_util.normalize_uuid_str("1116")
MODEL_SLIDE_R_UUID = uuid_util.normalize_uuid_str("1117")
MODEL_CAGE_UUID = uuid_util.normalize_uuid_str("1113")
MODEL_DRILL_UUID = uuid_util.normalize_uuid_str("1114")
MODEL_LED_UUID = uuid_util.normalize_uuid_str("1115")
MODEL_RESET_UUID = uuid_util.normalize_uuid_str("1118")

class GraniteGrinderGui:
    def __init__(self): 
        self.master = tk.Tk()
        self.master.title("Granite Grinder Gui")

        self.config = configparser.ConfigParser()
        if not os.path.exists("config.ini"):
            print('Could not load "config.ini", using default parameters')
            
            self.config["Params_Front"] = {
                "Speed": "25",
                "Step": "25",
                "R-Travel": "60",
                "L-Travel": "30",
            }
            
            self.config["Params_Back"] = {
                "Speed": "25",
                "Step": "25",
                "R-Travel": "60",
                "L-Travel": "30",
            }
            self.config["Params_Left"] = {
                "Speed": "25",
                "Step": "25",
                "R-Travel": "60",
                "L-Travel": "30",
            }
            self.config["Params_Right"] = {
                "Speed": "25",
                "Step": "25",
                "R-Travel": "60",
                "L-Travel": "30"
            }
            self.config["Params_Cage"] = {
                "Cage_Top":"150",
                "Cage_Bottom":"20"
            }
            with open("config.ini", "w") as configfile:
                self.config.write(configfile)
                print('Saved Default Config as "config.ini"')

        else:
            self.config.read("config.ini")
            print('"config.ini" loaded ')
        
        try:
            self.base_vals = [[
                self.config.getint("Params_Front","Speed"),
                self.config.getint("Params_Front","Step"),
                self.config.getint("Params_Front","R-Travel"),
                self.config.getint("Params_Front","L-Travel"),
            ],[
                self.config.getint("Params_Left","Speed"),
                self.config.getint("Params_Left","Step"),
                self.config.getint("Params_Left","R-Travel"),
                self.config.getint("Params_Left","L-Travel"),
            ],[
                self.config.getint("Params_Left","Speed"),
                self.config.getint("Params_Left","Step"),
                self.config.getint("Params_Left","R-Travel"),
                self.config.getint("Params_Left","L-Travel"),
            ],[
                self.config.getint("Params_Right","Speed"),
                self.config.getint("Params_Right","Step"),
                self.config.getint("Params_Right","R-Travel"),
                self.config.getint("Params_Right","L-Travel"),
            ]]
            self.cage_vals = [
                self.config.getint("Params_Cage","Cage_Top"),
                self.config.getint("Params_Cage","Cage_Bottom"),
            ]
        except configparser.NoSectionError as e:
            print("Problem with config file")
            print(e)

        labels_h = (
            "Speed",
            "Step",
            "R-Travel",
            "L-Travel",
            "Led-State",
            "Drill",
            "Cage"
        )

        labels_v = (
            "Forward",
            "Backward",
            "Right",
            "Left",
        )

        for i, label_text in enumerate(labels_h):
            label = ttk.Label(self.master, text=label_text)
            label.grid(row=0, column=i+1, padx=10, pady=5)
        
        for i, label_text in enumerate(labels_v):
            label = ttk.Label(self.master, text=label_text)
            label.grid(row=i+1, column=0, padx=10, pady=5)

        label_16 = ttk.Label(self.master, text="Min")
        label_16.grid(row=1, column=7, padx=10, pady=5)
        self.cage_min_val = tk.StringVar()
        cage_min_val_box = ttk.Entry(self.master, textvariable=self.cage_min_val)
        cage_min_val_box.grid(row=2, column=7, padx=10, pady=5)
        self.cage_min_val.set(self.cage_vals[1])

        label_36 = ttk.Label(self.master, text="Max")
        label_36.grid(row=3, column=7, padx=10, pady=5)
        self.cage_max_val = tk.StringVar()
        cage_max_val_box = ttk.Entry(self.master, textvariable=self.cage_max_val)
        cage_max_val_box.grid(row=4, column=7, padx=10, pady=5)
        self.cage_max_val.set(self.cage_vals[0])

        self.checkbox_led = tk.BooleanVar()
        checkbox_led = ttk.Checkbutton(self.master, text="", variable=self.checkbox_led)
        checkbox_led.grid(row=1, column=5, padx=10, pady=5, sticky="w")
        self.checkbox_led.set(False)

        self.checkbox_drill = tk.BooleanVar()
        checkbox_drill = ttk.Checkbutton(self.master, text="", variable=self.checkbox_drill)
        checkbox_drill.grid(row=1, column=6, padx=10, pady=5, sticky="w")
        self.checkbox_drill.set(False)

        self.entry_vars = [[tk.StringVar() for _ in range(4)],
                           [tk.StringVar() for _ in range(4)],
                           [tk.StringVar() for _ in range(4)],
                           [tk.StringVar() for _ in range(4)]]
        
        for i in range(1,5):
            for j in range(1,5):
                entry = ttk.Entry(self.master, textvariable=self.entry_vars[i-1][j-1])
                entry.grid(row=i, column=j, padx=10, pady=5)
                self.entry_vars[i-1][j-1].set(self.base_vals[i-1][j-1])

        save_button = ttk.Button(self.master, text="Save Config", command=self.save_config)
        save_button.grid(row=5, column=0, padx=10, pady=5)

        led_button = ttk.Button(self.master, text="Send Led", command=self.set_led)
        led_button.grid(row=5, column=5, padx=10, pady=5)

        drill_button = ttk.Button(self.master, text="Send Drill", command=self.set_drill)
        drill_button.grid(row=5, column=6, padx=10, pady=5)

        self.cage_state = True #open
        cage_button = ttk.Button(self.master, text="Switch Cage", command=self.cage)
        cage_button.grid(row=5, column=7, padx=10, pady=5)

        self.combo = ttk.Combobox(
            state="readonly",
            values=["Forward", "Backward", "Right", "Left"],
        )
        self.combo.grid(row=5, column=2, padx=10, pady=5)
        self.combo.set("Forward")
        
        send_button = ttk.Button(self.master, text="Send", command=self.send)
        send_button.grid(row=5, column=3, padx=10, pady=5)

        reset_button = ttk.Button(self.master, text="Reset", command=self.reset)
        reset_button.grid(row=5, column=4, padx=10, pady=5)

        """
        speed_button = ttk.Button(self.master, text=buttons[0], command=self.speed)
        speed_button.grid(row=4, column=0, padx=10, pady=5)

        step_button = ttk.Button(self.master, text=buttons[1], command=self.step)
        step_button.grid(row=4, column=1, padx=10, pady=5)

        slide_r_button = ttk.Button(self.master, text=buttons[2], command=self.slide_R)
        slide_r_button.grid(row=4, column=2, padx=10, pady=5)
        
        slide_l_button = ttk.Button(self.master, text=buttons[3], command=self.slide_L)
        slide_l_button.grid(row=4, column=3, padx=10, pady=5)

        cage_button = ttk.Button(self.master, text=buttons[4], command=self.cage)
        cage_button.grid(row=4, column=4, padx=10, pady=5)

        led_button = ttk.Button(self.master, text=buttons[5], command=self.set_led)
        led_button.grid(row=4, column=5, padx=10, pady=5)

        drill_button = ttk.Button(self.master, text=buttons[6], command=self.set_drill)
        drill_button.grid(row=4, column=6, padx=10, pady=5)

        reset_button = ttk.Button(self.master, text=buttons[7], command=self.reset)
        reset_button.grid(row=4, column=7, padx=10, pady=5)
        """
        do_ble = True
        if do_ble:
            adapters = simplepyble.Adapter.get_adapters()
            for i, adapter in enumerate(adapters):
                print(f"{i}: {adapter.identifier()} [{adapter.address()}]")
            if len(adapters) <= 1:
                adapter = adapters[0]
                print(f"Using Adapter: {adapter.identifier()}")

            adapter.scan_for(5000)
            peripherals = adapter.scan_get_results()

            for i, peripheral in enumerate(peripherals):
                print(f"{i}: {peripheral.identifier()} [{peripheral.address()}]")
                if peripheral.identifier() == "Granite Grinder":
                    self.Granite_Grinder = peripheral  
                    print("Found Granite Grinder Service")
                    break
            try:
                self.Granite_Grinder.connect()  
            except AttributeError:
                print("Could not connect to Granite Grinder")
                sys.exit()

            print("Successfully connected, listing services...")
            services = peripheral.services()
            service_characteristic_pair = []
            for service in services:
                for characteristic in service.characteristics():
                    service_characteristic_pair.append((service.uuid(), characteristic.uuid()))
                    self.service = service.uuid()

        pygame.init()
        pygame.joystick.init()
        joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        if len(joysticks) < 1:
            print("No Joystick detected")
        else:
            print("Joystick detected, selecting first")
            joystick_button = ttk.Button(self.master, text="Joystick", command=self._thread_starter)
            joystick_button.grid(row=5, column=1, padx=10, pady=5)
            self.joystick = joysticks[0]

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.master.mainloop()


    def save_config(self):
        self.config["Params_Front"] = {
                "Speed": self.entry_vars[0][0].get(),
                "Step": self.entry_vars[0][1].get(),
                "R-Travel": self.entry_vars[0][2].get(),
                "L-Travel": self.entry_vars[0][3].get(),
            }
        self.config["Params_Back"] = {
                "Speed": self.entry_vars[1][0].get(),
                "Step": self.entry_vars[1][1].get(),
                "R-Travel": self.entry_vars[1][2].get(),
                "L-Travel": self.entry_vars[1][3].get(),
            }
        self.config["Params_Left"] = {
                "Speed": self.entry_vars[2][0].get(),
                "Step": self.entry_vars[2][1].get(),
                "R-Travel": self.entry_vars[2][2].get(),
                "L-Travel": self.entry_vars[2][3].get(),
            }
        self.config["Params_Right"] = {
                "Speed": self.entry_vars[3][0].get(),
                "Step": self.entry_vars[3][1].get(),
                "R-Travel": self.entry_vars[3][2].get(),
                "L-Travel": self.entry_vars[3][3].get(),
            }
        self.config["Params_Cage"] = {
                "Cage_Top": self.cage_max_val.get(),
                "Cage_Bottom":self.cage_min_val.get()
            }
        with open("config.ini", "w") as configfile:
                self.config.write(configfile)
                print('Saved Default Config as "config.ini"')


    def _thread_starter(self):
        self.thread = threading.Thread(target=self.joystick_reader, daemon=True)
        self.use_joystick = True
        self.thread.start()
        
        messagebox.showinfo("Joystick", "Use Joystick for control")
        self.use_joystick = False
        self.thread.join()

    def joystick_reader(self):
        print("Using Joystick")
        old_drill_state = 0
        old_led_state = 0
        old_hat = (0,0)
        old_cage_val = 0

        while self.use_joystick:
            pygame.event.get()
            drill_state = self.joystick.get_button(0)
            if drill_state != old_drill_state:
                old_drill_state = drill_state
                self.checkbox_drill.set(drill_state)
                self.set_drill()
            
            led_state = self.joystick.get_button(1)
            if led_state != old_led_state:
                if self.checkbox_led.get() == old_led_state:
                    self.checkbox_led.set(True)
                else:
                    self.checkbox_led.set(False)
                old_led_state = led_state
                self.set_led()

            cage_val = self.joystick.get_button(2)
            if cage_val != old_cage_val:
                old_cage_val = cage_val
                if cage_val:
                    self.cage()

            hat = self.joystick.get_hat(0)
            if old_hat != hat:
                if hat == (0,1):
                    direction_select = 0
                    print("Forward")
                elif hat == (0,-1):
                    direction_select = 1
                    print("Backward")
                elif hat == (-1,0):
                    direction_select = 2
                    print("Left")
                elif hat == (1,0):
                    direction_select = 3
                    print("Right")
                else:
                    direction_select = 4
                    print("0 State")
                if direction_select != 4:
                    self.Granite_Grinder.write_request(self.service, MODEL_STEP_UUID, bytes(chr(int(self.entry_vars[direction_select][1].get())),'utf-8'))
                    self.Granite_Grinder.write_request(self.service, MODEL_SLIDE_L_UUID, bytes(chr(int(self.entry_vars[direction_select][3].get())),'utf-8'))
                    self.Granite_Grinder.write_request(self.service, MODEL_SLIDE_R_UUID, bytes(chr(int(self.entry_vars[direction_select][2].get())),'utf-8'))
                    self.Granite_Grinder.write_request(self.service, MODEL_SPEED_UUID, bytes(chr(int(self.entry_vars[direction_select][0].get())),'utf-8'))
                else:
                    self.reset()
                
                old_hat = hat
                print(hat)

            if self.joystick.get_button(3):
                self.reset()
                time.sleep(0.5)
                

            time.sleep(0.05)
                
        
    def on_closing(self):
            print("Disconnecting from Granite Grinder...")
            try:
                self.reset()
                self.Granite_Grinder.disconnect()
            except RuntimeError:
                print("Connection already terminated")
            print("Disconnected")
            print("Closing")
            self.master.destroy()

    """
    def slide_L(self):
        try:
            content = int(self.entry_vars[3].get())
            print(f"Sending Slide_L value: ({content})")
            self.Granite_Grinder.write_request(self.service, MODEL_SLIDE_L_UUID, bytes(chr(content),'utf-8'))
        except ValueError:
            print(f"{self.entry_vars[3].get()} can not be written")

    def slide_R(self):
        try:
            content = int(self.entry_vars[2].get())
            print(f"Sending Slide_R value: ({content})")
            self.Granite_Grinder.write_request(self.service, MODEL_SLIDE_R_UUID, bytes(chr(content),'utf-8'))
        except ValueError:
            print(f"{self.entry_vars[2].get()} can not be written")
    
    def speed(self):
        try:
            content = int(self.entry_vars[0].get())
            print(f"Sending Speed value: ({content})")
            self.Granite_Grinder.write_request(self.service, MODEL_SPEED_UUID, bytes(chr(content),'utf-8'))
        except ValueError:
            print(f"{self.entry_vars[0].get()} can not be written")

    def step(self):
        try:
            content = int(self.entry_vars[1].get())
            print(f"Sending Step value: ({content})")
            self.Granite_Grinder.write_request(self.service, MODEL_STEP_UUID, bytes(chr(content),'utf-8'))
        except ValueError:
            print(f"{self.entry_vars[1].get()} can not be written")
    """
    def set_led(self):
        content = self.checkbox_led.get()
        print(f"Sending Led value: ({content})")
        self.Granite_Grinder.write_request(self.service, MODEL_LED_UUID, bytes(chr(content),'utf-8'))

    def set_drill(self):
        content = self.checkbox_drill.get()
        print(f"Sending Led value: ({content})")
        self.Granite_Grinder.write_request(self.service, MODEL_DRILL_UUID, bytes(chr(content),'utf-8'))

    def cage(self):
        if self.cage_state:
            temp = self.cage_min_val
            self.cage_state = False
        else: 
            temp = self.cage_max_val
            self.cage_state = True
        try:
                content = int(temp.get())
                print(f"Sending Cage value: ({content})")
                self.Granite_Grinder.write_request(self.service, MODEL_CAGE_UUID, bytes(chr(content),'utf-8'))
        except ValueError:
            print(f"{temp.get()} can not be written")

    def reset(self):
        print(f"Resetting...")
        self.Granite_Grinder.write_request(self.service, MODEL_RESET_UUID, str.encode("1"))
        time.sleep(0.1)
        self.Granite_Grinder.write_request(self.service, MODEL_RESET_UUID, str.encode("0"))

    def send(self):
        try:
            direction_select = self.combo.current()
            print(f"Sending Step value: ({self.combo.get()})")
            self.Granite_Grinder.write_request(self.service, MODEL_STEP_UUID, bytes(chr(int(self.entry_vars[direction_select][1].get())),'utf-8'))
            self.Granite_Grinder.write_request(self.service, MODEL_SLIDE_L_UUID, bytes(chr(int(self.entry_vars[direction_select][3].get())),'utf-8'))
            self.Granite_Grinder.write_request(self.service, MODEL_SLIDE_R_UUID, bytes(chr(int(self.entry_vars[direction_select][2].get())),'utf-8'))
            self.Granite_Grinder.write_request(self.service, MODEL_SPEED_UUID, bytes(chr(int(self.entry_vars[direction_select][0].get())),'utf-8'))
        except ValueError:
            print(f"One Value from {self.combo.get()} not be written")

if __name__ == "__main__":
    GraniteGrinderGui()
