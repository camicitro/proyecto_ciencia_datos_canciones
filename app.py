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

# ========================
# CONFIGURACIÓN GENERAL
# ========================
st.set_page_config(page_title="Explorador de Canciones", layout="wide")

st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #fff8f8;
    }
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
page = st.sidebar.radio("", ["Explorador de canciones", "Referencias"])

# ========================
# OPCIÓN 1: EXPLORADOR
# ========================
if page == "Explorador de canciones":
    st.title("🎵 Explorador de Canciones")

    df = pd.read_csv("songs_final_8_COMPLETO.csv")

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
    components.html(html_cards, height=230)

    st.markdown("---")

    class PCAPipeline(BaseEstimator, TransformerMixin):
        def __init__(self, n_components=2):
            self.n_components = n_components
            self.pipeline = Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
                ("pca", PCA(n_components=self.n_components))
            ])
        def fit(self, X, y=None):
            self.pipeline.fit(X)
            return self
        def transform(self, X):
            return self.pipeline.transform(X)

    features = ["sad","happy","party","relaxed","acoustic","danceable","tonal","bright","instrumental"]

    pca2 = PCAPipeline(n_components=2)
    pca_2d = pca2.fit_transform(df[features])
    df["pca_1_2d"] = pca_2d[:,0]
    df["pca_2_2d"] = pca_2d[:,1]

    color_legend = alt.Legend(
        title="Tipo de canción",
        labelExpr="datum.value == 0 ? 'Cluster 0 (Movido)' : 'Cluster 1 (Tranquilo)'"
    )
    cluster_color_scale = alt.Scale(domain=[0, 1], range=['#E66E6E', '#6496E8'])

    base = (
        alt.Chart(df)
        .mark_circle()
        .encode(
            x=alt.X('pca_1_2d', title='Componente principal 1 (tranquilidad)'),
            y=alt.Y('pca_2_2d', title='Componente principal 2 (positividad emocional)'),
            color=alt.Color('cluster:N', legend=color_legend, scale=cluster_color_scale),
            tooltip=["title", "artist_name", "genre_rosamerica"]
        )
        .properties(width=450, height=400)
        .interactive()
    )

    highlight = (
        alt.Chart(df[df["track_mbid"] == selected_song["track_mbid"]])
        .mark_circle(size=200, color="#f5b342", stroke="black", strokeWidth=1)
        .encode(x='pca_1_2d', y='pca_2_2d', tooltip=["title", "artist_name", "genre_rosamerica"])
    )

    chart_pca = (base + highlight).interactive()

    song_features = pd.DataFrame({
        "feature": features,
        "value": [selected_song[f] for f in features]
    })
    chart_features = (
        alt.Chart(song_features)
        .mark_bar(size=25, color="#f5b342")
        .encode(
            x=alt.X("value:Q", title="Valor", scale=alt.Scale(domain=[0, 1])),
            y=alt.Y("feature:N", sort="-x", title=""),
            tooltip=["feature", "value"]
        )
        .properties(width=450, height=400)
    )

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Clusters con PCA")
        st.altair_chart(chart_pca, use_container_width=True)
    with col2:
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
# OPCIÓN 2: REFERENCIAS
# ========================
elif page == "Referencias":
    st.title("📘 Referencias y análisis complementario")
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
