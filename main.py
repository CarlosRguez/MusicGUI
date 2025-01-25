from __future__ import unicode_literals
import threading, time, tkinter
import tkinter.messagebox
from tkinter import *
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

    if selected_playlist:
        db = selected_playlist + '.txt'
        song = buscar(busqueda, 1)
        include_to_db(db, song)
        yt_to_mp3(song, directory)

        filename_path = directory + '/' + song['titulo'] + '.mp3'
        song['route'] = filename_path
        # add_to_playlist(filename_path)
        add_to_playlist(song)
    else:
        statusbar['text'] = "Seleccione una playlist"


#### BUSQUEDA PALABRA
def clear_search_song(event):  # Borra el 'Buscar...' cuando se pulsa
    entrada.delete(0, END)


entrada = Entry(TOPmiddleframe, width=60)
entrada.pack(side=LEFT)
entrada.insert(0, ' Buscar...')
entrada.bind("<Return>", (lambda event: search(entrada.get())))  # Accion con el enter
entrada.bind("<Button-1>", clear_search_song)  # #Borra el texto del principio al pulsar

#### BOTON BUSCAR
searchPhoto = PhotoImage(file='images/search.png')
searchPhoto = searchPhoto.subsample(4)
BOTONbuscar = Button(TOPmiddleframe, image=searchPhoto, command=lambda: search(entrada.get()),
                     bd=0)  # si no se pasaran argumentos, seria command = search
BOTONbuscar.pack(side=RIGHT)


#        NTOPframe

NTopframe = Frame(root)
NTopframe.pack(side=TOP, fill=BOTH, expand=True)  # padx=30


#       NLTopframe

NLTopframe = Frame(NTopframe)
NLTopframe.pack(side=LEFT, fill=BOTH)

#### CARGAR CANCIONES AL SELECCIONAR PLAYLIST
selected_playlist = None


def onselect(event):
    try:  # Dejar de ver los errores cuando no hay w.curselection()[0]
        entradaplaylist.delete(0, END)  # elimina el valor que se introdujo
        w = event.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        print('Has escogido playlist %d: "%s"' % (index, value))
        statusbar['text'] = f"Playlist {value}"
        #### CARGAR PLAYLIST
        try:
            songs = open_file(value + '.txt')
        except FileNotFoundError:  # si no existe el .txt lo creamos:
            save_file(value + '.txt', [])
            songs = open_file(value + '.txt')
        global selected_playlist
        if selected_playlist != value:
            playlistbox.delete(0, tkinter.END)
            for song in songs:
                add_to_playlist(song)
            selected_playlist = value
    except:
        pass


#### ENTRADA ANADIR PLAYLIST
def clear_search_playlist(event):  # Borra el '+ Playlist' cuando se pulsa
    entradaplaylist.delete(0, END)


entradaplaylist = Entry(NLTopframe, width=15)
entradaplaylist.pack(side=TOP)
entradaplaylist.insert(0, '+ Playlist')
entradaplaylist.bind("<Return>", (lambda event: add_playlist(entradaplaylist.get())))  # Accion con el enter
entradaplaylist.bind("<Button-1>", clear_search_playlist)  # Borra el texto del principio al pulsar ( el + Playlist)
#### LIST BOX PLAYLISTS
playlistbox2 = Listbox(NLTopframe, width=15)
playlistbox2.pack(side=TOP, fill='y', expand=True)
playlistbox2.bind('<<ListboxSelect>>', onselect)  # al pulsar


def add_playlist(name):
    if name not in open_file('playlists.txt'):
        include_to_db('playlists.txt', name)
    ind = 0
    playlistbox2.insert(ind, name)  # visualizar las playlists
    ind += 1


#### MINIATURA IMAGEN
im = Image.open('images/disco-vinilo.jpg')
im = im.resize((90, 60), Image.ANTIALIAS)
image = ImageTk.PhotoImage(im)

miniatura = tkinter.Label(NLTopframe, image=image)
miniatura.pack(side=BOTTOM)


