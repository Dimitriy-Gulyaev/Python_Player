import random
from tkinter import *
from tkinter.filedialog import askdirectory
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
from tkinter import simpledialog
import os
import pygame
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
import wckToolTips

root = Tk()
root.title("Player")
root.geometry("220x463+200+200")
root.configure(background='white')
root.resizable(0, 0)

# Просто изображение для красоты
photo_bear = PhotoImage(file="./assets/images/small_bear.png")
bear = Label(image=photo_bear, background='white')
bear.grid(row=3, column=0, sticky=NW, columnspan=5)

pygame.mixer.init()

list_of_songs = []  # Список с названиями файлов песен для загрузки
real_names = []  # Список реальных названий композиций для отображения в окне плеера

index = 0  # Номер трека в списке для загрузки текущего трека
song_name = StringVar()  # Название трека


# Выбор папки с музыкой, вызывается кнопкой open
def manage_playlist(one_file_flag, adding=False, loading=False, filenames=None):
    global index
    global list_of_songs
    global real_names
    global current_track_time

    if not adding:
        list_of_songs = []
        real_names = []
        index = 0
        current_track_time = 0
        time_var.set(current_track_time)

    if not loading:
        filenames = []
        if one_file_flag:
            name = askopenfilename()
            if name.endswith("mp3"):
                filenames.append(name)
        else:
            directory = askdirectory()
            if directory == '':
                return
            os.chdir(directory)
            for name in os.listdir(directory):
                if name.endswith("mp3"):
                    filenames.append(name)

    if len(filenames) == 0:
        return

    for name in filenames:
        # Составление списка реальных названий композиций
        real_path = os.path.realpath(name)
        audio = ID3(real_path)
        real_names.insert(len(list_of_songs), audio['TIT2'].text[0])

        # Составление списка имён музыкальных файлов
        list_of_songs.append(name)

    if not adding:
        pygame.mixer.music.load(list_of_songs[index])
        pygame.mixer.music.stop()
        pygame.mixer.music.play()
        update_label()

    change_playlist()


def change_playlist():
    playlist.delete(0, 'end')
    real_names.reverse()

    for items in real_names:
        playlist.insert(0, items)

    real_names.reverse()


playlist_label = Label(text="Playlist:")
playlist_label.grid(row=6, column=0, columnspan=2, sticky=NW, pady=5)
playlist = Listbox(master=root, selectmode=SINGLE, width=35)
playlist.grid(row=7, column=0, columnspan=5, sticky=NW)


def delete_position():
    global index

    song_to_delete = playlist.get(playlist.curselection())
    ind = real_names.index(song_to_delete)
    del real_names[ind]
    del list_of_songs[ind]
    old_index = index

    if ind <= old_index:
        index -= 1
    if ind == old_index:
        next_song()

    update_label()
    change_playlist()


delete_from_playlist = Button(master=root, command=delete_position, text="Remove")
delete_from_playlist.grid(row=8, column=0, columnspan=2, sticky=NW)
wckToolTips.register(delete_from_playlist, "Remove selected track from playlist")


def play_position():
    global index

    song_to_play = playlist.get(playlist.curselection())
    index = real_names.index(song_to_play)
    stop_song()
    pygame.mixer.music.load(list_of_songs[index])
    play_song()


play_element = Button(master=root, command=play_position, text="Play")
play_element.grid(row=8, column=4, sticky=NE)
wckToolTips.register(play_element, "Play the selected track")


def open_folder():
    manage_playlist(False, False)


def open_file():
    manage_playlist(True, False)


def add_folder():
    manage_playlist(False, True)


def add_file():
    manage_playlist(True, True)


# Кнопка открытия папки с файлами
photo_open_file = PhotoImage(file="./assets/buttons/open.png")
open_menu = Menubutton(master=root, image=photo_open_file, bd=0, bg="white")
open_menu.grid(row=0, column=0, sticky=NW, padx=3)
wckToolTips.register(open_menu, "File")

open_menu.menu = Menu(master=open_menu, tearoff=False)
open_menu["menu"] = open_menu.menu  # назначаем Menu ID
open_menu.menu.add_command(label="Open Folder", command=open_folder)
open_menu.menu.add_command(label="Open File", command=open_file)
open_menu.menu.add_command(label="Add Folder to Playlist", command=add_folder)
open_menu.menu.add_command(label="Add File to Playlist", command=add_file)


