# NOME SCRIPT: StreamingCommunity Serie Downloader
# VERSIONE: 1.0
# DATA: 15 febbraio 2025
# AUTORI: *Glider con la preziosa collaborazione dell'intelligenza artificiale (ChatGPT)

# DESCRIZIONE:
# Questo script permette di cercare e scaricare episodi da StreamingCommunity utilizzando 
# l'API di "streamingcommunity" e yt-dlp per il download del contenuto. 
# 

# ATTENZIONE
# Modifica il percorso in cui salvare il file ad es. c:\serie nella var download_directory

# LICENSE:
# Questo script è liberamente utilizzabile, con la seguente condizione:
# Se desideri utilizzare e modificare lo script, ti chiedo gentilmente di fare una donazione 
# a tua discrezione, in modo che io possa continuare a migliorare questo e altri script.
# Puoi fare una donazione in criptovalute come Bitcoin, Dogecoin, o Ethereum.
# 
# Se sei interessato a fare una donazione, puoi utilizzare i seguenti indirizzi:
# Bitcoin: 1GMukowiQJYTjAY2cYStDJFxiDZ9FsbA23
# Dogecoin: DR2cEpXFahfQHKS8GU8gpfajBGDVEcqNaZ
# Ethereum: 0xF1BdF4eFD3Dd69696874B898491B8D6FcC5a60eD
# Solana: nRfEP8pWnA12DwEiTpWZrnsYRxLapG7fAQZYJyojjNT
# Aleo: aleo18mfh9vaxskpgf5e3a4vfw4ts5vd79as32a284ejaaxttdyusa5rqgg0qr9
# Dimo: 0xd7EFE727Bd1D7B2BCeA604100Fe3d83CcE45F3a3
# Near: 7fe5e7ca0e0efac6379c6896091d4f636def90c593f4930af4de8bf0b260fbea
# Floky: 0x0099dB0556fa8D3910fA27Dde5dcC10Db898111c
#
# Grazie per il tuo supporto!

# Nota: Questo script è stato sviluppato a scopo personale e non è destinato alla distribuzione commerciale.
# Buon download!

import sys
import requests
import random
import os
import re
import subprocess
import yt_dlp
import webbrowser
import json
import html
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from scuapi import API

from concurrent.futures import ThreadPoolExecutor

# Memorizza il dominio di default
default_domain = "https://streamingcommunity.paris"
current_domain = default_domain

# Inizializza l'API
sc = API('streamingcommunity.paris')

# Lista di User-Agent comuni
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.64 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Opera/78.0.4093.147 Safari/537.36",
]

def pulisci(testo):
    testo_pulito = re.sub(r'[^a-zA-Z0-9\s]', '', testo)
    testo_pulito = re.sub(r'\s+', ' ', testo_pulito)
    testo_pulito = testo_pulito.strip()
    return testo_pulito

def download_series(m3u_playlist_url, download_directory, episode_title, series_name, season_number, episode_number):
    os.chdir(download_directory)
    
    season_folder = f'{series_name}/Stagione {season_number}'
    os.makedirs(season_folder, exist_ok=True)
    episode_number = str(episode_number).zfill(2)
    
    output_template = f'{season_folder}/{episode_number} - {episode_title}.%(ext)s'
    
     # Opzioni di configurazione per yt-dlp
    ydl_opts = {
        'outtmpl': output_template,  # Usa il nome della serie, stagione e episodio nel nome del file
        'verbose': True,
        'noplaylist': True,
        'concurrent_fragment_downloads': 10,
        'retries': 5,
    }

    # Avvia yt-dlp per ottenere i formati disponibili
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Ottieni le informazioni del video
        info_dict = ydl.extract_info(m3u_playlist_url, download=False)

        # Lista dei formati disponibili
        formati = info_dict.get('formats', [])
        
        # Cerca un formato combinato (audio e video)
        formato_combinato = None
        for formato in formati:
            if formato.get('vcodec') and formato.get('acodec'):  # Deve avere sia audio che video
                if formato_combinato is None or formato['height'] > formato_combinato['height']:
                    formato_combinato = formato
        
        if formato_combinato:
            # Se un formato combinato è disponibile, seleziona il miglior formato
            formato_id = formato_combinato['format_id']
            ydl_opts['format'] = formato_id
            print(f"Scarico il formato combinato: {formato_id}")
        else:
            # Se il formato combinato non è disponibile, scegli separatamente video e audio
            video_format = None
            audio_format = None
            for formato in formati:
                if formato.get('vcodec') and (not video_format or formato['height'] > video_format['height']):
                    video_format = formato
                if formato.get('acodec') and formato['acodec'] == 'mp4a.40.2' and formato.get('language') == 'ita':
                    audio_format = formato  # Seleziona l'audio in italiano

            if video_format and audio_format:
                # Usa l'ID dei formati video e audio per scaricare separatamente
                ydl_opts['format'] = f"{video_format['format_id']}+{audio_format['format_id']}"
                print(f"Scarico separatamente il video: {video_format['format_id']} e l'audio italiano: {audio_format['format_id']}")
            else:
                print("Non è stato possibile trovare i formati desiderati.")

        # Esegui il download
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([m3u_playlist_url])
            
