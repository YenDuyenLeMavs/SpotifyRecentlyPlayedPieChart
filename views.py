from flask import Blueprint, render_template, request, redirect, url_for

import spotipy
from spotipy.oauth2 import SpotifyOAuth

import matplotlib
import matplotlib.pyplot as plt

import pyautogui
import webbrowser
import os
from dotenv import load_dotenv

class Item:
    def __init__(self, id, name, artist, streams):
        self.id = id
        self.name = name
        self.artist = artist
        self.streams = streams

views = Blueprint(__name__, "views")

resultsSorted = []
streams = []
names = []
percentages = []
limit = "50"

@views.route("/")
def home():
    return render_template("home.html")

@views.route("/get-chart/", methods = ['Post'])
def get_chart():
    global resultsSorted
    global streams
    global names
    global percentages
    global limit

    if request.method == 'POST':
        form_data = request.form
    scope = ["user-library-read", "user-read-recently-played"]
    load_dotenv()
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri = 'http://localhost:8888/callback', scope=scope))
    
    limit = form_data.get("Name")
    if int(limit) <= 0 or int(limit) > 50:
        limit = "50"
    results = sp.current_user_recently_played(limit=limit)
 
    pyautogui.hotkey('ctrl', 'w')
    
    for idx, item in enumerate(results['items']):
        track = item['track']
        unique = True
        for j in resultsSorted:
            if track['id'] == j.id:
                unique = False
                j.streams += 1
                break
        if unique == True:
            resultsSorted.append(Item(id=track['id'], name=track['name'], artist=track['artists'][0]['name'], streams=1))

    def sortByStreams(item):
        return item.streams
        
    resultsSorted.sort(reverse=True, key=sortByStreams)

    for j in resultsSorted:
        streams.append(j.streams)
        percentages.append(round((j.streams / float(limit) * 100), 2))

    plt.pie(streams, autopct='%.2f%%', pctdistance=1.1, textprops={'fontsize': 4})
    plt.savefig('static/temp.png', dpi=150)
    matplotlib.use('Agg')

    webbrowser.open('https://accounts.spotify.com/en/logout')
    os.remove('.cache')

    return redirect(url_for("views.chart"))
@views.route("/chart")
def chart():   
    return render_template("chart.html", resultsSorted=resultsSorted, percentages=percentages, limit=limit)

