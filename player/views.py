from django.shortcuts import render, reverse

from django.http import HttpResponse, HttpResponseRedirect
from django.core import serializers

import requests
import json
import time
from urllib.parse import urlencode

from .SpotifyAuth import SpotifyAuth
from .SongQueue import SongQueue

from django.http import JsonResponse

def health_check(request):
    return JsonResponse({'status': 'healthy'})

# Create your views here.

def index(request):
    params = {
        "client_id": SpotifyAuth.getSpotifyId(),
        "response_type": "code",
        "redirect_uri": SpotifyAuth.getSpotifyRedirectUri(),
        "scope": SpotifyAuth.getSpotifyLoginScope(),
        "show_dialog": "true",
    }
    auth = getAuth(request)
    if auth==None:
        context={
            "loggedOut" : True,
            "login_link": f"https://accounts.spotify.com/en/authorize?{urlencode(params)}"
        }
        return render(request, "player/index.html", context)
    playerResponse = requests.get("https://api.spotify.com/v1/me/player", headers={"Authorization": auth})
    if playerResponse.status_code==204:
        return render(request, "player/index.html", context={"song_title": "No song playing"})
    elif playerResponse.status_code==200:
        context = getCurrentSongInfo(request, auth)
        return render(request, "player/index.html", context)
    else:
        return HttpResponse("Spotify API returned status"+playerResponse.status_code)


def callback(request):
    code = request.GET.get("code", None)
    if code!=None:
        spotify_auth=SpotifyAuth(code)
        #cookie
        request.session["token"] = spotify_auth.toJSON()
        #auth = spotify_auth.getAuth()

    return HttpResponseRedirect(reverse("index"))

def getAuth(request):
    token = request.session.get("token", None)
    if token==None:
        return None
    t = json.loads(token)
    spotify_auth = SpotifyAuth(access_token=t["access_token"], refresh_token=t["refresh_token"], expiry_time=t["expiry_time"])
    auth = spotify_auth.getAuth()
    request.session["token"] = spotify_auth.toJSON()
    return auth

def skip_next(request):
    res = requests.post("https://api.spotify.com/v1/me/player/next", headers={"Authorization": getAuth(request)})
    return HttpResponse(json.dumps(res.status_code))

def skip_previous(request):
    res = requests.post("https://api.spotify.com/v1/me/player/previous", headers={"Authorization": getAuth(request)})
    return HttpResponse(json.dumps(res.status_code))

def play(request):
    res = requests.put("https://api.spotify.com/v1/me/player/play", headers={"Authorization": getAuth(request)})
    return HttpResponse(json.dumps(res.status_code))

def pause(request):
    res = requests.put("https://api.spotify.com/v1/me/player/pause", headers={"Authorization": getAuth(request)})
    return HttpResponse(json.dumps(res.status_code))

def getAlbumCoverLink(request, song_id):
    res = requests.get("https://api.spotify.com/v1/tracks/"+song_id, headers={"Authorization": getAuth(request)})
    playerJson = json.loads(res.text)
    return playerJson["album"]["images"][0]["url"]

def getSongQueue(request):
    sq_cookie = request.session.get("songqueue", None)
    if sq_cookie==None:
        sq = SongQueue(length=19)
    else:
        sq_json = json.loads(sq_cookie)
        sq = SongQueue(length=sq_json["length"],head=sq_json["head"],queue=sq_json["queue"])
    return sq

def isSongPaused(request, auth):
    res1 = requests.get("https://api.spotify.com/v1/me/player", headers={"Authorization": auth})
    if res1.status_code==204:
        #no song playing / spotify closed
        return True
    playerJson = json.loads(res1.text)
    before = playerJson["progress_ms"]
    #wait so song can progress and spotify update
    time.sleep(0.5)
    artistResponse = requests.get("https://api.spotify.com/v1/me/player", headers={"Authorization": auth})
    artistJson = json.loads(artistResponse.text)
    after = artistJson["progress_ms"]
    if after-before > 0:
        return False
    else:
        return True

def getCurrentSongInfo_HTTP_RES(request):
    auth = getAuth(request)
    if auth==None:
        return JsonResponse({'status': 'unauthenticated'})
    return HttpResponse(json.dumps(getCurrentSongInfo(request, auth)))

def getCurrentSongID(request):
    auth = getAuth(request)
    playerResponse = requests.get("https://api.spotify.com/v1/me/player", headers={"Authorization": auth})
    playerJson = json.loads(playerResponse.text)
    data = {
        "song_id" : playerJson["item"]["id"],
        "song_progress" : playerJson["progress_ms"],
        "isPaused": isSongPaused(request, auth),
    }
    return HttpResponse(json.dumps(data))

def getCurrentSongInfo(request, auth):
    isPaused = isSongPaused(request, auth)
    playerResponse = requests.get("https://api.spotify.com/v1/me/player", headers={"Authorization": auth})
    if playerResponse.status_code != 200:
        return HttpResponse("Bad response", 500 )
    playerJson = json.loads(playerResponse.text)
    isLiked = checkLiked(request, playerJson["item"]["id"], auth)
    likedClass="not-liked"
    if isLiked:
        likedClass="liked"

    sq = getSongQueue(request)
    sq.addItem(playerJson["item"]["album"]["images"][0]["url"])
    request.session["songqueue"] = sq.toJSON()
    artist_id = playerJson["item"]["artists"][0]["id"]
    artistResponse = requests.get("https://api.spotify.com/v1/artists/"+artist_id, headers={"Authorization":  auth})
    artistJson = json.loads(artistResponse.text)
    data = {
        "song_id" : playerJson["item"]["id"],
        "song_title" : playerJson["item"]["name"],
        "song_artist" : playerJson["item"]["artists"][0]["name"],
        "song_art" : sq.peak(),
        "artist_image" : "noaristfound.png" if len(artistJson["images"]) == 0 else artistJson["images"][0]["url"],
        "song_progress" : playerJson["progress_ms"],
        "song_duration" : playerJson["item"]["duration_ms"],
        "song_time_left" : playerJson["item"]["duration_ms"] - playerJson["progress_ms"] + 1000,
        "recents" : sq.getTail(),
        "isPaused": isPaused,
        "likedClass" : likedClass,
    }
    return data

def checkLiked(request, song_id, auth):
    url = "https://api.spotify.com/v1/me/tracks/contains?ids="+song_id
    res = requests.get(url, headers={"Authorization": auth})
    print(res.status_code)
    if res.status_code==200:
        playerJson = json.loads(res.text)
        return playerJson[0]
    else:
        return False



def like_song(request, song_id):
    url = "https://api.spotify.com/v1/me/tracks?ids="+song_id
    res = requests.put(url, headers={"Authorization": getAuth(request)})
    return HttpResponse(json.dumps(res.status_code))