def menu():
    print("Seleziona un'opzione:")
    print("1) Download")
    print("2) Guarda video")
    print("3) Esci")

def operazione_principale(iframe,m3u_playlist_url, download_directory,title):
    while True:
        menu()
        scelta = input("Inserisci la tua scelta (1/2/3): ")

        if scelta == "1":
            print("Inizio download...")
            download_movie(m3u_playlist_url, download_directory,title)
        elif scelta == "2":
            webbrowser.open(iframe)
        elif scelta == "3":
            print("Uscita dal programma.")
            break
        else:
            print("Scelta non valida, riprova.")     # Opzioni di configurazione per yt-dlp
    ydl_opts = {
        'outtmpl': f'{movie_name}.%(ext)s',
        'verbose': True,
        'noplaylist': True,
        'concurrent_fragment_downloads': 10,
        'retries': 5,
    }

    # Avvia yt-dlp per ottenere i formati disponibili
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Ottieni le informazioni del video
        info_dict = ydl.extract_info(m3u_playlist_url, download=False)

        # Lista dei formati disponibili
        formati = info_dict.get('formats', [])
        
        # Cerca un formato combinato (audio e video)
        formato_combinato = None
        for formato in formati:
            if formato.get('vcodec') and formato.get('acodec'):  # Deve avere sia audio che video
                if formato_combinato is None or formato['height'] > formato_combinato['height']:
                    formato_combinato = formato
        
        if formato_combinato:
            # Se un formato combinato è disponibile, seleziona il miglior formato
            formato_id = formato_combinato['format_id']
            ydl_opts['format'] = formato_id
            print(f"Scarico il formato combinato: {formato_id}")
        else:
            # Se il formato combinato non è disponibile, scegli separatamente video e audio
            video_format = None
            audio_format = None
            for formato in formati:
                if formato.get('vcodec') and (not video_format or formato['height'] > video_format['height']):
                    video_format = formato
                if formato.get('acodec') and formato['acodec'] == 'mp4a.40.2' and formato.get('language') == 'ita':
                    audio_format = formato  # Seleziona l'audio in italiano

            if video_format and audio_format:
                # Usa l'ID dei formati video e audio per scaricare separatamente
                ydl_opts['format'] = f"{video_format['format_id']}+{audio_format['format_id']}"
                print(f"Scarico separatamente il video: {video_format['format_id']} e l'audio italiano: {audio_format['format_id']}")
            else:
                print("Non è stato possibile trovare i formati desiderati.")

        # Esegui il download
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([m3u_playlist_url])
            
def menu():
    print("Seleziona un'opzione:")
    print("1) Download")
    print("2) Guarda video")
    print("3) Esci")

def operazione_principale(iframe,m3u_playlist_url, download_directory,title):
    while True:
        menu()
        scelta = input("Inserisci la tua scelta (1/2/3): ")

        if scelta == "1":
            print("Inizio download...")
            download_movie(m3u_playlist_url, download_directory,title)
        elif scelta == "2":
            webbrowser.open(iframe)
        elif scelta == "3":
            print("Uscita dal programma.")
            break
        else:
            print("Scelta non valida, riprova.")

def get_response_with_retries(url, retries=3):
    for attempt in range(retries):
        user_agent = random.choice(user_agents)
        headers = {'User-Agent': user_agent}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response
        else:
            print(f"Tentativo {attempt + 1} fallito con status {response.status_code}. Riprovo...")
    
    # Se falliscono tutti i tentativi, restituisce l'ultimo errore
    print(f"Tutti i {retries} tentativi falliti. Restituisco l'errore.")
    return response

