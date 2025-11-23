from airflow import DAG
from pendulum import datetime
from airflow.providers.http.operators.http import HttpOperator
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
import os 

SONGS_PATH = "/tmp/songs/songs_data.csv"

default_args = {
    'owner': 'camila y lucia',
    'start_date': datetime.today() - timedelta(days=1),
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
    'email_on_failure': False,
    'depends_on_past': False,
}

COUNTRIES = [
    "argentina","bolivia","chile","colombia","costa rica","cuba","dominican republic",
    "ecuador","el salvador","equatorial guinea","guatemala","honduras","mexico","nicaragua",
    "panama", "paraguay","peru","spain","uruguay","venezuela","united states",
    "albania", "andorra", "armenia", "austria", "azerbaijan", "belarus", "belgium",
    "bosnia and herzegovina", "bulgaria", "croatia", "cyprus", "czechia", "denmark",
    "estonia", "finland", "france", "georgia", "germany", "greece", "hungary",
    "iceland", "ireland", "italy", "kazakhstan", "kosovo", "latvia", "liechtenstein",
    "lithuania", "luxembourg", "malta", "moldova", "monaco", "montenegro",
    "netherlands", "north macedonia", "norway", "poland", "portugal", "romania",
    "san marino", "serbia", "slovakia", "slovenia", "sweden", "switzerland",
    "turkey", "ukraine", "united kingdom", "vatican city",
    "antigua and barbuda", "bahamas", "barbados", "belize", "canada",
    "dominica","grenada", "haiti", "jamaica", "saint kitts and nevis", "saint lucia",
    "saint vincent and the grenadines", "trinidad and tobago","brazil", 
    "guyana","suriname",
]

api_key = os.getenv("API_KEY")

def merge_artists(**kwargs):
    import os, logging
    import pandas as pd

    ds = kwargs['ds'] # obtener fecha de ejecucion de airflow
    output_path = f"/tmp/artists/top_artists_{ds}.csv"
    
    all_artists = []

    ti = kwargs['ti'] # task instance para acceder a XCom
    
    for country in COUNTRIES:

        country_task_id = country.lower().replace(" ", "_")

        response = ti.xcom_pull(task_ids=f"fetch_top_artists_{country_task_id}")
        
        if not response:
            continue # Si no hay nada en el xcom, pasamos al proximo pais
        import json
        data = json.loads(response)
        artists = data.get("topartists", {}).get("artist", []) # Obtenemos los artistas de la respuesta
        # Guardamos pais, nombre y mbid de cada artista en una lista de diccionarios
        for a in artists:
            all_artists.append({
                "country": country,
                "name": a.get("name"),
                "mbid": a.get("mbid")
            })
        unique_artists = {}
        for a in all_artists:
            key = a["mbid"] if a["mbid"] else a["name"].lower() #se usa como key el mbid, si no tiene se usa el nombre en minusc
            unique_artists[key] = a

    logging.info(f"[merge_artists] {len(unique_artists)} artistas únicos encontrados")
    
    # Guardar los artistas en un CSV
    import pandas as pd
    os.makedirs("/tmp/artists", exist_ok=True)
    df = pd.DataFrame(list(unique_artists.values()))
    df.to_csv(output_path, index=False)
    logging.info(f"[merge_artists] Guardado CSV con {len(df)} artistas en {output_path}")


    return list(unique_artists.values())

