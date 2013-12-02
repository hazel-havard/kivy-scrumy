import kivy
kivy.require('1.7.1')

from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty, ListProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout 
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from base64 import b64encode
from httplib import HTTPSConnection
import json

class Story():
    def __init__(self, name, taskList):
        self.name = name
        self.tasks = taskList

class Task():
    def __init__(self, name, status, person, id):
        self.name = name
        self.status = status
        self.person = person
        self.id = id

class LoginScreen(Screen):
    scrumIdInput = ObjectProperty()
    passwordInput = ObjectProperty()
    
    def login(self):
        username = self.scrumIdInput.text
        password = self.passwordInput.text
        conn = HTTPSConnection('scrumy.com')
        rawLogin = b"%s:%s" % (username, password)
        loginInfo = b64encode(rawLogin).decode("ascii")
        headers = {'Authorization': 'Basic %s' % loginInfo}
        conn.request('GET', '/api/scrumies/%s' % username, headers=headers)
        response = conn.getresponse()
        conn.close()
        if response.status == 200:
            mainScreen = ScrumApp.get_running_app().root.get_screen('main')
            mainScreen.username = username
            mainScreen.headers = headers
            mainScreen.refresh()
            self.manager.current = 'main'
        else:
            print("error: could not authenticate")

class TaskNameLabel(Label):
    pass

class TaskPersonLabel(Label):
    pass

class TaskNameInput(TextInput):
    def save(self):
        self.parent.task.name = self.text

class TaskPersonInput(TextInput):
    def save(self):
        self.parent.task.person = self.text

class StickyNote(BoxLayout):
    background = ObjectProperty((1, 0, 0, 1))
    task = ObjectProperty()
    def __init__(self, task, **kwargs):
        self.task = task
        super(StickyNote, self).__init__()

    # Select the sticky being touched if in view mode
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            mainScreen = ScrumApp.get_running_app().root.get_screen('main')
            if mainScreen.mode == 'view':
                mainScreen.selectedSticky = self
                self.background = (0, 0, 1, 1)
                mainScreen.showButtons()
            return True

class TitleLabel(Label):
    pass

class GridData(GridLayout):
    # handle moving stickies if in move mode
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            mainScreen = ScrumApp.get_running_app().root.get_screen('main')
            if mainScreen.mode == 'move':
                parent = mainScreen.selectedSticky.parent
                oldStoryName = parent.id[:parent.id.index('_')]
                parent.remove_widget(mainScreen.selectedSticky)
                self.add_widget(mainScreen.selectedSticky)
                task = mainScreen.selectedSticky.task
                task.status = self.id[self.id.index('_') + 1:]
                newStoryName = self.id[:self.id.index('_')]
                for story in mainScreen.stories:
                    if story.name == oldStoryName:
                        story.tasks.remove(task)
                for story in mainScreen.stories:
                    if story.name == newStoryName:
                        story.tasks.append(task)
                mainScreen.mode = 'view'
                return True
        return super(GridData, self).on_touch_up(touch)

class MainScreen(Screen):
    grid = ObjectProperty()
    buttonArea = ObjectProperty()
    stickies = ListProperty()
    selectedSticky = ObjectProperty()
    # current screen mode can be view, edit, or move
    mode = StringProperty('view')

    stories = []

    def refresh(self):
        conn = HTTPSConnection('scrumy.com')
        conn.request('GET', '/api/scrumies/%s/sprints/current.json' % self.username, headers=self.headers)
        response = conn.getresponse()
        if response.status != 200:
            print('Error:server responded %s: %s' % (response.status, response.reason))
            conn.close()
            return
        scrumJSON = response.read()
        conn.close()
        scrum = json.loads(scrumJSON)
        sprint = scrum['sprint']
        stories = []
        for rawStory in sprint['stories']:
            story = Story(rawStory['story']['title'], [])
            for rawTask in rawStory['story']['tasks']:
                task = Task(rawTask['task']['title'], rawTask['task']['state'], \
                        rawTask['task']['scrumer']['name'], rawTask['task']['id'])
                story.tasks.append(task)
            stories.append(story)
        self.stories = stories
        self.drawGrid()


    def drawGrid(self):
        self.grid.clear_widgets()
        self.grid.add_widget(TitleLabel(text='Stories'))
        self.grid.add_widget(TitleLabel(text='To Do'))
        self.grid.add_widget(TitleLabel(text='In Progress'))
        self.grid.add_widget(TitleLabel(text='Verify'))
        self.grid.add_widget(TitleLabel(text='Completed'))
        for story in self.stories:
            self.grid.add_widget(TitleLabel(text=story.name))
            todo = GridData(id=story.name + "_" + "todo")
            self.grid.add_widget(todo)
            inprogress = GridData(id=story.name + "_" + "inprogress")
            self.grid.add_widget(inprogress)
            verify = GridData(id=story.name + "_" + "verify")
            self.grid.add_widget(verify)
            done = GridData(id=story.name + "_" + "done")
            self.grid.add_widget(done)
            for task in story.tasks:
                if task.status == 'todo':
                    cell = todo
                elif task.status == 'inprogress':
                    cell = inprogress
                elif task.status == 'verify':
                    cell = verify
                elif task.status == 'done':
                    cell = done
                sticky = StickyNote(task)
                self.stickies.append(sticky)
                cell.add_widget(sticky)

    def edit(self, instance):
        self.mode = 'edit'
        self.selectedSticky.clear_widgets()
        self.selectedSticky.add_widget(TaskNameInput(text = self.selectedSticky.task.name))
        self.selectedSticky.add_widget(TaskPersonInput(text = self.selectedSticky.task.person))

    def exitEdit(self):
        self.mode = 'view'
        self.selectedSticky.clear_widgets()
        self.selectedSticky.add_widget(TaskNameLabel(text = self.selectedSticky.task.name))
        self.selectedSticky.add_widget(TaskPersonLabel(text = self.selectedSticky.task.person))

    def delete(self, instance):
        if self.selectedSticky.parent is not None:
            conn = HTTPSConnection('scrumy.com')
            conn.request('DELETE', '/api/tasks/%s' % self.selectedSticky.task.id, headers=self.headers)
            response = conn.getresponse()
            conn.close()
            if response.status != 200:
                print('Error: Delete response was %s %s' % (response.status, response.reason))
                return
            self.refresh()

    # guts of move handled by GridData class
    def move(self, instance):
        self.mode = 'move'

    def showButtons(self):
        editButton = Button(text='edit', on_press=self.edit)
        deleteButton = Button(text='delete', on_press=self.delete)
        moveButton = Button(text='move', on_press=self.move)
        self.buttonArea.add_widget(editButton)
        self.buttonArea.add_widget(deleteButton)
        self.buttonArea.add_widget(moveButton)

    def on_touch_up(self, touch):
        if self.grid.collide_point(*touch.pos):
            for sticky in self.stickies:
                sticky.background = (1, 0, 0, 1)
            self.buttonArea.clear_widgets()
            if self.mode == 'edit' and not self.selectedSticky.collide_point(*touch.pos):
                self.exitEdit()
        super(MainScreen, self).on_touch_up(touch)

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
