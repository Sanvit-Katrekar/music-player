import pygame
import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import askdirectory
import os
import threading
import time

pygame.init()
pygame.mixer.init()

def resourcePath(relativePath):
    ''' Get absolute path to resource, works for dev and for PyInstaller '''
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        basePath = sys._MEIPASS
    except Exception:
        basePath = os.path.abspath('Images')
    return os.path.join(basePath, relativePath)

class MusicPlayer:
    
    def __init__(self):
        self.window = tk.Tk()
        self.bgColour = 'deep sky blue'
        self.window.config(bg=self.bgColour)
        self.width = 800
        self.height = 825
        self.xOffset = 200
        self.yOffset = 10
        self.window.geometry(f'{self.width}x{self.height}+{self.xOffset}+{self.yOffset}')
        self.window.title('My music player!')
        self.iconPath = resourcePath('musicIcon.png')
        self.window.iconphoto(True, tk.PhotoImage(file=self.iconPath))
        self.window.protocol('WM_DELETE_WINDOW', self.onClose)
        self.fonts = [('Times New Roman', 30), ('Times New Roman', 20)]
        self.masterFrame = tk.Frame(self.window, bg=self.bgColour, padx=40, pady=20)
        self.masterFrame.pack(pady=30)

        self.shortcuts = {
            'Quit': 'q',
            'Restart': 'r',
            'Play': 'Enter/Return'
                          }

        self.window.bind(f"<KeyPress-{self.shortcuts['Quit']}>", self.onClose)
        self.window.bind('<Escape>', self.onClose)

        self.colours = [self.bgColour, 'red', 'green', 'royal blue', 'gold', 'orange']
        self.flashCount = 0
        self.currentSong = {}
        self.isFlash = tk.IntVar()
        self.isFlash.set(False)

        self.supportedExtensions = ('mp3', 'wav')
        self.directory = os.getcwd()

        self.paused = False
        self.autoplay = tk.IntVar()

        
    def clearWindow(self):
        for widget in self.masterFrame.winfo_children():
            widget.destroy()
            
    @staticmethod
    def clearFrame(frame):
        for widget in frame.winfo_children():
            widget.destroy()        
            
    @staticmethod
    def createImg(widget, imgName):
        img = tk.PhotoImage(file=imgName)
        widget.img = img
        widget.config(image=widget.img, text=' ', compound='c')

    def createButton(self, master, **kwargs):
        button = tk.Button(master, font=self.fonts[0])
        button.config(**kwargs)
        button.config(activebackground=button['bg'], activeforeground=button['fg'])
        return button
    
    def createLabel(self, master, **kwargs):
        label = tk.Label(master, font=self.fonts[0])
        label.config(**kwargs)
        return label

    def createCheckBtn(self, master, **kwargs):
        checkBtn = tk.Checkbutton(master, font=self.fonts[0])
        tk.Checkbutton(master, font=self.fonts[0], onvalue=1, offvalue=0)
        checkBtn.config(**kwargs)
        checkBtn.config(activebackground=checkBtn['bg'], activeforeground=checkBtn['fg'])
        return checkBtn
    
    def flashColours(self, parent):
        if not self.isFlash.get():
            parent['bg'] = self.bgColour
            return
        if self.flashCount >= len(self.colours):
            self.flashCount = 0
        parent.config(bg=self.colours[self.flashCount])
        parent.after(1000, lambda: self.flashColours(parent))
        self.flashCount += 1
        
    def menuScreen(self):
        self.createLabel(self.masterFrame, text='Music player!', padx=70, pady=10,
                         bg='orange', fg='red').pack()
        label = self.createLabel(self.masterFrame)
        self.createImg(label, resourcePath('music.png'))
        label.pack(pady=40)
        startBtn = self.createButton(self.masterFrame, text='Start!', fg='red', bg='gold',
                                     command=self.onStart, padx=50)
        startBtn.pack()

        self.flashColours(self.window)
        self.window.bind('<Return>', self.onStart)

    def mainWindow(self):
        self.titleLabel = self.createLabel(self.masterFrame, text='Music player!', bg='orange',
                                           fg='red', padx=70, pady=10)
        self.titleLabel.pack(pady=5)
        
        self.songTitleFrame = tk.Frame(self.masterFrame, bg='royal blue', padx=20, pady=10)
        self.songTitleFrame.columnconfigure(0, weight=1)
        self.songTitleFrame.columnconfigure(1, weight=2)
        
        self.createLabel(self.songTitleFrame, text='Now playing:', padx=20, pady=10,
                         fg='red', bg='gold').grid(row=0, column=0, sticky='w')
        self.songLabel = self.createLabel(self.songTitleFrame, text='–⁠', fg='red', bg='gold',
                                          pady=10)
        self.songLabel.grid(row=0, column=1, sticky='nsew', padx=10)
        self.songTitleFrame.pack(fill='x', pady=20)

        frame = tk.Frame(self.masterFrame, bg=self.bgColour)
        frame.columnconfigure((0, 1), weight=1)
        self.createButton(frame, text='\u27F3', bg='orange', fg='red',
                          command=self.onStart).grid(row=0, column=0)
        settingsBtn = self.createButton(frame, bg='orange', command=self.settings, pady=2)
        self.createImg(settingsBtn, resourcePath('settings.png'))
        settingsBtn.grid(row=0, column=1, padx=20)
        frame.pack(pady=10)

        self.songFrame = tk.LabelFrame(self.masterFrame, bg='aqua', fg='red', text='Songs',
                                       font=self.fonts[0]+('bold',), padx=10, pady=10)
        self.songFrame.pack(pady=5)

        buttonsFrame = tk.Frame(self.masterFrame, bg=self.bgColour)
        buttonsFrame.columnconfigure([i for i in range(4)], weight=1)
        playBtn = self.createButton(buttonsFrame, text='Play', bg='gold', fg='red',
                                    command=self.playSong)
        stopBtn = self.createButton(buttonsFrame, text='Stop', command=self.stop, bg='gold', fg='red')
        pauseBtn = self.createButton(buttonsFrame, text='Pause', command=self.pause, bg='gold', fg='red')
        unpauseBtn = self.createButton(buttonsFrame,text='Unpause', command=self.unpause, bg='gold', fg='red')
        playBtn.grid(row=0, column=0, padx=10)
        stopBtn.grid(row=0, column=1, padx=10)
        pauseBtn.grid(row=0, column=2, padx=10)
        unpauseBtn.grid(row=0, column=3, padx=10)
        buttonsFrame.pack(pady=25)
        
        selectBtn = self.createButton(self.masterFrame, text='Select song folder',
                                      fg='red', bg='orange', command=self.getSongs)
        selectBtn.pack(pady=5)

        self.window.bind(f"<KeyPress-{self.shortcuts['Restart']}>", self.onStart)
        self.window.bind('<Return>', self.play)

    def getSongs(self):
        self.autoplay.set(False)
        self.currentSong = {}
        self.stop()
        directory = askdirectory()
        self.clearFrame(self.songFrame)
        try:
            os.chdir(directory)
        except OSError:
            return
        try:
            songs = [song for song in os.listdir() if song.split('.')[1] in self.supportedExtensions]
        except IndexError:
            return
        lst = []
        maxSongs = 3
        for index, song in enumerate(songs):
            label = self.createLabel(self.songFrame, fg='red', font=self.fonts[1],
                                     bg='gold' if index%2 == 0 else 'deep sky blue')
            label.songName, label.extension = song.split('.')
            label['text'] = label.songName
            col, row = divmod(index, maxSongs)
            label.grid(row=row, column=col, sticky='we', padx=5, pady=5)
            label.bind('<Button-1>', lambda e, label=label: self.selectSong(label))
            lst.append(label)
            
        self.songList = list(zip(songs, lst))

    def selectSong(self, label):
        self.currentSong['fg'] = 'red'
        self.currentSong = label
        self.currentSong['fg'] = 'green'
        self.songLabel.config(text=self.currentSong['text'], width=len(self.currentSong['text']))
        
    def onStart(self, event=None):
        os.chdir(self.directory)
        self.stop()
        self.autoplay.set(False)
        self.window.unbind('<Return>')
        self.clearWindow()
        self.mainWindow()
        
    def onClose(self, event=None):
        if not messagebox.askyesno('Exit', 'Do you wish to quit?'):
            return
        self.autoplay.set(False)
        self.stop()
        self.window.destroy()

    def playSong(self):
        if not self.autoplay.get():
            self.play()
        else:
            self.autoPlayThread = threading.Thread(target=self.startAutoPlay, daemon=True)
            self.autoPlayThread.start()
            
    def play(self, event=None):
        if not self.currentSong:
            return
        song = '.'.join([self.currentSong.songName, self.currentSong.extension])
        pygame.mixer.music.load(song)
        pygame.mixer.music.play()
        
    def stop(self):
        self.currentSong['fg'] = 'red'
        self.currentSong = {}
        pygame.mixer.music.stop()

    def pause(self):
        self.paused = True
        pygame.mixer.music.pause()
        
    def unpause(self):
        self.paused = False
        pygame.mixer.music.unpause()

    def settings(self):
        if hasattr(self, 'settingsWindow'):
            self.settingsWindow.destroy()
        
        self.settingsWindow = tk.Toplevel(self.window, bg=self.bgColour)
        self.settingsWindow.wm_title('Settings')
        CHECKBTN_BG = 'orange'
        BUTTON_FG = 'red'
        CHECKBTN_BG1 = 'gold'
        BUTTON_FG = 'red'
        self.createLabel(self.settingsWindow, bg='orange', fg='red',
                         text='Settings', padx=50).pack(padx=100, pady=10)
        optionsFrame = tk.Frame(self.settingsWindow, bg=self.bgColour)
        options = {
            'Auto play': {'variable': self.autoplay},
            'Flashing background': {'variable': self.isFlash,
                                    'command': lambda: self.flashColours(self.window)}
                   }
        for index, option in enumerate(options.items()):
            checkBtn = self.createCheckBtn(optionsFrame, fg='red', text=option[0], font=self.fonts[1],
                                           bg='gold' if index%2 == 0 else 'green2', **option[1])
            checkBtn.grid(row=index, column=0, sticky='nsew', padx=5, pady=10)
        optionsFrame.pack()
        shortcutsFrame = tk.LabelFrame(self.settingsWindow, bg='light salmon', fg='red',
                                       text='Shortcuts', font=self.fonts[1]+('bold',),
                                       padx=20)
        for index, shortcut in enumerate(self.shortcuts.items()):
            action = self.createLabel(shortcutsFrame, fg='red', text=shortcut[0]+':', font=self.fonts[1],
                                      bg='gold' if index%2 == 0 else 'green2')
            label = self.createLabel(shortcutsFrame, fg='red', text=shortcut[1], font=self.fonts[1],
                                     bg='gold' if index%2 == 0 else 'green2')
            action.grid(row=index, column=0, sticky='nsew', padx=5, pady=10)
            label.grid(row=index, column=1, sticky='nsew', padx=5, pady=10)
        shortcutsFrame.pack()
        self.createButton(self.settingsWindow, bg='orange', fg='red', text='Done',
                          command=self.settingsWindow.destroy, font=self.fonts[1],
                          padx=15).pack(pady=10)

    def isBusy(self):
        return pygame.mixer.music.get_busy()
    
    def startAutoPlay(self):
        if not hasattr(self, 'songList'):
            return
        for song, songLabel in self.songList:
            self.selectSong(songLabel)
            self.play()
            time.sleep(1)
            #Loop to wait for song to finish
            while self.isBusy():
                if not self.autoplay.get():
                    return
        
    def run(self):
        self.menuScreen()
        self.window.mainloop()

class ScrollableFrame(tk.Frame):
    "Utility class that manages frames that can be scrolled and dynamically updates itself"
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

        # Create a frame inside a canvas, pack it to left
        # Create a vertical scrollbar, pack it to right
        self.canvas = tk.Canvas(self, bd=0, background=kwargs.get('bg', 'white'))
        self.frame = tk.Frame(self.canvas, background=kwargs.get('bg', 'white'))
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Places the frame on the canvas
        # Update scroll region when any event is fired
        self.canvas_frame = self.canvas.create_window((4,4), window=self.frame, anchor='nw')
        self.frame.bind('<Configure>', self.update_scrollbar)
        self.canvas.bind('<Configure>', self.resize_frame)
    
    def clear(self):
        "Deletes all items on the frame and resets the scrollbar"
        for child in self.frame.winfo_children():
            child.destroy()
    
        self.canvas.yview_moveto(0)

    def resize_frame(self, event):
        "Resize frame to canvas size"
        self.canvas.itemconfigure(self.canvas_frame, width=event.width)
    
    def update_scrollbar(self, _=None):
        "Update scroll region to cover whole canvas"
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.yview_moveto(1)


if __name__ == '__main__':
    musicPlayer = MusicPlayer()
    musicPlayer.run()
        
