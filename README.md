# MusicApp: Explorador de Canciones
En este repositorio se encuentra el proyecto integrador elaborado para la cátedra "Ciencia de Datos" en 2025. Se desarrolló un explorador de canciones en conjunto con Lucía Bürky.

## Resumen del proyecto
Se trata de un proyecto que busca analizar y segmentar canciones basándose en sus características acústicas (emocionales, tonales y rítmicas).

Utilizamos técnicas de clustering, reducción de dimensionalidad y detección de animalías para desarrollar un mini sistema que no sólo clasifica las canciones en clusters (Movidas/Tranquilas), sino que también ofrece un explorador interactivo para analizar las características individuales de cada tema y generar recomendaciones de canciones individuales.

El proyecto cumple el ciclo de Data Science, desde la ingeniería de datos hasta el despliegue de una aplicación interactiva. En caso de que se quiera conocer más el paso por paso, en la siguiente sección está detallada cada etapa por la que pasamos durante el desarrollo del proyecto.

## Detalle de cada etapa
Antes de comenzar con cada etapa habíamos definido como idea inicial el desarrollo de un sistema que pudiera tomar un evento determinado indicado por el usuario (por ejemplo una fiesta, un asado e incluso un funeral) y en base a dicho evento brindar una playlist de canciones acordes al mismo. Sin embargo, a lo largo del desarrollo del proyecto fuimos variando la idea inicial.

### 1. Ingeniería de datos aplicada al proyecto
En primer lugar definimos el objetivo del proyecto (sistema de recomendación de canciones según el evento del usuario) y luego comenzamos a buscar de dónde podríamos sacar los datos. Encontramos dos APIs que nos iban a servir:
- **Last.fm**: para obtener un listado con los 50 artistas más populares de cada país, para luego con esos artistas obtener las 50 canciones más populares de cada uno. Para ello, utilizamos dos endpoints (geo.getTopArtists y artist.getTopTracks). Nos dimos cuenta de que cada canción obtenida contenía un MBID, que es el mismo que se utiliza tanto en MusicBrainz como en AcousticBrainz. Además, en primera instancia decidimos utilizar únicamente países hispanohablantes y otros de América, pero luego lo ampliamos, agregando países de Europa y África.
- **AcousticBrainz**: utilizando el MBID obtenido en cada canción anteriormente, buscamos los datos "high-level" de cada canción dentro de esta otra API. Obtuvimos datos relacionados con las características de las canciones, como "happy", "sad", "danceable", "acoustic", etc.

Una vez teniendo las dos APIs qu serían nuestras fuentes de datos, comenzamos a desarrollar el siguiente DAG con Airflow.:
<img width="1241" height="261" alt="image" src="https://github.com/user-attachments/assets/5a0d4aac-98f4-41bf-b269-5c42870cca97" />

En los siguientes puntos se detalla cada una de las tareas del DAG:
- _start_dummy_: es una tarea vacía para indicar el inicio del DAG.
- _fetch_top_artists_(pais)_: es un HttpOperator que hace uso del endpoint geo.getTopArtists explicado anteriormente, para obtener los artistas más escuchados por país. Se ha pensado que haya una tarea que realice este trabajo por cada país del listado, y se guarda la información obtenida en el XCom de cada una de ellas.
- _merge_artists_: es un PythonOperator encargado de juntar la información obtenida en la tarea anterior, y colocarla en un CSV y en el XCom. Por cada artista obtenido se guarda el país, MBID y nombre del artista.
- _fetch_top_songs_per_artist_: se trata de un PythonOperator que se encarga de buscar las 50 canciones más populares de cada uno de los artistas que se encuentran en el arreglo mencionado en el punto anterior. El MBID de cada canción se guarda en un CSV y en el XCom de la tarea.
- _fetch_songs_info_: es un PythonOperator encargado de buscar la información (metadata y high level) referida a cada una de las canciones obtenidas en la tarea anterior. El resultado se guarda en el XCom de la tarea.
- _merge_songs_to_csv_: se trata de un PythonOperator encargado de generar el CSV final que contiene toda la información relevante de las canciones. Las columnas que componen el archivo son: title, track_mbid, artist_name, artist_mbid, genre, genre_rosamerica, genre_dortmund, genre_electronic, genre_tzanetakis, length, date, language, danceable, happy, sad, party, relaxed, acoustic, instrumental, tonal, bright