def save_playlist():
    name = simpledialog.askstring("Save Playlist", "Enter your playlist name:", initialvalue="user_playlist")
    name += ".txt"
    directory = askdirectory()
    if directory == '':
        return
    os.chdir(directory)
    playlist_file = open(name, "w")
    for name in list_of_songs:
        if directory in name:
            playlist_file.write(name + '\n')
        else:
            playlist_file.write(directory + '/' + name + '\n')
    playlist_file.close()


open_menu.menu.add_command(label="Save Playlist", command=save_playlist)


def load_playlist():
    name = askopenfilename()
    if name == '':
        return
    if not name.endswith("txt"):
        messagebox.showerror("Error", 'File should have ".txt" extension')
        return

    playlist_file = open(name, "r")
    filenames = []

    item_name = playlist_file.readline()
    while item_name != '':
        item_name = item_name[:-1]
        filenames.append(item_name)
        item_name = playlist_file.readline()
    manage_playlist(False, False, True, filenames)


open_menu.menu.add_command(label="Load Playlist", command=load_playlist)


# Функция отображения названия текущей композиции, обновляет соотв. метку
def update_label():
    song_name.set(real_names[index])


# Метка с названием текущей композиции
song_label = Label(root, textvariable=song_name, width=30)
song_label.grid(row=1, column=0, sticky=NW, columnspan=5)


# Следующая композиция. Выбирается случайным образом, если флаг playing_random == True
def next_song():
    global index
    global current_track_time

    if len(list_of_songs) == 0:
        return

    current_track_time = 0

    if playing_random:
        index = random.choice([i for i in range(0, len(list_of_songs)) if i != index])
    else:
        index += 1
        if index >= len(list_of_songs):
            index = 0

    pygame.mixer.music.load(list_of_songs[index])
    pygame.mixer.music.play()

    update_label()


# Кнопка воспроизведения следующей композиции
photo_next = PhotoImage(file="./assets/buttons/next_song.png")
next_song_button = Button(master=root, image=photo_next, bd=0, command=next_song, background='white')
next_song_button.grid(row=5, column=4, sticky=NW, padx=5)
wckToolTips.register(next_song_button, "Play next track")


# Предыдущая композиция. Выбирается случайным образом, если флаг playing_random == True
def previous_song():
    global index
    global current_track_time

    if len(list_of_songs) == 0:
        return

    current_track_time = 0

    if playing_random:
        index = random.choice([i for i in range(0, len(list_of_songs)) if i != index])
    else:
        index -= 1
        if index == -1:
            index = 0

    pygame.mixer.music.load(list_of_songs[index])
    pygame.mixer.music.play()

    update_label()


# Кнопка воспроизведения предыдущей композиции
photo_prev = PhotoImage(file="./assets/buttons/previous.png")
previous = Button(master=root, image=photo_prev, bd=0, command=previous_song, background='white')
previous.grid(row=5, column=3, sticky=NW)
wckToolTips.register(previous, "Play previous track")

# Пауза
paused = False


def pause_song():
    global paused

    paused = True
    pygame.mixer.music.pause()


# Кнопка паузы
photo_pause = PhotoImage(file="./assets/buttons/pause.png")
pause = Button(master=root, image=photo_pause, bd=0, command=pause_song, background='white')
pause.grid(row=5, column=1, sticky=NW, padx=5)
wckToolTips.register(pause, "Pause")


# Воспроизведение
def play_song():
    global playback_stopped
    global paused

    if len(list_of_songs) == 0:
        return

    paused = False
    playback_stopped = False

    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.play()
    else:
        pygame.mixer.music.unpause()

    update_label()


# Кнопка воспроизведения
photo_play = PhotoImage(file="./assets/buttons/play.png")
play = Button(master=root, image=photo_play, bd=0, command=play_song, background='white')
play.grid(row=5, column=0, sticky=NW, padx=1)
wckToolTips.register(play, "Play")

playback_stopped = False


# Остановка воспроизведения
def stop_song():
    global playback_stopped
    global current_track_time

    playback_stopped = True
    pygame.mixer.music.stop()
    current_track_time = 0
    position_scale.set(0)

    song_name.set("")
    time_var.set(0)


# Кнопка остановки воспроиздведения
photo_stop = PhotoImage(file="./assets/buttons/stop.png")
stop = Button(master=root, image=photo_stop, bd=0, command=stop_song, background='white')
stop.grid(row=5, column=2, sticky=NW, padx=5)
wckToolTips.register(stop, "Stop")


# Настройка громкости по шкале
def set_volume(self):
    volume_on_scale = volume_scale.get()
    if type(volume_on_scale) == int:
        volume_on_scale = float(volume_on_scale / 100)
    pygame.mixer.music.set_volume(float(volume_on_scale))