def fetch_top_songs_per_artist(**kwargs):
    import requests
    from airflow.providers.http.hooks.http import HttpHook
    import json, os, logging, time
    
    ti = kwargs['ti']
    artists = ti.xcom_pull(task_ids='merge_artists') # Toma la lista de artistas que se guardó temporalmente en el XCom

    if not artists:
        logging.warning("No se encontraron artistas en XCom")
        return
    
    # Creacion del directorio para guardar las canciones en caso de no existir
    os.makedirs(os.path.dirname(SONGS_PATH), exist_ok=True)

    if os.path.exists(SONGS_PATH): # Si el archivo ya existia, entonces lo carga para continuar desde donde se quedó
        with open(SONGS_PATH, "r") as f: 
            songs_data = json.load(f)
        done_tracks = {mbid for entry in songs_data for mbid in entry["top_tracks_mbids"]}
    else:
        songs_data = []
        done_tracks = set()
    
    done_artists = {a["artist_mbid"] for a in songs_data if a.get("artist_mbid")}
    
    hook = HttpHook(http_conn_id='lastfmartist', method='GET')
   
    for i, artist in enumerate(artists):
        mbid = artist.get("mbid")
        # name = artist.get("name")

        if mbid in done_artists:
            continue
        
        # Preparacion de parametros para llamar a la api de lastfm
        params = {
            "method": "artist.gettoptracks",
            "mbid": mbid,
            "api_key": api_key,
            "format": "json",
        }
        
        # ejecucion de la request a la api lastfm
        try:
            res = hook.run("/", data=params)
            data = res.json()
            tracks = data.get("toptracks", {}).get("track", [])
            
            # Toma solo los mbids de las canciones que no se descargaron antes
            mbids_canciones = [t.get("mbid") for t in tracks if t.get("mbid") and t.get("mbid") not in done_tracks]
            
            # Si no hay canciones nuevas pasa al siguiente
            if not mbids_canciones:
                logging.info(f"[{i}] {artist.get('name')}: no hay canciones nuevas.")
                continue
            
            # Agrega al songs_data el artista y sus canciones
            songs_data.append({
                "artist_name": artist.get("name"),
                "artist_mbid": mbid,
                "top_tracks_mbids": mbids_canciones
            })

            done_artists.add(mbid)

            logging.info(f"[{i}] {artist}: {len(mbids_canciones)} canciones guardadas")

            # Se hace un guardado cada 20 artistas para no perder todo el progreso en caso de fallo
            if i % 20 == 0:
                with open(SONGS_PATH, "w") as f:
                    json.dump(songs_data, f)
                logging.info(f"[INFO] Progreso guardado en {SONGS_PATH}")
            
            time.sleep(0.5)

        except Exception as e:
            logging.error(f"Error al procesar artista {artist}: {e}") 
    
    # Guarda el json final en el archivo y en el XCom
    with open(SONGS_PATH, 'w') as f:
        json.dump(songs_data, f)

    total_canciones = sum(len(entry["top_tracks_mbids"]) for entry in songs_data)
    logging.info(f"[INFO] Descarga finalizada con {total_canciones} canciones en total, de {len(songs_data)} artistas.")
    
    kwargs["ti"].xcom_push(key="songs_path", value=SONGS_PATH)
    
    return songs_data

def get_songs_info(**kwargs):
    import os, json, logging, time
    import pandas as pd
    from airflow.providers.http.hooks.http import HttpHook

    # Recupera el songs_data del XCom
    songs_path = kwargs["ti"].xcom_pull(task_ids="fetch_top_songs_per_artist", key="songs_path")
    if not songs_path or not os.path.exists(songs_path):
        logging.error(f"Archivo con canciones no encontrado en {songs_path}")
        return []

    with open(SONGS_PATH, "r") as file:
        songs_data = json.load(file)

    all_songs_records = [] # Aca se va a guardar la info completa de cada cancion
    not_found_records = [] # Canciones que no encontramos
    processed_mbids = set() # los mbids de las canciones que ya fueron procesadas para no repetirlas

    hook = HttpHook(http_conn_id='acousticbrainz', method='GET')

    total_tracks = sum(len(entry["top_tracks_mbids"]) for entry in songs_data)
    logging.info(f"[INFO] Total de tracks con mbid: {total_tracks}")

    # Para cada cancion de cada artista va buscar la info
    for artist_entry in songs_data:
        artist_name = artist_entry["artist_name"]
        artist_mbid = artist_entry["artist_mbid"]

        for track_mbid in artist_entry["top_tracks_mbids"]:
            if not track_mbid or track_mbid in processed_mbids:
                continue

            try:
                endpoint = f"/{track_mbid}/high-level"
                res = hook.run(endpoint)
                if res.status_code != 200:
                    logging.warning(f"No se pudo obtener info de {track_mbid} ({res.status_code})")
                    not_found_records.append({
                        "artist_name": artist_name,
                        "artist_mbid": artist_mbid,
                        "track_mbid": track_mbid,
                        "status_code": res.status_code
                    })
                    continue

                data = res.json()
                
                metadata = data.get("metadata", {})
                tags = metadata.get("tags", {})
                audio_props = metadata.get("audio_properties", {})

                # Extraer la info de metadata
                record = {
                    "artist_name": artist_name,
                    "artist_mbid": artist_mbid,
                    "track_mbid": track_mbid,
                    "title": tags.get("title", [None])[0] if tags.get("title") else None, #En acoustic brainz los tags son listas, por eso usamos [0]
                    "genre": tags.get("genre", [None])[0] if tags.get("genre") else None,
                    "date": tags.get("date", [None])[0] if tags.get("date") else None,
                    "length": audio_props.get("length"),
                    "language": tags.get("language", [None])[0] if tags.get("language") else None
                }

                highlevel = data.get("highlevel", {})
                # Funcinon para acceder a cada probabilidad pasando la key
                def safe_prob(feat, key):
                    return highlevel.get(feat, {}).get("all", {}).get(key)          

                # Extraer la info de high level
                record.update({
                    "danceable": safe_prob("danceability", "danceable"),
                    "happy": safe_prob("mood_happy", "happy"),
                    "sad": safe_prob("mood_sad", "sad"),
                    "relaxed": safe_prob("mood_relaxed", "relaxed"),
                    "party": safe_prob("mood_party", "party"),
                    "acoustic": safe_prob("mood_acoustic", "acoustic"),
                    "instrumental": safe_prob("voice_instrumental", "instrumental"),
                    "bright": safe_prob("timbre", "bright"),
                    "tonal": safe_prob("tonal_atonal", "tonal"),
                    "genre_dortmund": highlevel.get("genre_dortmund", {}).get("value"),
                    "genre_rosamerica": highlevel.get("genre_rosamerica", {}).get("value"),
                    "genre_tzanetakis": highlevel.get("genre_tzanetakis", {}).get("value"),
                })

                all_songs_records.append(record)
                processed_mbids.add(track_mbid)

                logging.info(f"Guardado track {track_mbid} ({artist_name}) con {len(highlevel)} features + metadata")

                time.sleep(0.8)  # para no saturar la API

            except Exception as e:
                logging.error(f"Error procesando track {track_mbid}: {e}")

    # Devolvemos los registros a través de XCom
    kwargs["ti"].xcom_push(key="songs_info", value=all_songs_records)
    return all_songs_records

