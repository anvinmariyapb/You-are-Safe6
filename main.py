from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from database_json import load_users, save_users,add_user
from database_json import verify_user  
from random import choice

import os
import re
import json

USER_DB_PATH = os.path.join("db", "users.json")

class GoBackButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = "Go Back"
        self.size_hint_y = None
        self.height = "40dp"
        self.bind(on_release=self.go_back)

    def go_back(self, instance):
        App.get_running_app().root.current = "login"
#====================================================

def verify_user(username, password):
    try:
        with open(USER_DB_PATH, 'r') as f:
            users = json.load(f)
    except FileNotFoundError:
        return False, "User database not found"

    if username in users and users[username]['password'] == password:
        return True, users[username]
    else:
        return False, None

def add_user(username, password, email):
    try:
        with open(USER_DB_PATH, 'r') as f:
            users = json.load(f)
    except FileNotFoundError:
        users = {}  # No file yet, start fresh

    if username in users:
        return False, "User already exists"

    users[username] = {
        "password": password,
        "email": email,
        "contacts": {}
    }

    with open(USER_DB_PATH, 'w') as f:
        json.dump(users, f, indent=4)

    return True, "User added successfully"

def load_users():
    if not os.path.exists(USER_DB_PATH):
        return {}
    with open(USER_DB_PATH, "r") as file:
        return json.load(file)

def save_users(users):
    with open(USER_DB_PATH, "w") as file:
        json.dump(users, file, indent=4)

def get_user_profile():
    username = App.get_running_app().current_user
    users = load_users()
    user = users.get(username)
    if user:
        return (
            user.get("username"),
            user.get("password"),
            user.get("email"),
            user.get("emergency_contact")
        )
    return None

def update_user_profile(password, email, emergency_contact):
    username = App.get_running_app().current_user
    users = load_users()
    if username in users:
        users[username]["password"] = password
        users[username]["email"] = email
        users[username]["emergency_contact"] = emergency_contact
        save_users(users)
        return True
    return False

#=======================================================

class LoginScreen(Screen):
    def login_user(self, username, password):
        success, user = verify_user(username, password)
        if success:
            App.get_running_app().current_user = username
            App.get_running_app().logged_in_username = username
            self.manager.current = 'profile'
            self.ids.login_message.text = ""
        else:
            self.ids.login_message.text = "Invalid username or password"

class SignUpScreen(Screen):
    def signup_user(self, username, password, email):
        error1 = self.validate_username(username)
        if error1:
            self.show_popup("Invalid username", error1)
            return
        error2 = self.validate_password(password)
        if error2:
            self.show_popup("Invalid Password", error2)
            return
        error3 = self.validate_email(email)
        if error3:
            self.show_popup("Invalid email", error3)
            return

        success, message = add_user(username, password, email)
        self.ids.signup_message.text = message
        if success:
            app = App.get_running_app()
            app.current_user = username
            app.logged_in_username = username
            self.manager.current = "login"
        
    def validate_username(self,username):
        if not username:
            return "Username cannot be empty."
        if len(username) < 6:
            return"Username must be at least 6 characters long."
        if  not re.match("[a-z0-9_]",username):
            return"Username should only have small letters,numbers and underscore "
        return None            
        
    def validate_password(self, password):
        if len(password) < 8:
            return "Password must be at least 8 characters long."
        if not re.search(r"[A-Z]", password):
            return "Password must contain at least one uppercase letter."
        if not re.search(r"[a-z]", password):
            return "Password must contain at least one lowercase letter."
        if not re.search(r"\d", password):
            return "Password must contain at least one number."
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return "Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)."
        if re.search(r"\s", password):
            return "Password must not contain spaces."
        return None  # Valid password
    
    def validate_email(self, email):
        if not email:
            return "Email cannot be empty."
        
        # Basic email regex pattern (regular expression)
        #just check if typed correct ie.,doesnot check the existence of that email
        pattern = r'^[a-z0-9]+@[a-z]+\.[a-z]+$'
        
        if not re.match(pattern, email):
            return "Invalid email format. Example: name@example.com"
        
        return None

    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.7, 0.3),
            auto_dismiss=True
        )
        popup.open()
        
class ContactCard(BoxLayout):
    contact = StringProperty('')
    code = StringProperty('')

    def send_secret(self):
        print(f" Sending secret code '{self.code}' to {self.contact}")
        
