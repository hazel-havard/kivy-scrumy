import kivy
kivy.require('1.7.1')

from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout 
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

class LoginScreen(Screen):
    scrumIdInput = ObjectProperty()
    passwordInput = ObjectProperty()
    
    def login(self):
        print("login: " + self.scrumIdInput.text + ", password: " + self.passwordInput.text)
        self.manager.current = 'main'
        
class StickyNote(BoxLayout):
	pass

class TitleLabel(Label):
    pass

class GridData(GridLayout):
    pass

class MainScreen(Screen):
    pass

class ScrumScreenManager(ScreenManager):
    pass

class ScrumApp(App):
    
    def build(self):
        manager = ScrumScreenManager()
        manager.add_widget(LoginScreen(name='login'))
        manager.add_widget(MainScreen(name='main'))
        return manager

if __name__ == '__main__':
    ScrumApp().run()
