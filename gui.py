import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext
import requests
import json

class ChatApp:
    def __init__(self, root, LOCAL_IP, CLIENT_PORT):
        self.CLIENT_PORT = CLIENT_PORT
        self.url = f"http://{LOCAL_IP}:{self.CLIENT_PORT}"

        self.root = root
        self.root.title("WhatsApp-P2P")

        self.current_frame = None
        self.create_main_widgets()

    def create_main_widgets(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(padx=80, pady=80)

        self.info_label = tk.Label(self.main_frame, text="Bienvenido a WhatsApp-P2P", fg="blue", font=("Verdana", 12))
        self.info_label.grid(row=0, column=0, columnspan=2)

        self.nickname_label = tk.Label(self.main_frame, text="Nickname:")
        self.nickname_label.grid(row=1, column=0)
        self.nickname_entry = tk.Entry(self.main_frame)
        self.nickname_entry.grid(row=1, column=1)

        self.password_label = tk.Label(self.main_frame, text="Password:")
        self.password_label.grid(row=2, column=0)
        self.password_entry = tk.Entry(self.main_frame, show="*")
        self.password_entry.grid(row=2, column=1)

        self.register_button = tk.Button(self.main_frame, text="Register", command=self.register)
        self.register_button.grid(row=3, column=0)

        self.login_button = tk.Button(self.main_frame, text="Login", command=self.login)
        self.login_button.grid(row=3, column=1)

        self.current_frame = self.main_frame

    def switch_frame(self, new_frame):
        if self.current_frame is not None:
            self.current_frame.pack_forget()
        self.current_frame = new_frame
        self.current_frame.pack(padx=80, pady=80)

    def create_back_button(self, parent, command):
        back_button = tk.Button(parent, text="Back", command=command, fg="red")
        back_button.pack(anchor='nw', side='top', pady=5, padx=5)

    def register(self):
        nickname = self.nickname_entry.get()
        password = self.password_entry.get()
        url = f"{self.url}/Register"
        response = requests.post(url, params={"nickname": nickname, "password": password})
        messagebox.showinfo("Response", response.text)
        if response.text == '"You are logged"' or response.text == '"Register complete"':
            self.open_chats_window()

    def login(self):
        nickname = self.nickname_entry.get()
        password = self.password_entry.get()
        url = f"{self.url}/Login"
        response = requests.post(url, params={"nickname": nickname, "password": password})
        messagebox.showinfo("Response", response.text)
        if response.text == '"You are logged"' or response.text == '"Login Successful"':
            self.open_chats_window()


    def open_chats_window(self):
        self.chats_frame = tk.Frame(self.root)

        self.create_back_button(self.chats_frame, lambda: self.logout())  

        contacts_button = tk.Button(self.chats_frame, text="Contacts", command=self.open_contacts_window)
        contacts_button.pack(pady=10)

        self.switch_frame(self.chats_frame)
        self.get_chats()


    def logout(self):  
        url = f"{self.url}/Logout"
        response = requests.post(url)
        if response.status_code == 200:
            messagebox.showinfo("Response", response.text)
            self.switch_frame(self.main_frame)

    def open_contacts_window(self):
        self.contacts_frame = tk.Frame(self.root)

        self.create_back_button(self.contacts_frame, lambda: self.switch_frame(self.chats_frame))

        add_contact_button = tk.Button(self.contacts_frame, text="Add Contact", command=self.add_contact)
        add_contact_button.pack(pady=5)

        delete_contact_button = tk.Button(self.contacts_frame, text="Delete Contact", command=self.delete_contact)
        delete_contact_button.pack(pady=5)

        self.get_contacts()

        self.switch_frame(self.contacts_frame)


    def get_contacts(self):
        url = f"{self.url}/GetContacts"
        response = requests.get(url)
        if response.status_code == 200:
            contacts: dict = json.loads(response.text)
            for name, nickname in contacts.items():
                button = tk.Button(self.contacts_frame, text=name, command=lambda ch=nickname: self.open_chat_window(ch))
                button.pack(pady=5)
            

    def add_contact(self):
        name = simpledialog.askstring("Input", "Enter contact name:")
        nickname = simpledialog.askstring("Input", "Enter contact nickname:")
        url = f"{self.url}/AddContacts"
        response = requests.post(url, params={"name": name, "nickname": nickname})
        # messagebox.showinfo("Response", response.text)

    def delete_contact(self):
        name = simpledialog.askstring("Input", "Enter contact name to delete:")
        url = f"{self.url}/DeleteContacts"
        response = requests.post(url, params={"name": name})
        # messagebox.showinfo("Response", response.text)

    def get_chats(self):
        url = f"{self.url}/GetChats"
        response = requests.get(url)
        if response.status_code == 200:
            chats = json.loads(response.text)
            for chat in chats:
                button = tk.Button(self.chats_frame, text=chat, command=lambda ch=chat: self.open_chat_window(ch))
                button.pack(pady=5)

    def open_chat_window(self, chat):
        self.chat_frame = tk.Frame(self.root)
        
        self.create_back_button(self.chat_frame, lambda: self.switch_frame(self.chats_frame))

        messages = self.get_messages(chat)

        self.message_display = scrolledtext.ScrolledText(self.chat_frame, width=50, height=10)
        self.message_display.pack(pady=10)

        for i, message in enumerate(messages):
            if message and i % 2 == 0:
                self.message_display.insert(tk.END, message + "\n")

        # self.message_display.insert(tk.END, messages)
        self.message_display.config(state=tk.DISABLED)

        self.message_entry = tk.Entry(self.chat_frame, width=40)
        self.message_entry.pack(pady=5, side=tk.LEFT)

        send_button = tk.Button(self.chat_frame, text="Send", command=lambda: self.send_message(chat))
        send_button.pack(pady=5, side=tk.LEFT)

        self.switch_frame(self.chat_frame)

    def get_messages(self, nickname):
        url = f"{self.url}/GetMessages"
        response = requests.get(url, params={"nickname": nickname})
        if response.status_code == 200:
            return json.loads(response.text)
        return ""

    def send_message(self, user):
        message = self.message_entry.get()
        url = f"{self.url}/SendMessage"
        response = requests.post(url, params={"user": user, "message": message})
        # messagebox.showinfo("Response", response.text)
        if response.status_code == 200:
            self.message_display.config(state=tk.NORMAL)
            self.message_display.insert(tk.END, f"Me: {message}\n")
            self.message_display.config(state=tk.DISABLED)
            self.message_entry.delete(0, tk.END)