class HomeScreen(Screen):
    def on_enter(self):
        app = App.get_running_app()
        username = app.current_user
        try:
            self.ids.side_panel.username = username
            data = load_users()
        except Exception as e:
            print("Could not set side panel username:", e)
        

        try:
            contact_cards = self.ids.contact_cards
            contact_cards.clear_widgets()

            if username in data and "contacts" in data[username]:
                contacts = data[username]["contacts"]
                has_contacts = False

                for key in ["1", "2", "3"]:
                    number = contacts.get(key, {}).get("number", "")
                    code = contacts.get(key, {}).get("code", "")
                    if number:
                        card = ContactCard(contact=number, code=code)
                        contact_cards.add_widget(card)
                        has_contacts = True

                if not has_contacts:
                    contact_cards.add_widget(Label(text="No contacts saved yet.", color=(1, 1, 1, 1)))
            else:
                contact_cards.add_widget(Label(text="No contacts saved yet.", color=(1, 1, 1, 1)))

        except Exception as e:
            print("Error loading contact cards:", e)
    
SAFETY_QUOTES = [
    "“You are not alone. You are powerful. And you are protected.” ",
    "“Speak up. Stay strong. Safety is your right.”",
    "“Your voice can shatter silence. Be brave.” ",
    "“Safety isn’t optional. It’s essential.” ",
    "“Every woman deserves to feel safe. Always.” ",
]

class ProfileScreen(Screen):
 def on_enter(self):
    app = App.get_running_app()
    username = app.current_user  # 🔥 THIS is the missing line
    
    quote = choice(SAFETY_QUOTES)
    self.ids.safety_quote.text = quote
    
    try:
        self.ids.side_panel.username = username
        data = load_users()
    except Exception as e:
        print("Could not set side panel username:", e)

class SidePanel(BoxLayout):
    username = StringProperty("User")

    def on_kv_post(self, base_widget):
        app = App.get_running_app()
        if hasattr(app, 'logged_in_username'):
            self.username = app.logged_in_username
            app.bind(logged_in_username=self.update_username)

    def update_username(self, instance, value):
        self.username = value

class SettingsScreen(Screen):
    def save_settings(self, c1, code1, c2, code2, c3, code3):
        username = App.get_running_app().current_user
        data = load_users()

        if username:
            data.setdefault(username, {})["contacts"] = {
                "1": {"number": c1, "code": code1},
                "2": {"number": c2, "code": code2},
                "3": {"number": c3, "code": code3}
            }
            save_users(data)
            print("Emergency contacts updated!")

        self.manager.current = "home"
        home_screen = self.manager.get_screen("home")
        home_screen.on_enter()

    def on_pre_enter(self):  
        username = App.get_running_app().current_user
        data = load_users()

        if username in data:
            contacts = data[username].get("contacts", {})
            self.ids.contact1.text = contacts.get("1", {}).get("number", "")
            self.ids.code1.text = contacts.get("1", {}).get("code", "")
            self.ids.contact2.text = contacts.get("2", {}).get("number", "")
            self.ids.code2.text = contacts.get("2", {}).get("code", "")
            self.ids.contact3.text = contacts.get("3", {}).get("number", "")
            self.ids.code3.text = contacts.get("3", {}).get("code", "")

class ScreenManagement(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.history = []

    def switch_to(self, screen, **options):
        if self.current != screen.name:
            self.history.append(self.current)
        super().switch_to(screen, **options)

    def go_back(self):
        if self.history:
            previous = self.history.pop()
            self.current = previous
        else:
            # If no history, fallback to 'home'
            self.current = 'home'

class YouAreSafe(App):
    current_user = None
    logged_in_username = StringProperty("Guest")

    def build(self):
        Builder.load_file("kv/backbutton.kv")
        Builder.load_file("kv/screenmanager.kv")
        Builder.load_file("kv/login.kv")
        Builder.load_file("kv/signup.kv")
        Builder.load_file("kv/profile.kv")
        Builder.load_file("kv/home.kv")
        Builder.load_file("kv/sidepanel.kv")
        Builder.load_file("kv/settings.kv")
        Builder.load_file("kv/contactcard.kv")

        sm = ScreenManagement()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(SignUpScreen(name="signup"))
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(ProfileScreen(name="profile"))
        sm.add_widget(SettingsScreen(name="settings"))

        return sm

if __name__ == "__main__":
    YouAreSafe().run()