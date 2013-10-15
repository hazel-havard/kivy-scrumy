import kivy
kivy.require('1.7.1')

from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout 
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

class Story():
    def __init__(self, name, taskList):
        self.name = name
        self.tasks = taskList

class Task():
    def __init__(self, name, status, person):
        self.name = name
        self.status = status
        self.person = person

class LoginScreen(Screen):
    scrumIdInput = ObjectProperty()
    passwordInput = ObjectProperty()
    
    def login(self):
        print("login: " + self.scrumIdInput.text + ", password: " + self.passwordInput.text)
        main_screen = ScrumApp.get_running_app().root.get_screen('main')
        main_screen.refresh()
        self.manager.current = 'main'
        
class StickyNote(BoxLayout):
    name = StringProperty()
    person = StringProperty()
    def __init__(self, name, person, **kwargs):
        super(StickyNote, self).__init__()
        self.name = name
        self.person = person

class TitleLabel(Label):
    pass

class GridData(GridLayout):
    pass

class MainScreen(Screen):
    grid = ObjectProperty()

    oatTask = Task('make oatmeal', 'verify', 'wolf')
    eatTask = Task('eat grandma', 'in_progress', 'wolf')
    appleTask = Task('do not eat apple', 'to_do', 'wolf')
    wolfStory = Story('Big Bad Wolf', [oatTask, eatTask, appleTask])

    hairTask = Task('cut hair', 'verify', 'goldilocks')
    beTask = Task('break and enter', 'to_do', 'goldilocks')
    vandalizeTask = Task('valdalize', 'to_do', 'golidlocks')
    goldStory = Story('Goldilocks', [hairTask, beTask, vandalizeTask])

    stories = [wolfStory, goldStory]

    def refresh(self):
        for story in self.stories:
            self.grid.add_widget(TitleLabel(text=story.name))
            to_do = GridData(id=story.name + "_" + "to_do")
            self.grid.add_widget(to_do)
            in_progress = GridData(id=story.name + "_" + "in_progress")
            self.grid.add_widget(in_progress)
            verify = GridData(id=story.name + "_" + "verify")
            self.grid.add_widget(verify)
            done = GridData(id=story.name + "_" + "done")
            self.grid.add_widget(done)
            for task in story.tasks:
                if task.status == 'to_do':
                    cell = to_do
                elif task.status == 'in_progress':
                    cell = in_progress
                elif task.status == 'verify':
                    cell = verify
                elif task.status == 'done':
                    cell = done
                cell.add_widget(StickyNote(task.name, task.person))

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