Inicialmente, el csv generado contenía un montón de columnas, pero a medida que fuimos avanzando en cada etapa fuimos eliminando, modificando y agregando columnas.


### 2. Análisis exploratorio sobre el conjunto de datos
Para esta entrega la idea era explorar y conocer el dataset, limpiar datos que fueran innecesarios o problemáticos y la realización de hipótesis preliminares para tener en cuenta en próximas etapas.
El archivo relacionado con esta etapa se llama "_segunda_entrega.ipynb_"
Dividimos esta etapa en dos partes: preprocesamiento y análisis exploratorio.

#### Preprosesamiento
Inicialmente realizamos una limpieza de los datos ejecutando un pipeline, eliminamos datos nulos, columnas innecesarias y también normalizamos los datos como por ejemplo las fechas.
Funciones que componen el pipeline:
1. Explorar: permite conocer la cantidad de registros de datos que teníamos, cantidad de columnas, tipos de datos y cantidad de nulos.
2. Limpiar: luego de analizar las columnas que podían llegar a darnos problemas, las eliminamos.
3. Arreglo de duración: transformamos la duración, ya que antes se encontraba en segundos y nosotras queríamos tenerla en minutos.
4. Arreglo de fechas: debido a que la API de donde descargamos los datos es open source, muchas de las canciones poseían fechas extrañas con años muy antigüos (ej. 501 para una canción de Sabrina Carpenter). Es por ello que modificamos esos valores extraños y en su lugar colocamos el valor de la moda según el género de la canción. Adem+ás, hicimos el mismo procedimiento para canciones que tenían fechas nulas.
5. Agregado de décadas: en caso de que pudiese servir, decidimos agregar la década como columna a las canciones. Esto teniendo en cuenta desde 1910 hasta 2020.
6. Longitud del título: en caso de poder encontrar futuras hipótesis relacionadas con el título de las canciones, decidimos agregar una columna que indicara la cantidad de caracteres que presentaba el mismo.
7. Eliminación de la columna genre: debido a que esa columna presentaba muchos valores nulos y en otros casos presentaba cadenas que no indicaban el género sino que decían cosas sin sentido, decidimos eliminarla y utilizar alguno de los otros géneros.
8. Limpieza/Normalización de géneros: para que se comprendiera mejor cada género, decidimos colcar su nombre completo. Por ejemplo, para el caso de "hip", colocamos "Hip-Hop".

#### Análisis exploratorio estructurado
Realizamos diferentes análisis:
- Correlaciones entre las variables, tanto de forma géneral como para cada género.
- Distribución de géneros de canciones: en este caso observamos que en el dataset inicial (obtenido por el top de artistas), los datos estaban bastante desbalanceados, contando con muchas canciones de Pop, Rythmic y Rock y casi ninguna de Jazz y Classic. Esto luego lo arreglamos consiguiendo muchas más canciones (más adelante se comenta).
- Análisis de las propiedades: vimos los valores más altos de cada propiedad, y para cada propiedad tomando las 100 canciones con valores más altos, analizamos el género de las mismas.
- Análisis de las características para cada género.
- Hipótesis particulares (a modo de prueba e ideas).

### 3. Modelado y métricas iniciales
Inicialmente hicimos un archivo para el entrenamiento de los modelos (tercera_entrega.ipynb) y luego, para poder facilitar algunas cosas para la siguiente entregam, modificamos ese archivo (tercera_entrega_modificada.ipynb).
La idea de esta entrega era realizar al menos 3 modelos distintos de Machine Learning. Por lo que nosotras decidimos aplicar tanto aprendizaje supervisado como no supervisado.

#### Aprendizaje supervisado para clasificación según el género
Inicialmente queríamos ver si podíamos predecir el género de las canciones. Para ello probamos 3 modelos distintos:
- K-Neighbors Classifier (KNN)
- Random Forest Classifier
- Gradient Boosting (XGBoost)