def get_iframe_src(urliframe):
    # Ottieni la risposta dal web
    response_frame = get_response_with_retries(urliframe)
    if response_frame:
        html_content_frame = response_frame.text  # Contenuto HTML

        # Creiamo un oggetto BeautifulSoup per analizzare il codice HTML
        soup = BeautifulSoup(html_content_frame, 'html.parser')  # Passa il contenuto HTML e il parser giusto

        # Troviamo l'iframe tramite il ref e estraiamo l'attributo 'src'
        iframe = soup.find('iframe', {'ref': 'iframe'})
        src = iframe['src'] if iframe else None

        return src
    else:
        print("Impossibile ottenere il contenuto HTML dalla URL.")
        return None

# Funzione di supporto per ottenere la risposta con retries (puoi adattarla se necessario)
def get_response_with_retries(url, retries=3):
    for _ in range(retries):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Alza un'eccezione se la richiesta fallisce
            return response
        except requests.RequestException as e:
            print(f"Errore durante la richiesta: {e}")
    return None  # Restituisce None se fallisce dopo i retry

def search_and_download(search_term, download_directory):
    result = sc.search(search_term)
    
    last_title = list(result.values())[0]
    last_name = last_title.get('name')
    last_name = pulisci(last_name)
    print(f"Titolo serie: {last_name}")

    episode_details = []  # Spostiamo la variabile per memorizzare gli episodi fuori dal ciclo
    
    for title, details in result.items():
        if search_term.lower() in title.lower():
            id = details.get('id')
            print(f"Id per '{title}': {id}")

            iframe, m3u_playlist_url = sc.get_links(id)
            print(f"iFrame per '{title}': {iframe}")
            print(f"URL M3U Playlist per '{last_name}': {m3u_playlist_url}")
            
            seasons_count = details.get('seasons_count', 0)
            print(f"Numero di stagioni: {seasons_count}")
            slug = details.get('slug')

            # Estraiamo gli episodi di tutte le stagioni
            for season_number in range(1, seasons_count + 1):
                print(f"Pagina stagione {season_number} di {title}")
                episode_page = current_domain + "/titles/" + str(id) + "-" + slug + "/stagione-" + str(season_number)
                print(f"Url pagina episodi: {episode_page}")

                # Scraping della pagina degli episodi
                response = get_response_with_retries(episode_page)
                if response.status_code == 200:
                    # Estrai i dati dalla pagina (JSON)
                    html_content = response.text
                    match = re.search(r'<div id="app" data-page="(.*?)">', html_content)
                    if match:
                        data_page = match.group(1)
                        
                        # Decodifica le entità HTML nel contenuto di data-page
                        decoded_data_page = html.unescape(data_page)
                        
                        try:
                            data = json.loads(decoded_data_page)
                            id_stagione = data["props"]["loadedSeason"]["id"]
                            episodes = data["props"]["loadedSeason"]["episodes"]

                            for episode in episodes:
                                episode_id = episode["id"]
                                episode_number = episode["number"]
                                episode_title = episode["name"]
                                imageable_id = episode["images"][0]["imageable_id"]
                                #urliframe = current_domain + "/iframe/" + str(id) + "?episode_id=" + str(episode_id) + "&next_episode=1"
                                #urliframe = current_domain + "/watch/" + str(id) + "?e=" + str(episode_id)
                                # QUI IMPLEMENTA IN CODICE PER RILEVARE URL IFRAME REF="IFRAME"
                                #src = get_iframe_src(urliframe)
                                print(f"{title} {id}: Episodio {episode_number} {episode_title} {episode_id}")
                                #print(f"src {src}")
                                print("")
                                print("")
                                #iframe, m3u_playlist_episode_url, m3u_playlist_file = sc.get_links(str(id), episode_id = str(episode_id), get_m3u=True)
                                iframe, m3u_playlist_episode_url = sc.get_links(str(id) + "?e=" + str(episode_id))
                                #print(f"M3U playlist: {m3u_playlist_file}")
                                print(f"M3U Epis Url: {m3u_playlist_episode_url}")
                                download_series(m3u_playlist_episode_url, download_directory, episode_title, title, season_number, episode_number)
                                #break
                                episode_details.append({"episode_id": episode_id, "episode_title": episode_title, "episode_number": episode_number})

                        except json.JSONDecodeError:
                            print("Errore nel decodificare il JSON da data-page.")
                    else:
                        print("Impossibile trovare il div con id 'app' e l'attributo data-page.")
                else:
                    print(f"Errore nel recuperare la pagina degli episodi. Status code: {response.status_code}")

    return episode_details



# Esegui la ricerca e il download per il termine inserito
# Modifica il percorso in cui salvare il file ad es. c:\serie
download_directory = r"CARTELLA PER IL DOWNLOAD"
search_term = input("Inserisci il titolo della SERIE da cercare: ")
search_and_download(search_term, download_directory)
