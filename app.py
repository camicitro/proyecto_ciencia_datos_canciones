import streamlit as st
import pandas as pd
import altair as alt
import base64
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import streamlit.components.v1 as components
from sklearn.neighbors import NearestNeighbors
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import MinMaxScaler

alt.data_transformers.enable("vegafusion")
alt.renderers.enable("mimetype")

# ========================
# CONFIGURACIÓN GENERAL
# ========================
st.set_page_config(page_title="Explorador de Canciones", layout="wide")

st.markdown(
    """
    <style>
    
    h1, h2, h3 {
        color: #333333;
    }

    /* INICIO: ESTILOS PARA LA SIDEBAR (SOLUCIÓN) */

    /* 1. Oculta el título del st.radio (el "Ir a:") */
    .stRadio > label:first-child {
        display: none;
    }
    
    /* 2. Oculta los círculos de los radio buttons */
    div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }
    
    /* 3. Estilo por defecto de las opciones de la sidebar */
    div[role="radiogroup"] > label {
        padding: 10px 15px; /* Relleno interior */
        margin: 5px 0; /* Espacio vertical */
        border-radius: 8px; /* Bordes redondeados */
        transition: background-color 0.2s;
    }
    
    /* 4. Estilo de la opción NO seleccionada al pasar el mouse (hover) */
    div[role="radiogroup"] > label:hover {
        background-color: #f0f0f0; /* Un gris muy claro al pasar el mouse */
    }
    
    /* 5. Estilo de la opción SELECCIONADA (el fondo gris oscuro) */
    div[role="radiogroup"] > label:has(input:checked) {
        background-color: #e0e0e0; /* Gris más oscuro para la opción activa */
        font-weight: 600; /* Hace el texto un poco más grueso */
        color: #333333;
    }

    /* FIN: ESTILOS PARA LA SIDEBAR */
    
    </style>
    """,
    unsafe_allow_html=True
)

# ========================
# SIDEBAR DE NAVEGACIÓN
# ========================
st.sidebar.title("🎧 Menú")
page = st.sidebar.radio("", ["Introducción al proyecto","Explorador de canciones", "Exploración libre","Referencias"])


