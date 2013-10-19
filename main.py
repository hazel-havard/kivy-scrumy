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
        mainScreen = ScrumApp.get_running_app().root.get_screen('main')
        mainScreen.refresh()
        self.manager.current = 'main'

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

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            mainScreen = ScrumApp.get_running_app().root.get_screen('main')
            mainScreen.selectedSticky = self
            if mainScreen.mode == 'view':
                self.background = (0, 0, 1, 1)
                mainScreen.showButtons()
            return True

class TitleLabel(Label):
    pass

class GridData(GridLayout):
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
                    elif story.name == newStoryName:
                        story.tasks.append(task)
                mainScreen.mode = 'view'
                return True
        return super(GridData, self).on_touch_up(touch)

class MainScreen(Screen):
    grid = ObjectProperty()
    buttonArea = ObjectProperty()
    stickies = ListProperty()
    selectedSticky = ObjectProperty()
    mode = StringProperty('view')

    oatTask = Task('make oatmeal', 'verify', 'wolf')
    eatTask = Task('eat grandma', 'in_progress', 'wolf')
    appleTask = Task('do not eat apple', 'to_do', 'wolf')
    wolfStory = Story('Big Bad Wolf', [oatTask, eatTask, appleTask])

    hairTask = Task('cut hair', 'verify', 'goldilocks')
    beTask = Task('break and enter', 'to_do', 'goldilocks')
    vandalizeTask = Task('vandalize', 'to_do', 'golidlocks')
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
            self.selectedSticky.parent.remove_widget(self.selectedSticky)
            self.stickies.remove(self.selectedSticky)

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
