from __future__ import unicode_literals
import threading, time, tkinter
import tkinter.messagebox
from tkinter import *
from tkinter import filedialog
from mutagen.mp3 import MP3
from pygame import mixer
from io import BytesIO
from PIL import Image, ImageTk
import urllib
import urllib.request
import youtube_dl
from youtube_search import YoutubeSearch
import os, sys, os.path, json, unidecode


def remove_accents(string):
    return unidecode.unidecode(string)

def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def buscar(busqueda, pos):
    results = YoutubeSearch(busqueda, max_results=pos).to_dict()
    song = {
        "id": results[pos - 1]['id'],
        "url": 'https://www.youtube.com' + results[pos - 1]['url_suffix'],
        "titulo": remove_accents(results[pos - 1]['title']),
        "duration": results[pos - 1]['duration'],
        "thumbnail": results[pos - 1]['thumbnails'][-1],
        "route": 'my_mp3/' + remove_accents(results[pos - 1]['title']) + '.mp3'
    }
    return song

def open_file(file_name):
    with open(file_name, "r") as fp:
        busquedas = json.load(fp)
        return busquedas

def save_file(file_name, data):
    with open(file_name, "w") as fp:
        json.dump(data, fp)

def remove_file(route):
    os.remove(route)

def include_to_db(database, song):
    if os.path.exists(database):
        songs = open_file(database)
    else:
        songs = []
    songs.append(song)
    save_file(database, songs)
    return songs

def create_playlists_txt(database):
    if not os.path.exists(database):
        file = []
        save_file(database, file)
create_playlists_txt('playlists.txt')

def remove_from_db(database, song):
    songs = open_file(database)
    for item in songs:
        if item['id'] == song['id']:
            songs.remove(item)
    save_file(database, songs)
    return songs

def yt_to_mp3(song, directory):
    ydl_opts = {
        'outtmpl': directory + '/' + song["titulo"] + '.%(ext)s',
        'extractaudio': True,
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([song['url']])
        song["route"] = directory + '/' + song["titulo"] + '.mp3'
        statusbar['text'] = "Descarga completada"
    except:
        statusbar['text'] = "Error en yt_to_mp3"

#GUI
root = Tk()
root.minsize(600, 350)
root.title("OWNPLAY")
root.iconbitmap(r'images/images.ico')
mixer.init()
statusbar = Label(root, text="Bienvenido a OWNPLAY", relief=SUNKEN, anchor=W)
statusbar.pack(side=BOTTOM, fill=X)

#MENU
menubar = Menu(root)
root.config(menu=menubar)
subMenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Archivo", menu=subMenu)
subMenu.add_command(label="Salir", command=root.destroy)

def about_us():
    tkinter.messagebox.showinfo('Acerca de', '...')

subMenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Ayuda", menu=subMenu)
subMenu.add_command(label="Acerca de", command=about_us)

playlist = []

def add_to_playlist(song):
    filename = song['route']
    filename = os.path.basename(str(filename))
    index = 0
    playlistbox.insert(index, filename)
    playlist.insert(index, song['route'])
    index += 1

TOPframe = Frame(root, height=50)
TOPframe.pack(side=TOP, fill=BOTH)

def browse_file():
    global filename_path
    filename_path = filedialog.askopenfilename()
    if len(filename_path) != 0:
        song = {'route': filename_path}
        add_to_playlist(song)

addPhoto = PhotoImage(file='images/folder.png')
addPhoto = addPhoto.subsample(4)
addBtn = Button(TOPframe, image=addPhoto, command=browse_file, bd=0)
addBtn.pack(side=LEFT)

def del_song():
    if playlistbox.curselection():
        selected_song = playlistbox.curselection()
        selected_song = int(selected_song[0])
        todas_las_opciones = list(playlistbox.get(0, tkinter.END))
        posicion = len(todas_las_opciones) - ((selected_song) + 1)
        songs = open_file(selected_playlist + '.txt')
        song = songs[posicion]
        playlistbox.delete(selected_song)
        remove_from_db(selected_playlist + '.txt', song)
        try:
            remove_file(song['route'])
            print('BORRAR CANCION', song['route'])
            mixer.init()
        except:
            mixer.quit()
            remove_file(song['route'])
            print('BORRAR CANCION', song['route'])
            mixer.init()
    if playlistbox2.curselection():
        playlist_to_delete = playlistbox2.curselection()
        playlist_to_delete = int(playlist_to_delete[0])
        lista = open_file('playlists.txt')
        todas_las_opciones = list(playlistbox2.get(0, tkinter.END))
        pos = len(todas_las_opciones) - (playlist_to_delete + 1)
        nombre_playlist = lista[pos]
        print('BORRAR PLAYLIST: ', nombre_playlist, ', (item:', playlist_to_delete, ')')
        lista.remove(nombre_playlist)
        save_file('playlists.txt', lista)
        playlistbox2.delete(playlist_to_delete)
        playlistbox.delete(0, 'end')
        songs = open_file(nombre_playlist + '.txt')
        for song in songs:
            try:
                mixer.quit()
                remove_file(song['route'])
                print('BORRADO')
                mixer.init()
            except:
                mixer.init()
        remove_file(nombre_playlist + '.txt')

delPhoto = PhotoImage(file='images/trash.png')
delPhoto = delPhoto.subsample(4)
delBtn = Button(TOPframe, image=delPhoto, command=del_song, bd=0)
delBtn.pack(side=LEFT)

TOPmiddleframe = Frame(TOPframe)
TOPmiddleframe.place(relx=.5, rely=.5, anchor="center")

selected_playlist = None

def search(busqueda):
    entrada.delete(0, END)
    statusbar['text'] = f"Buscando: {busqueda}"

    directory = 'my_mp3'
    create_directory(directory)

    if selected_playlist:
        db = selected_playlist + '.txt'
        song = buscar(busqueda, 1)
        include_to_db(db, song)
#---------------------------------------------------------------------------------------------------------------



#    THIS ARE THE FIRST 200 OF 670 LINES OF CODE.
#    FOR COMPLETE AND COMMENTED FILE CONTACT ME