def merge_songs_to_csv(**kwargs):
    import os, logging
    import pandas as pd

    # Recuperamos todas las canciones de XCom
    ti = kwargs["ti"]
    all_songs_records = ti.xcom_pull(task_ids="get_songs_info", key="songs_info")

    if not all_songs_records:
        logging.warning("No se encontraron registros de canciones para exportar.")
        return None

    # Convertimos la lista de canciones en un DataFrame
    df = pd.DataFrame(all_songs_records)

    os.makedirs("/tmp/songs", exist_ok=True)
    output_csv = "/tmp/songs/songs_info.csv"
    # Creamos el csv a partir del dataframe
    df.to_csv(output_csv, index=False)

    logging.info(f"[INFO] CSV final guardado en {output_csv} con {len(df)} canciones.")
    return output_csv

# DAG
with DAG(
    dag_id='obtener_canciones',
    description='DAG ETL paralelo que une los top artistas por pais, con sus top canciones y su informacion',
    default_args=default_args,
    schedule=None,
    catchup=False,
    tags=['music', 'songs', 'etl']
) as dag:
    tasks_get_artists = [] # son las tareas para obtener el top 50 de artistas de cada pais
    for country in COUNTRIES:
        country_task_id = country.lower().replace(" ", "_")
        t = HttpOperator(
            task_id=f"fetch_top_artists_{country_task_id}",
            http_conn_id="lastfmgeo",
            endpoint=f"?method=geo.getTopArtists&api_key={api_key}&format=json&country={country}",
            method="GET",
            log_response=True,
            do_xcom_push=True, # Para indicar que los guarde en el XCom
        )
        
        tasks_get_artists.append(t)
        print(f"Endpoint: {t.endpoint}")

    start_dummy = EmptyOperator(
        task_id="start_dummy"
    )
    
    merge_artists = PythonOperator(
        task_id='merge_artists',
        python_callable=merge_artists,
    )

    fetch_top_songs_per_artist = PythonOperator(
        task_id='fetch_top_songs_per_artist',
        python_callable=fetch_top_songs_per_artist,
    )

    get_songs_info = PythonOperator(
        task_id='get_songs_info',
        python_callable=get_songs_info,
    )

    merge_songs_to_csv = PythonOperator(
        task_id='merge_songs_to_csv',
        python_callable=merge_songs_to_csv,
    )
    
    start_dummy >> tasks_get_artists >> merge_artists >> fetch_top_songs_per_artist >> get_songs_info >> merge_songs_to_csv