def mostrar_imagen(url):
    try:  # el try por si no hay internet y da error
        with urllib.request.urlopen(url) as u:
            raw_data = u.read()
        im = Image.open(BytesIO(raw_data))
        im = im.resize((90, 60), Image.ANTIALIAS)
        new_image = ImageTk.PhotoImage(im)

        miniatura.configure(image=new_image)
        miniatura.image = new_image
    except:
        pass


def cambiar_miniatura():
    songs = open_file(selected_playlist + '.txt')
    hay_miniatura = False
    for song in songs:
        if song['route'] == playlist[selected_song]:
            statusbar['text'] = 'Reproduciendo: ' + song['titulo']
            mostrar_imagen(song['thumbnail'])
            hay_miniatura = True
    if not hay_miniatura:  # e.g. para los mp3 que no hemos descargado, que son del equipo
        miniatura.configure(image=image)  # ponemos la imagen por defecto
        miniatura.image = image


####CARGAR LISTA DE PLAYLISTS de playlists.txt
nombres_playlists = open_file('playlists.txt')
for x in list(nombres_playlists):
    add_playlist(x)


#       NRTopframe

NRTopframe = Frame(NTopframe)
NRTopframe.pack(side=LEFT, fill=BOTH, expand=True)

#### SCROLLBAR
scrollbar = Scrollbar(NRTopframe, orient="vertical")
scrollbar.pack(side='right', fill=BOTH)

#### LIST BOX SONGS
playlistbox = Listbox(NRTopframe)
playlistbox.pack(expand=True, fill=BOTH)
playlistbox.config(yscrollcommand=scrollbar.set)  ## SCROLLBAR
scrollbar.config(command=playlistbox.yview)  ## SCROLLBAR


#        NBottomframe

NBottomframe = Frame(root, height=100)
NBottomframe.pack(side=BOTTOM, fill=BOTH)


#       leftframe
leftframe = Frame(NBottomframe)
leftframe.pack(side=LEFT)

####CONTADOR
currenttimelabel = Label(leftframe, text='--:-- /')  # text='Current Time : --:--'
currenttimelabel.pack(side=LEFT)

####DURACION
lengthlabel = Label(leftframe, text='--:--')  # text='Total Length : --:--'
lengthlabel.pack(side=LEFT)


####DURACION
def show_details(play_song):
    file_data = os.path.splitext(play_song)

    if file_data[1] == '.mp3':
        audio = MP3(play_song)
        total_length = audio.info.length
    else:
        a = mixer.Sound(play_song)
        total_length = a.get_length()

    # div - total_length/60, mod - total_length % 60
    mins, secs = divmod(total_length, 60)
    mins = round(mins)
    secs = round(secs)
    timeformat = '{:02d}:{:02d}'.format(mins, secs)
    # lengthlabel['text'] = "Total Length" + ' - ' + timeformat
    lengthlabel['text'] = timeformat

    t1 = threading.Thread(target=start_count, args=(total_length,))
    t1.start()


def start_count(t):
    global paused
    # mixer.music.get_busy(): - Returns FALSE when we press the stop button (music stop playing)
    # Continue - Ignores all of the statements below it. We check if music is paused or not.
    current_time = 0
    while current_time <= t and mixer.music.get_busy():
        if paused:
            continue
        else:
            mins, secs = divmod(current_time, 60)
            mins = round(mins)
            secs = round(secs)
            timeformat = '{:02d}:{:02d}'.format(mins, secs)
            # currenttimelabel['text'] = "Current Time" + ' - ' + timeformat
            currenttimelabel['text'] = timeformat + ' /'
            time.sleep(1)
            current_time += 1


#       middleframe
middleframe = Frame(NBottomframe)
middleframe.place(relx=.5, rely=.5, anchor="center")

def play_music():
    global paused
    if paused:
        mixer.music.unpause()
        statusbar['text'] = "Music Resumed"
        paused = FALSE
    else:
        global selected_song
        selected_song = playlistbox.curselection()
        selected_song = int(selected_song[0])

        print('Has escogido cancion', selected_song, ': ', playlist[selected_song])

        mixer.music.stop()
        time.sleep(1)

        mixer.music.load(playlist[selected_song])
        mixer.music.play(0)

        show_details(playlist[selected_song])  # tiempo de avance cancion
        cambiar_miniatura()
        continuar_reproduciendo_al_terminar()

