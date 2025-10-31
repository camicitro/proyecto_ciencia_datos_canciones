# para desactivar el entorno: deactivate
# activar el entorno: venv\Scripts\activate
#guardar las dependencias: pip freeze > requirements.txt
# para ejecutar la app de streamlit: streamlit run app.py

import streamlit as st
import pandas as pd
import altair as alt

st.title("🎵 Explorador de Canciones")

df = pd.read_csv("songs_final_3.csv")

song_name = st.selectbox("Elegí una canción:", sorted(df["title"].unique()))
selected_song = df[df["title"] == song_name].iloc[0]

st.subheader(f"{selected_song['title']} - {selected_song['artist_name']}")

# if selected_song["anomaly"] == 1:
#     st.warning("⚠️ Esta canción fue clasificada como **anómala** (no encaja bien en ningún grupo).")
# else:
#     st.success("✅ Esta canción no es anómala (pertenece claramente a un cluster).")


st.write(f"Género: **{selected_song['genre_rosamerica']}**")
st.write(f"Cluster: **{selected_song['cluster']}** ({'🎶 movida' if selected_song['cluster']==0 else '🕯️ tranquila'})")


# Visualización de características
st.subheader("📈 Características principales de la canción")

# Mostrar info principal
st.dataframe(selected_song[["happy","sad","party","relaxed","acoustic","danceable","bright","tonal","instrumental"]].to_frame().T)

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
similares = df[(df["cluster"]==selected_song["cluster"]) & (df["title"]!=song_name)].sample(5)
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
    alt.Chart(df[df["title"] == song_name])
    .mark_circle(size=150, color="red")
    .encode(
        x="pca_1:Q",
        y="pca_2:Q",
        tooltip=["title", "artist_name", "genre_rosamerica"]
    )
)

chart = (base + highlight).interactive().properties(title="Visualización de Clusters (PCA)")
st.altair_chart(chart, use_container_width=True)