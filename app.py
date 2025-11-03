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

### Configuración ###
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
    </style>
    """,
    unsafe_allow_html=True
)

### Título y select de canción ###
st.title("🎵 Explorador de Canciones")

df = pd.read_csv("songs_final_8_COMPLETO.csv")

# Se crea una columna con el nombre de canción - artista
if 'display_name' not in df.columns:
    df['display_name'] = df['title'] + " - " + df['artist_name']

options_list = sorted(df['display_name'].tolist())

st.markdown("### Seleccioná una canción para explorar sus características:")

# Canción por defecto
default_track_id = "85f842b8-6817-4721-a85c-8b4dde1e8814"

if default_track_id in df['track_mbid'].values:
    default_display_name = df.loc[df['track_mbid'] == default_track_id, 'display_name'].iloc[0]
    default_index = options_list.index(default_display_name) if default_display_name in options_list else 0
else:
    default_index = 0

selected_option = st.selectbox("", options_list, index=default_index)
selected_song = df[df["display_name"] == selected_option].iloc[0]

st.markdown("---")

# Función para convertir imagen a base64
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
    return encoded

# Imágenes de fondo para género y cluster
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

### Creación de tarjetas de género, cluster y anomalía ###
html_cards = f"""
<div style="display: flex; justify-content: space-around; margin-top: 20px; margin-bottom: 10px; font-family: 'Source Sans Pro', sans-serif;">
    <div style="
        position: relative;
        width: 30%;
        height: 200px;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.4);
    ">
        <div style="
            position: absolute;
            inset: 0;
            background-image: url('data:image/jpeg;base64,{base64_image_generos}');
            background-size: cover;
            background-position: center;
            opacity: 0.5;
        "></div>
        <div style="
            position: relative;
            z-index: 1;
            color: white;
            text-align: center;
            font-weight: bold;
            text-shadow: 1px 1px 4px rgba(0,0,0,0.8);
            top: 50%;
            transform: translateY(-50%);
        ">
            <h2>Género</h2>
            <h1>{selected_song['genre_rosamerica']}</h1>
        </div>
    </div>

    <div style="
        position: relative;
        width: 30%;
        height: 200px;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.4);
    ">
        <div style="
            position: absolute;
            inset: 0;
            background-image: url('data:image/gif;base64,{base64_image_clusters}');
            background-size: cover;
            background-position: center;
            opacity: 0.5;
        "></div>
        <div style="
            position: relative;
            z-index: 1;
            color: white;
            text-align: center;
            font-weight: bold;
            text-shadow: 1px 1px 4px rgba(0,0,0,0.8);
            top: 50%;
            transform: translateY(-50%);
        ">
            <h2>Cluster</h2>
            <h1>{cluster_label}</h1>
        </div>
    </div>

    <div style="
        position: relative;
        width: 30%;
        height: 200px;
        border-radius: 15px;
        overflow: hidden;
        background-color: {'#e57373' if selected_song['anomaly'] == -1 else '#81c784'};
        box-shadow: 0px 2px 10px rgba(0,0,0,0.4);
        color: white;
        text-align: center;
        font-weight: bold;
        text-shadow: 1px 1px 4px rgba(0,0,0,0.8);
        display: flex;
        flex-direction: column;
        justify-content: center;
    ">
        <h2>Anomalía</h2>
        <h1>
            {f"Anómala ({selected_song['porcentaje_anomalia']*100:.3f}%)" if selected_song["anomaly"] == -1 else "No anómala"}
        </h1>
    </div>
</div>
"""
components.html(html_cards, height=230)

### Gráficos de PCA y características ###
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

### GRáfico de PCA ###
base = (
    alt.Chart(df)
    .mark_circle()
    .encode(
        x=alt.X('pca_1_2d', title='Componente principal 1 (tranquilo)'),
        y=alt.Y('pca_2_2d', title='Componente principal 2 (movido)'),
        color=alt.Color('cluster:N', legend=color_legend, scale=cluster_color_scale),
        tooltip=["title", "artist_name", "genre_rosamerica"]
    )
    .properties(width=450, height=400)
    .interactive()
)
highlight = (
    alt.Chart(df[df["track_mbid"] == selected_song["track_mbid"]])
    .mark_circle(size=200, color="#f5b342", stroke="black", strokeWidth=1)
    .encode(
        x='pca_1_2d',
        y='pca_2_2d',
        tooltip=["title", "artist_name", "genre_rosamerica"]
    )
)
chart_pca = (base + highlight).interactive()

### Gráfico de características ###
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

# Mostrar gráficos uno al lado del otro
col1, col2 = st.columns(2)
with col1:
    st.subheader("Proyección 2D con PCA")
    st.altair_chart(chart_pca, use_container_width=True)
with col2:
    st.subheader("Características de la canción")
    st.altair_chart(chart_features, use_container_width=True)

### Canciones similares ###
st.markdown("---")
st.subheader("Canciones similares")

columnas_mostrar = ["title", "artist_name", "genre_rosamerica"]

df_similares_filtrado = df[columnas_mostrar].sample(5).rename(columns={
    "title": "Título",
    "artist_name": "Artista",
    "genre_rosamerica": "Género"
})

st.dataframe(df_similares_filtrado, use_container_width=True)