Luego, para cada modelo realizamos el ajuste de hiperparámetros, y finalmente para el modelo elegido decidimos aplicar balanceo de clases (ya que inicialmente nuestras clases estaban un poco desbalanceadas).
Terminamos concluyendo que el mejor modelo para este caso era el **Random Forest** base, es decir, sin ajuste de hiperparámetros y sin balanceo de clases. En caso de que se desee ver el análisis realizado y las conclusiones obtenidas, se puede ver en los archivos de esta etapa.

Sin embargo, no nos encontramos muy conformes con los resultados obtenidos, a continuación se adjunta la matriz de confusión (sin normalizar):

<img width="440" height="380" alt="image" src="https://github.com/user-attachments/assets/41891f13-ea6f-42f4-98d7-ad0d952949db" />

#### Aprendizaje no supervisado para clasificación de canciones
Es importante aclarar que para poder realizar esta entrega correctamente y no obtener malos resultados, tuvimos que descargar uno de los archivos de AcousticBrainz que contenía miles de canciones (cada una siendo un archivo JSON), y con un colab transformar todas estas canciones en un único CSV. Se deja el código de lo que hicimos en el archivo "_obtener_mas_canciones.ipynb_".

Aplicamos reducción de dimensionalidad con PCA, obteniendo que lo mejora era utilizar únicamente dos componentes. Luego, aplicamos clustering y descubrimos que lo mejor también era dividir las canciones en dos clusters, que luego nosotras describimos como:
- Cluster movido (0)
- Cluster tranquilo (1)

Luego graficamos las características de las canciones de cada cluster, permitiendo demostrar el por qué nosotras los separamos en "movido" y "tranquilo":

<img width="452" height="399" alt="image" src="https://github.com/user-attachments/assets/57caff82-70ec-4891-b427-50c2ca11ec4c" />

Y finalmente, para aplicar algo distinto, utilizamos una técnica de detección de anomalías (en base a las caractertísticas de las canciones) utilizando el algoritmo Isolation Forest.

### 4. Visualización final e integración del proyecto
Para la útlima entrega, inicialmente hicimos algunos gráficos en un colab utilizando Altair, y luego decidimos pasar todo lo que habíamos observado a una aplicación de Streamlit.
El archivo donde realizamos dichos gráficos es "_cuarta_entrega.ipynb_". Para la realización de dichos gráficos, tuvimos en cuenta los principios de la gramática de gráficos vistos en clase, con el objetivo de comunicar de manera clara los hallazgos más relevantes del proceso de análisis y modelado. 

Luego desarrollamos la aplicación de Streamlit, que se encuentra en el archivo "_app.py_". Además, desplegamos dicha aplicación: https://cancionesapp-pn7j277szrdnzyddqkn8en.streamlit.app/
Dentro de la misma, en la pestaña de introducción al proyecto se explican brevemente las etapas por las cuales pasamos. Además, en la pestaña de referencias se explica cada concepto para un mejor entendimiento.

## Herramientas utilizadas
<div align="center">
  <div align="center">
    <img width="200" height="115" alt="image" src="https://github.com/user-attachments/assets/d72dd099-c153-4d47-bc66-ffd6224338a5" />
    <p>Airflow (con Astro CLI)</p>
  </div>
  <div align="center">
     <img width="75" height="75" alt="image" src="https://github.com/user-attachments/assets/e0dbfdfd-bbf5-4521-8f50-9ab353fbdfd1" />
    <img width="75" height="75" alt="image" src="https://github.com/user-attachments/assets/fa0303da-77a9-45cf-9417-58c5257d3078" />
    <img width="150" height="75" alt="image" src="https://github.com/user-attachments/assets/384b0b00-11f7-4151-814d-9d4712f454d2" />
    <img width="75" height="75" alt="image" src="https://github.com/user-attachments/assets/3ec740df-9f96-4d6f-9f02-2e8a8426b3e1" />
    <p>Python, Pandas, Scikit-learn, Altair</p>
  </div>
 <div align="center">
    <img width="190" height="100" alt="image" src="https://github.com/user-attachments/assets/5dc60860-ce13-49d9-ad95-c4674b2d8741" />
    <p>Streamlit y Streamlit Cloud</p>
  </div>
</div>