# ==============================
# OPCIÓN EXPLORADOR DE CANCIONES
# ==============================
if page == "Explorador de canciones":
    st.title("🎵 Explorador de Canciones")

    df = pd.read_csv("songs_final_cortito_para_pruebas.csv")

    if 'display_name' not in df.columns:
        df['display_name'] = df['title'] + " - " + df['artist_name']

    options_list = sorted(df['display_name'].tolist())

    st.markdown("### Seleccioná una canción para explorar sus características:")

    default_track_id = "85f842b8-6817-4721-a85c-8b4dde1e8814"

    if default_track_id in df['track_mbid'].values:
        default_display_name = df.loc[df['track_mbid'] == default_track_id, 'display_name'].iloc[0]
        default_index = options_list.index(default_display_name) if default_display_name in options_list else 0
    else:
        default_index = 0

    selected_option = st.selectbox("", options_list, index=default_index)
    selected_song = df[df["display_name"] == selected_option].iloc[0]

    st.markdown("---")

    def get_base64_image(image_path):
        with open(image_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode()
        return encoded

    genre = selected_song["genre_rosamerica"].lower()
    cluster = selected_song["cluster"]
    backgrounds_generos = {
        "pop": "images/pop.png",
        "rock": "images/rock.jpg",
        "jazz": "images/jazz.jpg",
        "dance": "images/dance.jpg",
        "hip-hop": "images/hiphop.jpg",
        "classic": "images/classic.jpg",
        "rhythmic": "images/rhythmic.png",
    }
    backgrounds_clusters = {
        1: "images/tranquilo.gif",
        0: "images/movido.gif",
    }

    background_image_generos = backgrounds_generos.get(genre, "images/default.jpg")
    base64_image_generos = get_base64_image(background_image_generos)

    background_image_clusters = backgrounds_clusters.get(cluster, "images/default.jpg")
    base64_image_clusters = get_base64_image(background_image_clusters)

    cluster_label = "0 (Movido)" if cluster == 0 else "1 (Tranquilo)"

    html_cards = f"""
    <div style="display: flex; justify-content: space-around; margin-top: 20px; margin-bottom: 10px; font-family: 'Source Sans Pro', sans-serif;">
        <div style="position: relative; width: 30%; height: 200px; border-radius: 15px; overflow: hidden; box-shadow: 0px 2px 10px rgba(0,0,0,0.4);">
            <div style="position: absolute; inset: 0; background-image: url('data:image/jpeg;base64,{base64_image_generos}'); background-size: cover; background-position: center; opacity: 0.5;"></div>
            <div style="position: relative; z-index: 1; color: white; text-align: center; font-weight: bold; text-shadow: 1px 1px 4px rgba(0,0,0,0.8); top: 50%; transform: translateY(-50%);">
                <h2>Género</h2>
                <h1>{selected_song['genre_rosamerica']}</h1>
            </div>
        </div>

        <div style="position: relative; width: 30%; height: 200px; border-radius: 15px; overflow: hidden; box-shadow: 0px 2px 10px rgba(0,0,0,0.4);">
            <div style="position: absolute; inset: 0; background-image: url('data:image/gif;base64,{base64_image_clusters}'); background-size: cover; background-position: center; opacity: 0.5;"></div>
            <div style="position: relative; z-index: 1; color: white; text-align: center; font-weight: bold; text-shadow: 1px 1px 4px rgba(0,0,0,0.8); top: 50%; transform: translateY(-50%);">
                <h2>Cluster</h2>
                <h1>{cluster_label}</h1>
            </div>
        </div>

        <div style="position: relative; width: 30%; height: 200px; border-radius: 15px; overflow: hidden; background-color: {'#e57373' if selected_song['anomaly'] == -1 else '#81c784'}; box-shadow: 0px 2px 10px rgba(0,0,0,0.4); color: white; text-align: center; font-weight: bold; text-shadow: 1px 1px 4px rgba(0,0,0,0.8); display: flex; flex-direction: column; justify-content: center;">
            <h2>Anomalía</h2>
            <h1>{f"Anómala ({selected_song['porcentaje_anomalia']*100:.3f}%)" if selected_song["anomaly"] == -1 else "No anómala"}</h1>
        </div>
    </div>
    """
    features = ["sad","happy","party","relaxed","acoustic","danceable","tonal","bright","instrumental"]
    # Mostrar las tarjetas y capturar clics
    components.html(html_cards, height=230)
    
    # Botones para ver las caracteristicas de cada cosa
    col1, col2, col3 = st.columns(3, gap="medium")

    st.markdown("""
    <style>
    div[data-testid="stButton"] {
        display: flex;
        justify-content: center;
    }
    div[data-testid="stButton"] > button {
        min-width: 80%;
        max-width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)
    # Botón GÉNERO 
    with col1:
        inner_left, inner_center, inner_right = st.columns([1, 2, 1])
        with inner_center:
            clicked_genre = st.button(f"Ver características", key="genre_button")

    # Botón CLUSTER 
    with col2:
        inner_left, inner_center, inner_right = st.columns([1, 2, 1])
        with inner_center:
            clicked_cluster = st.button(f"Ver características", key="cluster_button")

    # Botón ANOMALÍA 
    with col3:
        if selected_song["anomaly"] == -1:
            inner_left, inner_center, inner_right = st.columns([1, 2, 1])
            with inner_center:
                clicked_anomaly = st.button("Ver detalles", key="anomaly_button")
            if clicked_anomaly:
                st.session_state.show_anomaly_chart = not st.session_state.get("show_anomaly_chart", False)
        else:
            st.session_state.show_anomaly_chart = False

    # Alternar gráficos 
    if clicked_genre:
        st.session_state.show_genre_chart = not st.session_state.get("show_genre_chart", False)
    if clicked_cluster:
        st.session_state.show_cluster_chart = not st.session_state.get("show_cluster_chart", False)
    
    # Mostrar gráficos 
    if st.session_state.get("show_genre_chart", False):
        st.markdown("---")
        st.subheader(f"Promedio de características del género: {selected_song['genre_rosamerica']}")

        genre_df = df[df["genre_rosamerica"] == selected_song["genre_rosamerica"]]
        genre_avg = genre_df[features].mean().reset_index()
        genre_avg.columns = ["Característica", "Valor promedio"]

        color = "#E66E6E" if cluster == 0 else "#6496E8"

        chart_genre_avg = (
            alt.Chart(genre_avg)
            .mark_bar(color=color, size=25)
            .encode(
                y=alt.Y("Característica:N", sort="-x", title=""),
                x=alt.X("Valor promedio:Q", scale=alt.Scale(domain=[0, 1]), title="Valor promedio"),
                tooltip=["Característica", "Valor promedio"]
            )
            .properties(width=600, height=400,
                        title=f"Promedio de características musicales - {selected_song['genre_rosamerica']}")
        )
        st.altair_chart(chart_genre_avg, use_container_width=True)

    if st.session_state.get("show_cluster_chart", False):
        st.markdown("---")
        st.subheader(f"Promedio de características del cluster {cluster_label}")

        cluster_df = df[df["cluster"] == cluster]
        cluster_avg = cluster_df[features].mean().reset_index()
        cluster_avg.columns = ["Característica", "Valor promedio"]

        color = "#E66E6E" if cluster == 0 else "#6496E8"

        chart_cluster_avg = (
            alt.Chart(cluster_avg)
            .mark_bar(color=color, size=25)
            .encode(
                y=alt.Y("Característica:N", sort="-x", title=""),
                x=alt.X("Valor promedio:Q", scale=alt.Scale(domain=[0, 1]), title="Valor promedio"),
                tooltip=["Característica", "Valor promedio"]
            )
            .properties(width=600, height=400,
                        title=f"Promedio de características musicales - Cluster {cluster_label}")
        )
        st.altair_chart(chart_cluster_avg, use_container_width=True)

    if st.session_state.get("show_anomaly_chart", False):
        st.markdown("---")
        st.subheader("Características con combinaciones inusuales")

        # Calcular correlaciones globales
        corr = df[features].corr()

        # Valores de la canción seleccionada
        song_vals = selected_song[features]

        # Detectar pares conflictivos: correlación negativa + ambos valores altos
        pairs = []
        conflict_features = set()

        for i in range(len(features)):
            for j in range(i+1, len(features)):
                f1, f2 = features[i], features[j]
                corr_val = corr.loc[f1, f2]
                if corr_val < -0.4 and song_vals[f1] > 0.6 and song_vals[f2] > 0.6:
                    pairs.append((f1, f2, corr_val))
                    conflict_features.update([f1, f2])

        if not conflict_features:
            st.info("Esta canción no presenta combinaciones conflictivas destacadas.")
        else:
            conflict_features = list(conflict_features)

        # === Gráfico de barras de características conflictivas ===
        conflict_df = pd.DataFrame({
            "Característica": conflict_features,
            "Valor": [selected_song[f] for f in conflict_features]
        })

        chart_conflicts = (
            alt.Chart(conflict_df)
            .mark_bar(size=40, color="#f5b342")
            .encode(
                x=alt.X("Valor:Q", scale=alt.Scale(domain=[0, 1]), title="Valor de la característica"),
                y=alt.Y("Característica:N", sort="-x", title=""),
                tooltip=["Característica", "Valor"]
            )
            .properties(
                width=500,
                height=350,
                title=alt.TitleParams(
                    text="Características que contribuyen a la anomalía",
                    anchor="middle",
                    fontSize=18,
                    fontWeight=500
                )
            )
        )

        st.altair_chart(chart_conflicts, use_container_width=True)

        st.markdown(
            """
            <div style="text-align:center; font-size:15px; color:gray; margin-top:-10px;">
                Estas características presentan valores altos simultáneamente (generando conflicto),
                aunque suelen estar negativamente correlacionadas.<br>
                Esa combinación poco común hace que la canción se considere <strong>inusual</strong>.
            </div>
            """,
            unsafe_allow_html=True
        )




    st.markdown("---")

    # Para caracteristicas de la cancion
    song_features = pd.DataFrame({
        "feature": features,
        "value": [selected_song[f] for f in features]
    })
    color = "#E66E6E" if cluster == 0 else "#6496E8"

    chart_features = (
        alt.Chart(song_features)
        .mark_bar(size=25, color=color)
        .encode(
            x=alt.X("value:Q", title="Valor", scale=alt.Scale(domain=[0, 1])),
            y=alt.Y("feature:N", sort="-x", title=""),
            tooltip=["feature", "value"]
        )
        .properties(width=450, height=400)
    )

    st.subheader("Características de la canción")
    st.altair_chart(chart_features, use_container_width=True)

    st.markdown("---")
    st.subheader("Canciones similares")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[features])
    knn = NearestNeighbors(n_neighbors=6)
    knn.fit(X_scaled)

    idx_selected = df.index[df["display_name"] == selected_option][0]
    distancias, indices = knn.kneighbors([X_scaled[idx_selected]])
    similares_knn = df.iloc[indices[0][1:]][["title","artist_name","genre_rosamerica","cluster"]]
    similares_knn = similares_knn.rename(columns={"title": "Título", "artist_name": "Artista", "genre_rosamerica": "Género", "cluster": "Cluster"})

    st.dataframe(similares_knn, use_container_width=True)

# ========================
# OPCIÓN REFERENCIAS
# ========================
elif page == "Referencias":
    st.title("📘 Referencias")
    st.markdown("---")

    html_referencias = """
    
<style>
    .container-analisis {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 20px 40px 20px; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    
    .section h2 {
        color: #333333; 
        font-size: 1.5em; 
        margin-bottom: 25px;
        border-bottom: 3px solid #333333; 
        padding-bottom: 10px;
    }

    .section {
        background: #ffffff;
        border-radius: 16px;
        padding: 30px;
        margin-bottom: 30px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.1);
    }
    
    .intro-text {
        font-size: 1.05em;
        line-height: 1.7;
        color: #555555;
        margin-bottom: 20px;
    }

    
    .clusters-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 25px;
        margin-top: 20px;
    }

    .cluster-card {
        border-radius: 12px;
        padding: 25px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .cluster-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    
    .cluster-0 {
        background: linear-gradient(135deg, #FFC4C4 0%, #FFAAAA 100%);
        color: #333333; 
    }

    .cluster-1 {
        background: linear-gradient(135deg, #C4E4FF 0%, #AABEFF 100%);
        color: #333333; 
    }
    
    .cluster-card h3 {
        font-size: 1.4em;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
        color: #333333;
    }
    
    .cluster-icon {
        font-size: 1.8em;
    }

    .cluster-card p {
        line-height: 1.6;
        font-size: 1em;
    }

    .pca-components {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 25px;
        margin-top: 20px;
    }
    
    .pca-card {
        border-radius: 12px;
        padding: 25px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }

    .pca-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }

    .pca-1 {
        background: linear-gradient(135deg, #e6f7f5 0%, #fff0f5 100%);
    }

    .pca-2 {
        background: linear-gradient(135deg, #fffbe6 0%, #ffe6cc 100%); 
    }

    .characteristics-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 20px;
        overflow: hidden;
        border-radius: 8px;
    }

    .characteristics-table thead {
        background: #f0f0f0; 
        color: #333333;
    }

    .characteristics-table th {
        padding: 12px 18px;
        text-align: left;
        font-weight: 600;
        font-size: 1em;
        border-bottom: 1px solid #cccccc;
    }

    .characteristics-table td {
        padding: 14px 18px;
        border-bottom: 1px solid #e0e0e0;
        line-height: 1.5;
    }

    .characteristics-table tbody tr:hover {
        background-color: #f9f9f9;
    }

    .characteristic-name {
        font-weight: bold; 
        color: #333333; 
        font-size: 1em;
    }
    
    @media (max-width: 768px) {
        .section {
            padding: 15px;
        }

        .section h2 {
            font-size: 1.4em;
        }
    }

    
</style>

<div class="container-analisis">
    <div class="section">
        <h2 id="cluster-title">Análisis de los clusters</h2>
        <p class="intro-text">El modelo de agrupamiento permitió identificar dos grandes grupos de canciones según sus características musicales:</p>
        <div class="clusters-grid">
            <div class="cluster-card cluster-0">
                <h3><span class="cluster-icon">💃</span> Cluster 0 (Movido)</h3>
                <p>Agrupa canciones con valores más altos en "party" y "danceable", asociadas a un ritmo activo, enérgico y festivo. Suelen incluir géneros como Pop, Rock y Dance, y transmiten una sensación dinámica y alegre, ideales para ambientes sociales o de celebración.</p>
            </div>
            <div class="cluster-card cluster-1">
                <h3><span class="cluster-icon">😴</span> Cluster 1 (Tranquilo)</h3>
                <p>Reúne canciones con valores más altos en "relaxed", "acoustic", "bright" y "tonal", reflejando una atmósfera serena, melódica y armónica. Predominan géneros como Rock clásico, Jazz y música clásica, destacándose por su mayor riqueza tonal y menor intensidad rítmica.</p>
            </div>
        </div>
        <p class="intro-text" style="margin-top: 25px;">En conjunto, los dos clusters representan dos modos de experiencia musical predominantes: uno energético y estimulante, y otro tranquilo y contemplativo.</p>
    </div>

    <div class="section">
        <h2 id="pca-title">Componentes principales del PCA</h2>
        <p class="intro-text">El análisis de componentes principales permitió reducir las características musicales a dos dimensiones fundamentales, que resumen la mayor parte de la variabilidad entre canciones:</p>
        <div class="pca-components">
            <div class="pca-card pca-1">
                <h3><span class="pca-icon">🧘‍♀️</span> Componente 1 – Tranquilidad</h3>
                <p>Presenta cargas positivas en "sad", "relaxed" y "acoustic", y negativas en "party" y "danceable". Esto significa que valores altos corresponden a canciones relajadas, melancólicas y acústicas, mientras que valores bajos indican temas festivos y bailables. Representa el nivel de energía o calma emocional de la canción.</p>
            </div>
            <div class="pca-card pca-2">
                <h3><span class="pca-icon">🌞</span> Componente 2 – Positividad emocional</h3>
                <p>Muestra cargas positivas en "happy", "tonal" y "bright", y negativas en "instrumental" y "relaxed". Las canciones con valores altos tienden a ser más alegres, luminosas y expresivas, mientras que las de valores bajos son más instrumentales, introspectivas o sobrias. Representa el grado de expresividad o brillo emocional.</p>
            </div>
        </div>
        <p class="intro-text" style="margin-top: 25px;">Estas dos dimensiones —Tranquilidad y Positividad emocional— conforman un mapa sonoro que permite visualizar el espacio musical de cada canción y entender su posición dentro de los clusters.</p>
    </div>

    <div class="section">
        <h2 id="table-title">Descripción de las características musicales</h2>
        <table class="characteristics-table">
            <thead>
                <tr>
                    <th>Característica</th>
                    <th>Descripción</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="characteristic-name">Relaxed</td>
                    <td>Indica el nivel de serenidad o calma de una canción. Valores altos corresponden a temas lentos o suaves.</td>
                </tr>
                <tr>
                    <td class="characteristic-name">Bright</td>
                    <td>Representa la luminosidad o "brillo" del sonido, asociado a tonos agudos y alegres.</td>
                </tr>
                <tr>
                    <td class="characteristic-name">Sad</td>
                    <td>Evalúa el nivel de melancolía o tristeza percibida en la canción.</td>
                </tr>
                <tr>
                    <td class="characteristic-name">Acoustic</td>
                    <td>Mide cuánto predomina el uso de instrumentos acústicos frente a electrónicos.</td>
                </tr>
                <tr>
                    <td class="characteristic-name">Happy</td>
                    <td>Describe el grado de positividad emocional o alegría transmitida.</td>
                </tr>
                <tr>
                    <td class="characteristic-name">Party</td>
                    <td>Refleja el carácter festivo o de celebración del tema.</td>
                </tr>
                <tr>
                    <td class="characteristic-name">Instrumental</td>
                    <td>Indica si la canción es principalmente instrumental (sin voz).</td>
                </tr>
                <tr>
                    <td class="characteristic-name">Danceable</td>
                    <td>Evalúa cuán fácil resulta bailar la canción, en función del ritmo y la percusión.</td>
                </tr>
                <tr>
                    <td class="characteristic-name">Tonal</td>
                    <td>Mide la estabilidad armónica o claridad tonal del tema (opuesto a lo atonal o experimental).</td>
                </tr>
            </tbody>
        </table>
    </div>
    <div class="section">
        <h2 id="genre-title">Información sobre Géneros Musicales</h2>
        <p class="intro-text">Los géneros han sido obtenidos de la base de datos de AcousticBrainz y clasificados bajo
            la taxonomía de Rosamerica. Esta tabla describe las características generales de los géneros predominantes
            en el dataset:</p>
        <table class="characteristics-table">
            <thead>
                <tr>
                    <th>Género</th>
                    <th>Descripción Representativa</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="characteristic-name">Pop</td>
                    <td>Música popular con estructuras simples, melódica y enfocada en el mainstream. Frecuentemente
                        asociada al Cluster Movido.</td>
                </tr>
                <tr>
                    <td class="characteristic-name">Rock</td>
                    <td>Amplia gama de estilos centrados en la guitarra eléctrica, batería y bajo. Puede variar entre
                        Movido (enérgico) y Tranquilo (baladas o clásico).</td>
                </tr>
                <tr>
                    <td class="characteristic-name">Rhythmic</td>
                    <td>Géneros con énfasis en ritmos complejos y percusión fuerte, como R&B contemporáneo, a menudo
                        orientados al baile (Movido).</td>
                </tr>
                <tr>
                    <td class="characteristic-name">Dance</td>
                    <td>Música electrónica de baile (EDM, House, Techno). Altamente "party" y "danceable" (generalmente se asocian al Cluster
                        Movido).</td>
                </tr>
                <tr>
                    <td class="characteristic-name">Classic</td>
                    <td>Música Clásica. Caracterizada por la riqueza tonal, orquestación y valores altos en "relaxed"
                        (mayoritariamente se asocian al Cluster Tranquilo).</td>
                </tr>
                <tr>
                    <td class="characteristic-name">Jazz</td>
                    <td>Estilos caracterizados por la improvisación, ritmos sincopados y armonías complejas. Tiende a
                        ser "relaxed" y "tonal" (suelen presentarse dentro del Cluster Tranquilo).</td>
                </tr>
                <tr>
                    <td class="characteristic-name">Hip-Hop</td>
                    <td>Música basada en el sampleo y ritmos programados, con un fuerte enfoque en el rap. Usualmente
                        es bailable y rítmico.</td>
                </tr>
            </tbody>
        </table>
    </div>

    <div class="section">
        <h2 id="anomaly-title">Detección y Porcentaje de Anomalías</h2>
        <div class="pca-components">
            <div class="pca-card pca-1" style="background: #ffe6e6; border: 1px solid #ffaaaa;">
                <h3><span class="pca-icon">🚨</span> ¿Qué es una Canción Anómala?</h3>
                <p>Una canción es considerada anómala cuando sus características musicales (sad, happy,
                    danceable, etc.) se desvían significativamente del patrón general o esperado del resto del
                    dataset. Es un caso atípico que no encaja bien en ninguno de los grupos principales.</p>
                <p>Esto no significa que sea "mala", sino que es única o inusual en su composición, como una
                    canción de Jazz extremadamente "party" o un tema que contenga niveles altos tanto de "happy" como de "sad".</p>
            </div>
            <div class="pca-card pca-2" style="background: #e6f9ff; border: 1px solid #aad8ff;">
                <h3><span class="pca-icon">📈</span> Clasificación y Porcentaje</h3>
                <p>Utilizamos el algoritmo Isolation Forest para identificar estas anomalías.
                    Este método aísla los puntos que están lejos de la mayoría, clasificándolos con anomaly = -1.</p>
                <p>El porcentaje de anomalía se calcula a partir del score de la distancia de aislamiento,
                    escalado entre 0% (totalmente normal) y 100% (la más anómala de todas). Esto indica qué tan lejos
                    está una canción del "corazón" del conjunto de datos.</p>
            </div>
        </div>
    </div>
</div>

    """

    components.html(html_referencias, height=3700, scrolling=False)

# ===============================
# OPCIÓN INTRODUCCION AL PROYECTO
# ===============================
elif page == "Introducción al proyecto":
    #st.title("MusicApp")
    st.markdown(
        """
        <h1 style="
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-weight: 800;
            background: linear-gradient(90deg, #ff6b6b, #5f9eff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: left;
            font-size: 56px;
        ">
            🎵 MusicApp
        </h1>
        """,
        unsafe_allow_html=True
    )
    st.subheader("Proyecto Integrador de Ciencia de Datos - Grupo 8")
    st.text("Lucía Bürky, Camila Citro")

    st.markdown("---")
    html_intro = """
    <style>
        .container-intro {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px 40px 20px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #333;
        }

        .section {
            background: #ffffff;
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.1);
        }

        .section h2 {
            border-bottom: 3px solid #333333;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }

        .intro-text {
            font-size: 1.05em;
            line-height: 1.7;
            margin-bottom: 20px;
        }
    </style>

    <div class="container-intro">
        <div class="section">
            <h2>📌 Descripción general</h2>
            <p class="intro-text">
            Este proyecto forma parte del <strong>Proyecto Integrador de Ciencia de Datos</strong> y tiene como objetivo 
            construir un sistema de análisis musical que permita explorar, clasificar y recomendar canciones 
            según sus características sonoras.
            </p>
            <p class="intro-text">
            Utilizamos la base de datos de <strong>AcousticBrainz</strong>, que ofrece información técnica sobre millones de canciones. 
            Sin embargo, es importante aclarar que a pesar de tener muchísimas canciones, AcousticBrainz está limitado ya que actualmente no está en uso. Es decir, se han cargado canciones en dicha plataforma hasta el año 2022, es por ello que aquí no se encontrarán canciones actuales.
            </p>
        </div>

        <div class="section">
            <h2>⚙️ Proceso de desarrollo</h2>
            <p class="intro-text">
            El desarrollo se dividió en distintas etapas:
            </p>
            <ol class="intro-text">
                <li><strong>Extracción y procesamiento de datos:</strong> Airflow automatizó la obtención de canciones desde APIs externas. Se utilizaron dos APIs: AcousticBrainz y Last.fm</li>
                <li><strong>Análisis exploratorio:</strong> Realizamos un <em>EDA</em> en Google Colab formulando hipótesis sobre la relación entre las características de las cancioens y sus géneros musicales.</li>
                <li><strong>Aprendizaje supervisado:</strong> Entrenamos distintos modelos para predecir el género de una canción, siendo el <em>Random Forest</em> el de mejor desempeño, aunque con limitaciones debido a la cantidad de géneros disponibles.</li>
                <li><strong>Aprendizaje no supervisado:</strong> Aplicamos <em>PCA</em> para reducir dimensiones y descubrimos que lo mejor era utilizar dos componentes, y que las mismas representaban la <em>tranquilidad</em> y la <em>positividad emocional</em> de las canciones. A partir de ellas, se identificaron dos <em>clusters</em>, que según las características que observamos, decidimos clasificarlos como: canciones “Movidas” (cluster 0) y canciones “Tranquilas” (cluster 1).</li>
                <li><strong>Detección de anomalías:</strong> Usamos el algoritmo <em>Isolation Forest</em> para encontrar alrededor de 300 canciones con combinaciones inusuales de características.</li>
                <li><strong>Visualización interactiva:</strong> Finalmente, desarrollamos esta aplicación en <em>Streamlit</em> para permitir al usuario explorar canciones, conocer sus características y descubrir temas similares.</li>
            </ol>
        </div>

        <div class="section">
            <h2>🎯 Resultados y aportes</h2>
            <p class="intro-text">
            El sistema permite explorar el espacio musical de forma visual e interactiva. 
            Los usuarios pueden seleccionar una canción, analizar sus atributos musicales, su pertenencia a un cluster 
            y recibir recomendaciones de temas similares.
            </p>
            <p class="intro-text">
            Además, los análisis realizados muestran una coherencia entre las agrupaciones y los géneros musicales, 
            validando la división entre canciones movidas y tranquilas. 
            Este proyecto sienta las bases para futuras aplicaciones de recomendación musical basadas en contenido.
            </p>
        </div>
    </div>
    """
    components.html(html_intro, height=1500, scrolling=True)

# ========================
# OPCIÓN EXPLORACIÓN LIBRE
# ========================
elif page == "Exploración libre":

    st.title("📈 Análisis y exploración libre de canciones")
    st.markdown("Explorá los distintos gráficos interactivos creados durante el análisis de datos.")
    st.markdown("---")

    df = pd.read_csv("songs_final_cortito_para_pruebas.csv")
    df["display_name"] = df["title"] + " - " + df["artist_name"]
    df_clean = df.dropna(subset=['track_mbid', 'cluster'])

    features = ["sad","happy","party","relaxed","acoustic","danceable","tonal","bright","instrumental"]

    # Gráfico 1: Clusters y características
    st.subheader("Visualización 1: Clusters y características")

    # Opciones para controles
    genres = ["Todos"] + sorted(df_clean["genre_rosamerica"].dropna().unique().tolist())
    genre_selected = st.selectbox("Filtrar por género:", genres, index=0)

    # Filtrado dinámico
    if genre_selected != "Todos":
        df_filtered = df_clean[df_clean["genre_rosamerica"] == genre_selected]
    else:
        df_filtered = df_clean

    # Selectbox para elegir canción
    song_names = sorted(df_filtered["display_name"].unique().tolist())
    song_selected = st.selectbox("Elegí una canción:", song_names)

    selected_song = df_filtered[df_filtered["display_name"] == song_selected].iloc[0]

    # Colores
    cluster_color_scale = alt.Scale(domain=[0, 1], range=['#E66E6E', '#6496E8'])
    color_legend = alt.Legend(title="Tipo de canción", labelExpr="datum.value == 0 ? 'Movido' : 'Tranquilo'")

    # Scatter PCA
    scatter = (
        alt.Chart(df_filtered)
        .mark_circle(size=40)
        .encode(
            x=alt.X("pca_1_2d", title="Componente principal 1 (tranquilidad)"),
            y=alt.Y("pca_2_2d", title="Componente principal 2 (positividad emocional)"),
            color=alt.Color("cluster:N", legend=color_legend, scale=cluster_color_scale),
            tooltip=["title", "artist_name", "genre_rosamerica", "cluster"]
        )
        .properties(width=600, height=500, title=alt.TitleParams(
            text="División de clusters (con PCA)",
            anchor="middle",          
            fontSize=18,
            fontWeight=500
        ))
        .interactive()
    )

    # Canción seleccionada destacada
    highlight = (
        alt.Chart(pd.DataFrame([selected_song]))
        .mark_circle(size=200, color="#f5b342", stroke="black", strokeWidth=2)
        .encode(x="pca_1_2d", y="pca_2_2d", tooltip=["title", "artist_name", "genre_rosamerica"])
    )

    # Gráfico combinado
    chart_pca = scatter + highlight 

    # Características de la canción seleccionada
    song_features = pd.DataFrame({
        "feature": features,
        "value": [selected_song[f] for f in features]
    })

    #colores
    cluster_color_scale_bar = alt.Scale(domain=[0, 1], range=['#E66E6E', '#6496E8'])
    cluster_value_bar = int(selected_song["cluster"])
    cluster_color_bar = "#E66E6E" if cluster_value_bar == 0 else "#6496E8"

    chart_features = (
        alt.Chart(song_features)
        .mark_bar(size=25, color=cluster_color_bar)
        .encode(
            x=alt.X("value:Q", title="Valor", scale=alt.Scale(domain=[0, 1])),
            y=alt.Y("feature:N", sort="-x", title=""),
            tooltip=["feature", "value"]
        )
        .properties(width=375, height=375, title=alt.TitleParams(
            text="Características de la canción",
            anchor="middle",
            fontSize=18,
            fontWeight=500
        ))
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        st.altair_chart(chart_pca, use_container_width=True)
        st.markdown(
            """
            <div style="text-align:center; font-size:14px; color:gray; margin-top:-15px;">
                <strong>Eje X:</strong> hacia la derecha → mayor <em>tranquilidad</em> |
                <strong>Eje Y:</strong> hacia arriba → mayor <em>positividad emocional</em>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.altair_chart(chart_features, use_container_width=True)
    
    


    st.markdown("---")
    st.subheader("Visualización 2: Géneros y características por cluster")
    
    genre_cluster_counts = (
        df_clean.groupby(['genre_rosamerica', 'cluster'])
        .size()
        .reset_index(name='count')
    )
 
    chart_genre_cluster = (
        alt.Chart(genre_cluster_counts)
        .mark_bar()
        .encode(
            x=alt.X('genre_rosamerica:N', title='Género', sort='-y',
                    axis=alt.Axis(labelAngle=-40, labelOverlap=False)),
            y=alt.Y('count:Q', title='Cantidad de canciones'),
            color=alt.Color('cluster:N', title='Cluster', scale=cluster_color_scale,
                            legend=alt.Legend(
                                title="Tipo de canción",
                                labelExpr="datum.value == 0 ? 'Movido' : 'Tranquilo'"
                            )),
            xOffset='cluster:N',
            tooltip=[
                alt.Tooltip('genre_rosamerica:N', title='Género'),
                alt.Tooltip('cluster:N', title='Cluster'),
                alt.Tooltip('count:Q', title='Cantidad')
            ]
        )
        .properties(
            title=alt.TitleParams(
                text='Distribución de géneros en cada cluster',
                anchor='middle',
                fontSize=18,
                fontWeight=500
            ),
            width=450,
            height=400
        )
    )

    feature_means = (
        df_clean.groupby("cluster")[features].mean().reset_index().melt(id_vars="cluster")
    )

    chart_bar_features = (
        alt.Chart(feature_means)
        .mark_bar()
        .encode(
            y=alt.Y("variable:N", title="Característica musical", sort='-x'),
            x=alt.X("value:Q", title="Valor promedio"),
            color=alt.Color("cluster:N", title="Cluster", scale=cluster_color_scale,
                            legend=alt.Legend(
                                labelExpr="datum.value == 0 ? 'Movido' : 'Tranquilo'"
                            )),
            xOffset="cluster:N",
            tooltip=["variable:N", "cluster:N", "value:Q"]
        )
        .properties(
            title=alt.TitleParams(
                text="Comparación de características musicales por cluster",
                anchor='middle',
                fontSize=18,
                fontWeight=500
            ),
            width=450,
            height=400
        )
    )

    col1, col2 = st.columns(2)
    with col1:
        st.altair_chart(chart_genre_cluster, use_container_width=True)
    with col2:
        st.altair_chart(chart_bar_features, use_container_width=True)

    
    
    st.markdown("---")
    st.subheader("Visualización 3: Canciones anómalas")
    st.markdown("Explorá las canciones más inusuales según sus características musicales detectadas con *Isolation Forest*.")

    # Detección de anomalías
    X = df_clean[features]
    iso_forest = IsolationForest(contamination=0.02, random_state=42)
    predictions = iso_forest.fit_predict(X)
    df_clean['anomaly'] = predictions

    raw_anomaly_scores = iso_forest.score_samples(X)
    inverted_scores = -raw_anomaly_scores.reshape(-1, 1)
    scaler = MinMaxScaler()
    normalized_scores = scaler.fit_transform(inverted_scores)
    df_clean['porcentaje_anomalia'] = normalized_scores

    # Filtro por género
    genres = ["Todos"] + sorted(df_clean["genre_rosamerica"].dropna().unique().tolist())
    genre_selected = st.selectbox("Filtrar por género:", genres, index=0, key="genre_filter_v3")

    if genre_selected == "Todos":
        df_filtered = df_clean.copy()
    else:
        df_filtered = df_clean[df_clean["genre_rosamerica"] == genre_selected]

    # Selección de canción anómala
    df_anomalas = (
        df_filtered[df_filtered["anomaly"] == -1]
        .sort_values(by="porcentaje_anomalia", ascending=False)
        .head(200)
    )

    options_anomalas = df_anomalas["title"] + " - " + df_anomalas["artist_name"]
    selected_song = st.selectbox("Elegí una canción anómala:", options_anomalas, key="song_filter_v3")

    selected_row = df_anomalas[df_anomalas["title"] + " - " + df_anomalas["artist_name"] == selected_song].iloc[0]

    # Preparación de gráficos
    cluster_color_scale = alt.Scale(domain=[0, 1], range=["#E66E6E", "#6496E8"])

    color_scale = alt.Scale(domain=[df_anomalas["porcentaje_anomalia"].min(), df_anomalas["porcentaje_anomalia"].max()],
                            range=["#FFD166", "#006400"])
    size_scale = alt.Scale(domain=[df_anomalas["porcentaje_anomalia"].min(), df_anomalas["porcentaje_anomalia"].max()],
                        range=[100, 600])

    # --- Canciones normales ---
    normales = (
        alt.Chart(df_filtered[df_filtered["anomaly"] == 1])
        .mark_circle(size=25)
        .encode(
            x=alt.X("pca_1_2d", title="Componente Principal 1 (Tranquilidad)"),
            y=alt.Y("pca_2_2d", title="Componente Principal 2 (Positividad emocional)"),
            color=alt.value("#D3D3D3"),
            opacity=alt.value(0.3),
        )
    )

    # --- Canciones anómalas ---
    anomalas = (
        alt.Chart(df_anomalas)
        .mark_circle()
        .encode(
            x="pca_1_2d",
            y="pca_2_2d",
            fill=alt.Fill("porcentaje_anomalia:Q", scale=color_scale, legend=None),
            size=alt.Size(
                "porcentaje_anomalia:Q",
                scale=size_scale,
                legend=alt.Legend(title="Nivel de Anomalía", format=".0%", titleFontSize=13, labelFontSize=11),
            ),
            tooltip=["title", "artist_name", "genre_rosamerica", alt.Tooltip("porcentaje_anomalia:Q", format=".2%")],
        )
    )

    # --- Canción seleccionada destacada ---
    highlight = (
        alt.Chart(df_filtered[df_filtered["track_mbid"] == selected_row["track_mbid"]])
        .mark_circle(size=300, color="#f5b342", stroke="black", strokeWidth=2)
        .encode(x="pca_1_2d", y="pca_2_2d", tooltip=["title", "artist_name"])
    )

    # --- Texto con nombre ---
    text_label = (
        alt.Chart(pd.DataFrame([selected_row]))
        .mark_text(
            align="center",
            baseline="bottom",
            dy=-15,
            fontSize=13,
            fontWeight="bold",
            color="black",
        )
        .encode(x="pca_1_2d", y="pca_2_2d", text="title:N")
    )

    # --- Gráfico combinado ---
    scatter_anomalies = (
        alt.layer(normales, anomalas, highlight, text_label)
        .properties(
            title=alt.TitleParams(
                text="Visualización de Anomalías sobre PCA (Top 200 canciones más anómalas)",
                anchor="middle",
                fontSize=18,
                fontWeight="bold",
            ),
            width=650,
            height=450,
        )
        .interactive()
    )

    # --- Gráfico de características ---
    song_features = pd.DataFrame({
        "feature": features,
        "value": [selected_row[f] for f in features]
    })
    cluster_color_bar = "#E66E6E" if selected_row["cluster"] == 0 else "#6496E8"

    chart_features = (
        alt.Chart(song_features)
        .mark_bar(size=25, color=cluster_color_bar)
        .encode(
            x=alt.X("value:Q", title="Valor", scale=alt.Scale(domain=[0, 1])),
            y=alt.Y("feature:N", sort="-x", title=""),
            tooltip=["feature", "value"],
        )
        .properties(width=300, height=400, title="Características de la canción seleccionada")
    )


    col1, col2 = st.columns([2, 1])
    with col1:
        st.altair_chart(scatter_anomalies, use_container_width=True)
        st.markdown(
            """
            <div style="text-align:center; font-size:14px; color:gray; margin-top:-15px;">
                <strong>Eje X:</strong> hacia la derecha → mayor <em>tranquilidad</em> |
                <strong>Eje Y:</strong> hacia arriba → mayor <em>positividad emocional</em>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.altair_chart(chart_features, use_container_width=True)

    st.markdown("---")
    st.subheader("Visualización 4: Distribución PCA por género")

    genre_colors = {
        "Pop": "#F9C74F",
        "Rock": "#F17634",
        "Rhythmic": "#60DF00",
        "Dance": "#18D8F1",
        "Classic": "#056A96",
        "Jazz": "#F88DBF",
        "Hip-Hop": "#E63535"
    }
        
    genres_4 = ["Todos"] + sorted(df_clean["genre_rosamerica"].dropna().unique().tolist())
    genre_selected_4 = st.selectbox("Filtrar por género:", genres_4, index=0, key="genre_filter_v4")

    # --- Filtrado dinámico ---
    if genre_selected_4 != "Todos":
        df_filtered = df_clean[df_clean["genre_rosamerica"] == genre_selected_4]
    else:
        df_filtered = df_clean


    chart_pca_genre = (
        alt.Chart(df_filtered)
        .mark_circle(size=40)
        .encode(
            x=alt.X("pca_1_2d", title="Componente principal 1 (Tranquilidad)"),
            y=alt.Y("pca_2_2d", title="Componente principal 2 (Positividad emocional)"),
            #color=alt.Color("genre_rosamerica:N", legend=alt.Legend(title="Género")),
            color=alt.Color(
                "genre_rosamerica:N",
                legend=alt.Legend(title="Género"),
                scale=alt.Scale(domain=list(genre_colors.keys()), range=list(genre_colors.values()))
            ),
            tooltip=["title", "artist_name", "genre_rosamerica"]
        )
        .properties(
            width=700, 
            height=500, 
            title=(
                f"Proyección PCA - {genre_selected_4 if genre_selected_4 != 'Todos' else 'Todos los géneros'}"
            )
        )
        .interactive()
    )

    st.altair_chart(chart_pca_genre, use_container_width=True)
    st.markdown(
            """
            <div style="text-align:center; font-size:14px; color:gray; margin-top:-15px;">
                <strong>Eje X:</strong> hacia la derecha → mayor <em>tranquilidad</em> |
                <strong>Eje Y:</strong> hacia arriba → mayor <em>positividad emocional</em>
            </div>
            """,
            unsafe_allow_html=True
    )

    st.markdown("---")
    st.subheader("Visualización 5: Gráfico de radar de características por cluster")

    import plotly.graph_objects as go
    features = ["party", "danceable", "happy", "relaxed","acoustic", "sad", "tonal", "instrumental", "bright" ]

    cluster_means = df_clean.groupby("cluster")[features].mean().reset_index()

    fig = go.Figure()

    colors = {0: "#E66E6E", 1: "#6496E8"} 

    for i, row in cluster_means.iterrows():
        color = colors[int(row["cluster"])]
        fig.add_trace(go.Scatterpolar(
            r=row[features].values,
            theta=features,
            fill='toself',
            name=f"{'Movido' if row['cluster']==0 else 'Tranquilo'}",
            line=dict(color=color, width=2),
        ))

    fig.update_layout(
        title=dict(
            text="Comparación de características musicales por cluster",
            x=0.5, 
            xanchor="center",
            font=dict(size=18, family="Arial", color="#333", weight=400)
        ),
        polar=dict(radialaxis=dict(visible=True, range=[0,1])),
        showlegend=True,
        height=500,
        width=600
    )
    st.plotly_chart(fig, use_container_width=True)
    

    st.markdown("---")
    st.subheader("Visualización 6: Distribución de géneros y características promedio por género")

    # --- Datos base ---
    genre_counts = df_clean["genre_rosamerica"].value_counts(normalize=False).reset_index()
    genre_counts.columns = ["Género", "Cantidad"]

    # --- Calcular porcentajes ---
    total_songs = genre_counts["Cantidad"].sum()
    genre_counts["Porcentaje"] = genre_counts["Cantidad"] / total_songs

    # Paleta de colores consistente
    genre_colors = {
        "Pop": "#F9C74F",
        "Rock": "#F17634",
        "Rhythmic": "#60DF00",
        "Dance": "#18D8F1",
        "Classic": "#056A96",
        "Jazz": "#F88DBF",
        "Hip-Hop": "#E63535"
    }

    genres_list = ["Todos"] + sorted(df_clean["genre_rosamerica"].dropna().unique().tolist())
    selected_genre = st.selectbox("Elegí un género para analizar sus características:", genres_list, index=0)

    # --- Pie chart base ---
    pie = (
        alt.Chart(genre_counts)
        .mark_arc()
        .encode(
            theta=alt.Theta("Cantidad:Q"),
            order=alt.Order("Porcentaje:Q", sort="descending"),
            color=alt.Color(
                "Género:N",
                scale=alt.Scale(domain=list(genre_colors.keys()), range=list(genre_colors.values())),
                legend=alt.Legend(title="Género")
            ),
            opacity=alt.condition(
                alt.datum.Género == selected_genre,
                alt.value(1.0),
                alt.value(0.85) if selected_genre != "Todos" else alt.value(1.0)
            ),
            stroke=alt.condition(
                alt.datum.Género == selected_genre,
                alt.value("black"),
                alt.value(None)  # sin borde para los demás ni para la leyenda
            ),
            strokeWidth=alt.condition(
                alt.datum.Género == selected_genre,
                alt.value(3),
                alt.value(0)
            ),
            tooltip=["Género", "Cantidad", alt.Tooltip("Porcentaje:Q", format=".1%")]
        )
        .properties(
            width=400,
            height=400,
            title=alt.TitleParams(
                text="Distribución de géneros musicales",
                anchor="middle",
                fontSize=18,
                fontWeight=500
            )
        )
    )

    pie_chart = pie 

    # --- Gráfico de barras o mensaje según selección ---
    if selected_genre != "Todos":
        genre_avg = (
            df_clean[df_clean["genre_rosamerica"] == selected_genre][features]
            .mean()
            .reset_index()
        )
        genre_avg.columns = ["Característica", "Valor promedio"]

        chart_genre_avg = (
            alt.Chart(genre_avg)
            .mark_bar(size=30, color=genre_colors.get(selected_genre, "#888"))
            .encode(
                y=alt.Y("Característica:N", sort="-x", title=""),
                x=alt.X("Valor promedio:Q", scale=alt.Scale(domain=[0, 1]), title="Valor promedio"),
                tooltip=["Característica", "Valor promedio"]
            )
            .properties(
                width=450,
                height=400,
                title=alt.TitleParams(
                    text=f"Características promedio - {selected_genre}",
                    anchor="middle",
                    fontSize=18,
                    fontWeight=500
                )
            )
        )
    else:
        msg_html = """
        <div style="display:flex; align-items:center; justify-content:center; height:100%;">
        <div style="text-align:center; color:gray; padding:18px; border-radius:8px;">
            <strong>Seleccioná un género</strong> en el desplegable para ver aquí sus características promedio.
        </div>
        </div>
        """

    # --- Mostrar lado a lado ---
    col1, col2 = st.columns([1, 1])
    with col1:
        st.altair_chart(pie_chart, use_container_width=True)
    with col2:
        if selected_genre != "Todos":
            st.altair_chart(chart_genre_avg, use_container_width=True)
        else:
            st.markdown(msg_html, unsafe_allow_html=True)



    st.markdown("---")
    st.subheader("Visualización 7: Comparación de una característica entre géneros")

    selected_feature = st.selectbox(
        "Elegí una característica para comparar entre géneros:",
        features,
        index=features.index("happy") if "happy" in features else 0
    )

    # Calcular promedios por género
    feature_by_genre = (
        df_clean.groupby("genre_rosamerica")[selected_feature]
        .mean()
        .reset_index()
        .sort_values(by=selected_feature, ascending=False)
    )

    chart_feature_genre = (
        alt.Chart(feature_by_genre)
        .mark_bar(size=25)
        .encode(
            x=alt.X(selected_feature + ":Q", title=f"Promedio de '{selected_feature}'", scale=alt.Scale(domain=[0, 1])),
            y=alt.Y("genre_rosamerica:N", title="Género", sort="-x"),
            tooltip=["genre_rosamerica", selected_feature]
        )
        .properties(
            width=600,
            height=400,
            title=alt.TitleParams(
                text=f"Comparación de la característica '{selected_feature}' entre géneros",
                anchor="middle",
                fontSize=18,
                fontWeight=500
            )
        )
    )

    st.altair_chart(chart_feature_genre, use_container_width=True)