# Шкала громкости
volume_scale = Scale(root, from_=0, to=100, orient=HORIZONTAL, length=175, command=set_volume, background='white', bd=0,
                     highlightbackground='white', sliderlength=15)
volume_scale.grid(row=4, column=1, sticky=SW, columnspan=5, ipady=7)
volume_scale.set(100)

# Мьют
muted = False
volume = volume_scale.get()


def mute():
    global muted
    global volume

    if not muted:
        muted = True
        volume = volume_scale.get()
        volume_scale.set(0)
        sound_button.configure(image=photo_sound_button_muted)
    else:
        muted = False
        volume_scale.set(volume)
        sound_button.configure(image=photo_sound_button)


photo_sound_button = PhotoImage(file="./assets/buttons/sound.png")
photo_sound_button_muted = PhotoImage(file="./assets/buttons/mute.png")
sound_button = Button(master=root, image=photo_sound_button, background='white', bd=0, command=mute)
sound_button.grid(row=4, column=0, sticky=NW, pady=7)
wckToolTips.register(sound_button, "Mute")


# Обновление шкалы времени
def update_position():
    global index
    global current_track_time

    time_string = "Time: {minutes:02d}:{seconds:02d}".format(minutes=int(current_track_time / 60),
                                                             seconds=int(current_track_time % 60))

    if len(list_of_songs) != 0:
        song = MP3(list_of_songs[index])
        current_song_length = song.info.length

        if pygame.mixer.music.get_busy():
            if not paused:
                position_scale.set(current_track_time / current_song_length * 100)
                current_track_time += 1
                time_var.set(time_string)

        else:
            if not playback_stopped:
                if not repeating:
                    if playing_random:
                        index = random.choice([i for i in range(0, len(list_of_songs)) if i != index])
                    else:
                        index += 1
                pygame.mixer.music.load(list_of_songs[index])
                pygame.mixer.music.play()
                position_scale.set(0)
                current_track_time = 0
                time_var.set(time_string)
                update_label()

    root.after(1000, update_position)


# Перемотка композиции при помощи шкалы времени
def change_time(self):
    global current_track_time

    if len(list_of_songs) == 0:
        return

    song = MP3(list_of_songs[index])
    current_song_length = song.info.length

    pygame.mixer.music.rewind()
    pygame.mixer.music.set_pos(current_song_length / 100 * position_scale.get())
    current_track_time = current_song_length / 100 * position_scale.get()


# Шкала времени. current_track_time служит для отсчета времени текущей композиции
current_track_time = 0  # in seconds
time_var = StringVar()

time_label = Label(master=root, textvariable=time_var, width=10)
time_label.grid(row=2, column=0, sticky=NW, columnspan=2)

position_scale = Scale(root, from_=0, to=100, orient=HORIZONTAL, length=135, background='white',
                       bd=0, highlightbackground='white', sliderlength=15, showvalue=0)
position_scale.grid(row=2, column=2, sticky=NW, columnspan=5)
position_scale.bind("<ButtonRelease-1>", change_time)

# Повторение трека
repeating = False


def repeat_track():
    global repeating

    if not repeating:
        repeating = True
        repeat_track_button.configure(relief=SUNKEN, bd=1, bg="blue")
    else:
        repeating = False
        repeat_track_button.configure(relief=RAISED, bd=0, bg="white")


# Кнопка повторения трека
photo_repeat_track = PhotoImage(file="./assets/buttons/repeat.png")
repeat_track_button = Button(master=root, image=photo_repeat_track, bd=0, bg="white",
                             command=repeat_track)
repeat_track_button.grid(row=0, column=1, sticky=NW, padx=4)
wckToolTips.register(repeat_track_button, "Repeat current track")

# Воспроизведение случайного трека (флаг playing_random изменяет работу методов next_song и previous_song
playing_random = False


# Проигрывание случайного трека
def random_track():
    global playing_random

    if not playing_random:
        playing_random = True
        random_track_button.configure(relief=SUNKEN, bd=1, bg="blue")
    else:
        playing_random = False
        random_track_button.configure(relief=RAISED, bd=0, bg="white")


# Кнопка воспроизведения случайного трека из списка
photo_random_track = PhotoImage(file="./assets/buttons/shuffle.png")
random_track_button = Button(master=root, image=photo_random_track, bd=0, bg="white",
                             command=random_track, relief=RAISED)
random_track_button.grid(row=0, column=2, sticky=NW)
wckToolTips.register(random_track_button, "Play tracks in random order")

update_position()
root.mainloop()