def continuar_reproduciendo_al_terminar():
    global selected_song
    pos = mixer.music.get_pos()
    if int(pos) == -1:
        selected_song += 1
        mixer.music.load(playlist[selected_song])
        mixer.music.play(0)
        show_details(playlist[selected_song])  # tiempo de avance cancion
        cambiar_miniatura()
        playlistbox.selection_clear(0, END)  # Clear blue highlighted song
        playlistbox.selection_set(selected_song)  # blue highligh next song
    root.after(1, continuar_reproduciendo_al_terminar)

def siguiente_cancion():
    mixer.music.stop()
    time.sleep(1)
    global paused
    paused = FALSE
    continuar_reproduciendo_al_terminar()

paused = FALSE

def pause_music():
    global paused
    paused = TRUE
    mixer.music.pause()
    statusbar['text'] = "Musica pausada"

def rewind_music():
    play_music()
    statusbar['text'] = "Musica Rewinded"
    
def set_vol(val):
    volume = int(val) / 100
    mixer.music.set_volume(volume)
    # set_volume of mixer takes value only from 0 to 1. Example - 0, 0.1,0.55,0.54.0.99,1

muted = FALSE

def mute_music():
    global muted
    if muted:  # Unmute the music
        mixer.music.set_volume(0.7)
        volumeBtn.configure(image=volumePhoto)
        scale.set(70)
        muted = FALSE
    else:  # mute the music
        mixer.music.set_volume(0)
        volumeBtn.configure(image=mutePhoto)
        scale.set(0)
        muted = TRUE

#### BOTON PLAY
playPhoto = PhotoImage(file='images/play3.png')
playPhoto = playPhoto.subsample(4)  # Disminuye size
playBtn = Button(middleframe, image=playPhoto, command=play_music, bd=0)
playBtn.pack(side=LEFT)

#### BOTON PAUSE
pausePhoto = PhotoImage(file='images/pause3.png')
pausePhoto = pausePhoto.subsample(4)
pauseBtn = Button(middleframe, image=pausePhoto, command=pause_music, bd=0)
pauseBtn.pack(side=LEFT)

'''
carlitos = None
def carlos():
    global carlitos
    if carlitos == TRUE:
        ppBtn.configure(image=playPhoto)
        carlitos = FALSE
        pause_music()
    else: 
        ppBtn.configure(image=pausePhoto)
        carlitos = TRUE
        play_music()

ppPhoto = PhotoImage(file='images/stop3.png')
ppPhoto = ppPhoto.subsample(4)
ppBtn = Button(middleframe, image=ppPhoto, command=carlos, bd=0)
ppBtn.pack(side=LEFT)
'''

#### BOTON FORWARD
forwardPhoto = PhotoImage(file='images/forward.png')
forwardPhoto = forwardPhoto.subsample(4)
forwardBtn = Button(middleframe, image=forwardPhoto, command=siguiente_cancion, bd=0)
forwardBtn.pack(side=LEFT)


#       rightframe
rightframe = Frame(NBottomframe)
rightframe.pack(side=RIGHT, fill="none")

#### BOTON REWIND
rewindPhoto = PhotoImage(file='images/rewind3.png')
rewindPhoto = rewindPhoto.subsample(4)
rewindBtn = Button(rightframe, image=rewindPhoto, command=rewind_music, bd=0)
rewindBtn.pack(side=LEFT)

#### BOTON MUTE
mutePhoto = PhotoImage(file='images/mute3.png')
mutePhoto = mutePhoto.subsample(4)
volumePhoto = PhotoImage(file='images/volume3.png')
volumePhoto = volumePhoto.subsample(4)
volumeBtn = Button(rightframe, image=volumePhoto, command=mute_music, bd=0)
volumeBtn.pack(side=LEFT)

#### VOLUMEN
scale = Scale(rightframe, from_=0, to=100, orient=HORIZONTAL, command=set_vol)
scale.set(70)  # volumen por defecto
mixer.music.set_volume(0.7)
scale.pack(side=LEFT)

def on_closing():
    try: #si la musica se inicio
        mixer.music.stop()
        root.destroy()
    except:
        root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()


