# para desactivar el entorno: deactivate
# activar el entorno: venv\Scripts\activate
#guardar las dependencias: pip freeze > requirements.txt
# para ejecutar la app de streamlit: streamlit run app.py

import streamlit as st
import pandas as pd
import altair as alt
import base64

st.title("🎵 Explorador de Canciones")

df = pd.read_csv("songs_final_7_COMPLETO.csv")

if 'display_name' not in df.columns:
    df['display_name'] = df['title'] + " - " + df['artist_name']

options_list = sorted(df['display_name'].tolist())

selected_option = st.selectbox("Elegí una canción:", options_list)

selected_song = df[df["display_name"] == selected_option].iloc[0]

st.subheader(f"{selected_song['title']} - {selected_song['artist_name']}") 

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
    return encoded

genre = selected_song["genre_rosamerica"].lower()

backgrounds = {
    "pop": "images/pop.png",
    "rock": "images/rock.jpg",
    "jazz": "images/jazz.jpg",
    "dance": "images/dance.jpg",
    "hip-hop": "images/hiphop.jpg",
    "classic": "images/classic.jpg",
    "rhythmic": "images/rhythmic.png",
}

background_image = backgrounds.get(genre, "images/default.jpg")
base64_image = get_base64_image(background_image)

cluster_label = "💃 Movido" if selected_song["cluster"] == 0 else "💆‍♀️ Tranquilo"
cluster_color = "#ffb3ba" if selected_song["cluster"] == 0 else "#b3e5fc"

# === Mostrar información destacada con fondo dinámico en el género ===
st.markdown(
    f"""
    <div style="
        display:flex;
        justify-content: space-around;
        margin-top: 20px;
        margin-bottom: 20px;
    ">
        <div style="
            background-image: url('data:image/jpeg;base64,{base64_image}');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            border-radius:15px;
            padding:20px 40px;
            text-align:center;
            opacity: 0.6;
            color:white;
            box-shadow:0px 2px 10px rgba(0,0,0,0.4);
            font-weight: bold;
            text-shadow: 1px 1px 4px rgba(0,0,0,0.8);
            width: 40%;
        ">
            <h2>Género</h2>
            <h1>{selected_song['genre_rosamerica']}</h1>
        </div>
        <div style="
            background-color:{cluster_color};
            border-radius:15px;
            padding:20px 40px;
            text-align:center;
            box-shadow:0px 2px 10px rgba(0,0,0,0.3);
            width: 40%;
        ">
            <h3 style="color:#333;">🎯 Cluster</h3>
            <h2 style="color:#000;">{cluster_label}</h2>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# st.write(f"Género: **{selected_song['genre_rosamerica']}**")
# st.write(f"Cluster: {'💃 Movido (0)' if selected_song['cluster']==0 else '💆‍♀️ Tranquilo (0)'}")
# st.write(f"Cluster: **{selected_song['cluster']}** ({'🎶 movida' if selected_song['cluster']==0 else '🕯️ tranquila'})")

if selected_song["anomaly"] == -1:
    st.warning("⚠️ Esta canción fue clasificada como **anómala** (no encaja bien en ningún grupo).")
else: 
    st.success("✅ Esta canción no es anómala (pertenece claramente a un cluster).")
# Visualización de características
st.subheader("Características de la canción")

# Visualización de características
features = ["happy","sad","party","relaxed","acoustic","danceable","bright","tonal","instrumental"]

# Convertir la fila a un DataFrame apropiado para Altair
song_features = (
    pd.DataFrame({
        "feature": features,
        "value": [selected_song[f] for f in features]
    })
)

# Crear gráfico de barras horizontal
chart_features = (
    alt.Chart(song_features)
    .mark_bar(size=25, color="#1f77b4")
    .encode(
        x=alt.X("value:Q", title="Valor", scale=alt.Scale(domain=[0, 1])),
        y=alt.Y("feature:N", sort="-x", title=""),
        tooltip=["feature", "value"]
    )
    .properties(height=300)
)

st.altair_chart(chart_features, use_container_width=True)

# Canciones similares del mismo cluster
similares = df[(df["cluster"]==selected_song["cluster"]) & (df["title"]!=selected_song["title"])].sample(5)
st.subheader("🎯 Canciones similares")
st.table(similares[["title","artist_name","genre_rosamerica","cluster"]])

# Gráfico Altair
base = (
    alt.Chart(df)
    .mark_circle(size=60, color="lightgray")
    .encode(
        x="pca_1:Q",
        y="pca_2:Q",
        color=alt.Color("cluster:N", legend=alt.Legend(title="Cluster")),
        tooltip=["title", "artist_name", "genre_rosamerica"]
    )
    .interactive()
)
highlight = (
    alt.Chart(df[df["title"] == selected_song["title"]])
    .mark_circle(size=150, color="red")
    .encode(
        x="pca_1:Q",
        y="pca_2:Q",
        tooltip=["title", "artist_name", "genre_rosamerica"]
    )
)

chart = (base + highlight).interactive().properties(title="Visualización de Clusters (PCA)")
st.altair_chart(chart, use_container_width=True)