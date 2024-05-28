import dash
import dash_bootstrap_components as dbc
from dash import Dash,dash_table, Input, Output, html, dcc
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import numpy as np


# Carica i dati dei giochi complessi
url_Complex_Games = "https://raw.githubusercontent.com/Aldibah/Videogames/main/nuovo_file.csv"
C_games = pd.read_csv(url_Complex_Games, encoding='utf-8')

# Carica i dati dei giochi semplici
url_Simple_Games = "https://github.com/Aldibah/Videogames/raw/main/video_games.csv"
S_Games = pd.read_csv(url_Simple_Games, encoding='utf-8')

url_Global_games= "https://raw.githubusercontent.com/Aldibah/Videogames/main/vgsales.csv"
G_Games = pd.read_csv(url_Global_games)

image_url = "https://cdn.pixabay.com/photo/2022/07/17/19/41/chess-7328227_1280.png"

stonks = "https://cdn.pixabay.com/photo/2012/04/02/15/59/arrow-24829_1280.png"
not_stonks = "https://cdn.pixabay.com/photo/2012/04/02/15/53/down-24813_1280.png"
nord_america = "https://upload.wikimedia.org/wikipedia/commons/d/de/Flag_of_the_United_States.png"
japan = "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Flag_of_Japan.svg/2560px-Flag_of_Japan.svg.png"
europe ="https://upload.wikimedia.org/wikipedia/commons/b/b7/Flag_of_Europe.svg"


# Crea un'applicazione Dash con il tema Lux
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

#------------------------------------------------------------------------------------------------------------------------------------------
#PULIZIA E AGGIUSTAMENTO


#::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#1   GRAFICO
# C_Games = PUBLIC

# Lista dei generi
generi_c = ['GenreIsNonGame', 'GenreIsIndie', 'GenreIsAction', 'GenreIsAdventure', 'GenreIsCasual', 
          'GenreIsStrategy', 'GenreIsRPG', 'GenreIsSimulation', 'GenreIsEarlyAccess', 'GenreIsFreeToPlay',
          'GenreIsSports', 'GenreIsRacing', 'GenreIsMassivelyMultiplayer']

# Crea un nuovo DataFrame per i generi dei giochi complessi
generi_df_c = pd.DataFrame(columns=['Gioco', 'Genere', 'Voto della recensione'])

# Converti la colonna "Metacritic" in numerica e gestisci i valori non validi
C_games['Metacritic'] = pd.to_numeric(C_games['Metacritic'], errors='coerce')

# Rimuovi le righe dove la colonna "Metacritic" è NaN
C_games = C_games.dropna(subset=['Metacritic'])

# Rimuovi eventuali valori negativi o superiori a 100
C_games = C_games[(C_games['Metacritic'] > 0) & (C_games['Metacritic'] <= 100)]

# Inizializza una lista per memorizzare i DataFrame da concatenare
dfs_to_concat = []

# Itera attraverso le righe di C_games
for index, row in C_games.iterrows():
    # Inizializza una lista per memorizzare i DataFrame relativi al gioco corrente
    dfs_for_game = []
    # Itera attraverso i generi
    for genere in generi_c:
        # Se il genere è presente nella riga e non è nullo, aggiungi un nuovo DataFrame alla lista
        if row[genere] and not pd.isnull(row[genere]):
            # Se il genere è una lista, itera attraverso di essa
            if isinstance(row[genere], list):
                for g in row[genere]:
                    df_for_game = pd.DataFrame({'Gioco': [row['ResponseName']], 'Genere': [g.split('GenreIs')[1]], 'Voto della recensione': [row['Metacritic']],'DeveloperCount': [row['DeveloperCount']],'MovieCount': [row['MovieCount']]})
                    dfs_for_game.append(df_for_game)
            else:
                df_for_game = pd.DataFrame({'Gioco': [row['ResponseName']], 'Genere': [genere.split('GenreIs')[1]], 'Voto della recensione': [row['Metacritic']],'DeveloperCount': [row['DeveloperCount']],'MovieCount': [row['MovieCount']]})
                dfs_for_game.append(df_for_game)
    # Concatena i DataFrame relativi al gioco corrente
    if dfs_for_game:
        df_for_concat = pd.concat(dfs_for_game, ignore_index=True)
        dfs_to_concat.append(df_for_concat)

# Concatena tutti i DataFrame relativi ai giochi
if dfs_to_concat:
    generi_df_c = pd.concat(dfs_to_concat, ignore_index=True, sort=False)

# Lista dei generi da eliminare
generi_da_elim = ['NonGame', 'EarlyAccess', 'FreeToPlay', 'MassivelyMultiplayer', 'Casual']

# Filtra il DataFrame per eliminare le righe con i generi specificati
generi_df_c = generi_df_c[~generi_df_c['Genere'].isin(generi_da_elim)]
generi_df_c = generi_df_c.dropna(subset=['Gioco'])

# Rinomina i generi nel DataFrame generi_df_c
generi_df_c['Genere'] = generi_df_c['Genere'].replace({
    'Racing': 'Racing / Driving',
    'RPG': 'Role-Playing (RPG)',
    'Indie': 'Educational'
})

# Converti i punteggi Metacritic da float a interi
generi_df_c['Voto della recensione'] = generi_df_c['Voto della recensione'].astype(int)

# Trovare l'indice della riga con il voto migliore
indice_max_voto = generi_df_c['Voto della recensione'].idxmax()

# Trovare l'indice della riga con il voto peggiore
indice_min_voto = generi_df_c['Voto della recensione'].idxmin()

# Estrarre l'intera riga corrispondente all'indice massimo e minimo
riga_max_voto = generi_df_c.loc[indice_max_voto]
riga_min_voto = generi_df_c.loc[indice_min_voto]


media_voti_per_genere = generi_df_c.groupby('Genere')['Voto della recensione'].mean().round(2).sort_values(ascending=False)


top_voti_per_genere = media_voti_per_genere.head(3)


#------------------S_Games = CRITICS



# Dividi i generi e crea una lista di generi separati
elenco_generi = [generi.split(',') for generi in S_Games['Metadata.Genres']]

# Appiattisci la lista di liste
generi = [genere.strip() for sublist in elenco_generi for genere in sublist]

# Crea un nuovo DataFrame con i generi separati
generi_df = pd.DataFrame({
    'Gioco': S_Games['Title'].repeat([len(sublist) for sublist in elenco_generi]),
    'Genere': generi,
    'Voto della recensione': S_Games['Metrics.Review Score'].repeat([len(sublist) for sublist in elenco_generi]),
    # Aggiungi altre colonne se necessario
})


# Trovare l'indice della riga con il voto peggiore
indice_min_voto = generi_df['Voto della recensione'].idxmin()

# Estrarre l'intera riga corrispondente all'indice massimo e minimo
riga_max_voto_s = {
    'Gioco': 'Grand Theft Auto IV',
    'Genere': 'Action',
    'Voto della recensione': 98
}
riga_min_voto_s = generi_df.loc[indice_min_voto]



mixed_scale = ['#ff00a4', '#cb00ff', '#5000ff', '#00b6ff', '#94fff6','#ffa83e', '#f1ff46','#4bff00']

color_map = {
    'Simulation': '#ff00a4',
    'Sports': '#cb00ff',
    'Strategy': '#5000ff',
    'Role-Playing (RPG)': '#00b6ff',
    'Racing / Driving': '#94fff6',
    'Educational': '#ffa83e',
    'Action': '#f5ff62',
    'Adventure': '#4bff00',

    # Aggiungi altri generi e i rispettivi colori se necessario
}



# Calcola il voto medio della recensione per genere di gioco e arrotonda a due cifre decimali
avg_review_score = generi_df.groupby('Genere')['Voto della recensione'].mean().reset_index()
avg_review_score['Voto della recensione'] = avg_review_score['Voto della recensione'].apply(lambda x: round(x, 2))

# Ordina i generi in base al voto medio della recensione in ordine decrescente
avg_review_score = avg_review_score.sort_values(by='Voto della recensione', ascending=False)

# Calcola i primi tre generi con il voto medio migliore
top_genres_data = avg_review_score.head(3)

# Converte i valori della colonna 'Genere' nei colori corrispondenti utilizzando la mappatura dei colori
color_column = avg_review_score['Genere'].map(color_map)

#COMBINED

# Crea un DataFrame con i dati combinati per i critici e il pubblico
combined_data = pd.DataFrame({
    'Genere': avg_review_score['Genere'],
    'Critics': avg_review_score['Voto della recensione'],
    'Public': media_voti_per_genere.values
}).sort_values('Genere')


# Ordina media_voti_per_genere per genere
media_voti_per_genere_comb = media_voti_per_genere.sort_index()

# Crea un DataFrame con i dati combinati per i critici e il pubblico
combined_data = pd.DataFrame({
    'Genere': avg_review_score['Genere'],
    'Critics': avg_review_score['Voto della recensione'],
    'Public': media_voti_per_genere_comb.reindex(avg_review_score['Genere']).values
}).sort_values('Genere')

# Creare i dati per la tabella
data_for_table = []

for genre, critics_score, public_score in zip(combined_data['Genere'], combined_data['Critics'], combined_data['Public']):
    # Determina il massimo e il minimo tra il punteggio della critica e quello del pubblico
    max_score = max(critics_score, public_score)
    min_score = min(critics_score, public_score)

    # Calcola la differenza percentuale
    if min_score == 0:
        difference_percent = 100  # Imposta la differenza percentuale al 100% se il punteggio minimo è zero
    else:
        difference_percent = 100 - ((min_score * 100) / max_score) 

    # Aggiungi i dati alla lista
    data_for_table.append({
        "Genere": genre,
        "Critics Score": critics_score,
        "Public Score": public_score,
        "Difference (%)": round(difference_percent, 2)
    })




#::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#2 GRAFICO

console_df = pd.DataFrame({
    'Gioco': S_Games['Title'].repeat([len(sublist) for sublist in elenco_generi]),
    'Genere': generi,
    'Voto della recensione': S_Games['Metrics.Review Score'].repeat([len(sublist) for sublist in elenco_generi]),
    'Console': S_Games['Release.Console'].repeat([len(sublist) for sublist in elenco_generi]),
})

# Raggruppa per Genere e calcola la distribuzione delle Console
genre_console_percentage = console_df.groupby('Genere')['Console'].value_counts(normalize=True) * 100

# Converti la Series in un DataFrame
genre_console_df = genre_console_percentage.reset_index(name='Percentuale')


# Raggruppa per Console e calcola la distribuzione dei Generi
console_genre_percentage = console_df.groupby('Console')['Genere'].value_counts(normalize=True) * 100

# Converti la Series in un DataFrame
console_genre_df = console_genre_percentage.reset_index(name='Percentuale')


#::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#3 GRAFICO

# Converti la colonna 'DeveloperCount' in numerica
generi_df_c['DeveloperCount'] = pd.to_numeric(generi_df_c['DeveloperCount'], errors='coerce')

# Rimuovi eventuali righe con valori non numerici nella colonna 'DeveloperCount'
generi_df_c = generi_df_c.dropna(subset=['DeveloperCount'])
generi_df_c = generi_df_c[generi_df_c['DeveloperCount'] != 0]

# Aggiungi jitter ai valori di DeveloperCount
jitter_strength = 0.3  # Questo può essere regolato in base alle necessità
generi_df_c['DeveloperCountJitter'] = generi_df_c['DeveloperCount'] + np.random.uniform(-jitter_strength, jitter_strength, generi_df_c.shape[0])

# Creare il grafico scatter con Plotly Express
scatter = px.scatter(
    generi_df_c,
    x='DeveloperCountJitter',
    y='Voto della recensione',
    color='Genere',
    color_discrete_map=color_map,
    title='Is a Partnership Worth It?',
    labels={'DeveloperCountJitter': 'Number of Developers', 'Voto della recensione': 'Metacritic Score'},
    hover_data=['Genere'],
    template=None
)

# Convertire in oggetto go.Figure per aggiungere le linee verticali
scatter = go.Figure(scatter)

# Aggiungere le linee verticali per i valori originali di DeveloperCount
for developer_count in generi_df_c['DeveloperCount'].unique():
    scatter.add_shape(
        type='line',
        x0=developer_count, x1=developer_count,
        y0=generi_df_c['Voto della recensione'].min() - 5,
        y1=generi_df_c['Voto della recensione'].max() + 5,
        line=dict(color='rgba(169, 169, 169, 0.1)', width=65)  # Colore grigio trasparente per le linee
    )

# Aggiornare il layout
scatter.update_layout(
    title=dict(
        text='Is a Partnership Worth It?',
        font=dict(
            family='Roboto, sans-serif',
            size=21,
            color='white'
        ),
        x=0.4,
        xanchor='center',
    ),
    xaxis=dict(
        title=dict(
            text='N. Video Game Studios',
            font=dict(
                family='Roboto, sans-serif',
                size=18,
                color='white'
            )
        ),
        showline=False,
        showgrid=False,
    ),
    yaxis=dict(
        title=dict(
            text='Reviews',
            font=dict(
                family='Roboto, sans-serif',
                size=18,
                color='white'
            )
        ),
        gridcolor='rgba(255, 255, 255, 0.1)',
    ),
    plot_bgcolor='rgba(5, 13, 43, 1)',
    paper_bgcolor='rgba(5, 13, 43, 0.7)',
    font=dict(color='white'),
    margin=dict(l=50, r=50, t=50, b=50),
)

scatter.update_traces(
    marker=dict(size=7, line=dict(width=0.5))
)

#::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#4 GRAFICO GEOGRAFICO



# Lista delle regioni cliccabili e corrispondenti colonne di vendite per stato
region_sales_mapping = {
    'North America': 'NA_Sales',
    'Japan': 'JP_Sales',
    'Europe': 'EU_Sales'
}



def create_world_map():
    # Crea una mappa del mondo con regioni cliccabili
    world_map = go.Figure(go.Choropleth(
        locations=['USA', 'CAN', 'JPN', 'ALB', 'AND', 'ARM', 'AUT', 'AZE', 'BLR', 'BEL', 'BIH', 'BGR', 'HRV', 'CYP', 'CZE', 'DNK', 'EST', 'FIN', 'FRA', 'GEO', 'DEU', 'GRC', 'HUN', 'ISL', 'IRL', 'ITA', 'KOS', 'LVA', 'LIE', 'LTU', 'LUX', 'MKD', 'MLT', 'MDA', 'MCO', 'MNE', 'NLD', 'NOR', 'POL', 'PRT', 'ROU', 'SMR', 'SRB', 'SVK', 'SVN', 'ESP', 'SWE', 'CHE', 'VAT'],  
        z=[1]*59,  # Valore fittizio, non influisce sulla visualizzazione
        colorscale=[[0, 'rgb(211, 211, 211)'], [1, '#ff00a4']],
        showscale=False,
        hoverinfo='location',
    ))

    world_map.data[0].marker.line.color = 'rgba(0,0,0,0)'

    world_map.update_layout(
        title_text='Select: Nord America , Japan or EU',
        geo=dict(
            showframe=False,
            showcoastlines=False,
            showcountries=False,  # Rimuove i confini delle nazioni
            showsubunits=False,  # Rimuove i confini delle suddivisioni (stati, province, ecc.)
            projection_type='equirectangular',
            scope='world',  # Imposta lo scope su 'world' per visualizzare l'intero mondo senza possibilità di zoom
            bgcolor='rgba(0,0,0,1)',
        ),
        title_font=dict(color='white',size=15),
        height=370, 
        #paper_bgcolor='rgba(5, 13, 43, 1)',
        paper_bgcolor='black',  
    )

    return world_map





media_vendite_nord_america = round(G_Games['NA_Sales'].mean(), 2)
media_vendite_europa = round(G_Games['EU_Sales'].mean(), 2)
media_vendite_giappone = round(G_Games['JP_Sales'].mean(), 2)








#-----------------------------------------------------------------------------------------------------------------------------------
#DASHBOARD

initial_options = [
    {"label": "Genre", "value": "genre"},
    {"label": "Console", "value": "console"}
]




# Dizionari con le opzioni specifiche per genere e console
genre_options = [
    {"label": "Action", "value": "Action"},
    {"label": "Adventure", "value": "Adventure"},
    {"label": "Educational", "value": "Educational"},
    {"label": "Racing / Driving", "value": "Racing / Driving"},
    {"label": "Role-Playing (RPG)", "value": "Role-Playing (RPG)"},
    {"label": "Simulation", "value": "Simulation"},
    {"label": "Sports", "value": "Sports"},
    {"label": "Strategy", "value": "Strategy"}
]

console_options = [
    {"label": "Nintendo DS", "value": "Nintendo DS"},
    {"label": "Nintendo Wii", "value": "Nintendo Wii"},
    {"label": "PlayStation 3", "value": "PlayStation 3"},
    {"label": "Sony PSP", "value": "Sony PSP"},
    {"label": "X360", "value": "X360"}
]

# Creazione del grafico a barre Public
fig_metacritic_c = go.Figure(
    data=[
        go.Bar(
            x=media_voti_per_genere.index,  # Genere
            y=media_voti_per_genere.values,  # Media dei voti
            marker_color=[color_map[genre] for genre in media_voti_per_genere.index],  # Usa la mappatura dei colori
            width=0.6,
            hovertemplate='<b>Genre</b>: %{x}<br><b>Mean Vote</b>: %{y:.2f}<extra></extra>',  # Testo personalizzato al passaggio del mouse
            text=media_voti_per_genere.values.round(2),  # Testo visualizzato sulle barre
            textposition='auto',  # Posizione automatica del testo
        )
    ],
    layout=go.Layout(
        template=None,  # Disabilita qualsiasi template globale
        title=dict(
            text='Public',
            x=0.5,
            xanchor='center',
            font=dict(
                family='Roboto, sans-serif',  # Imposta il font a Roboto
                size=24,
                color='white'
            )
        ),
        xaxis=dict(
            title=dict(
                text='Genre',
                font=dict(
                    family='Roboto, sans-serif',  # Imposta il font a Roboto
                    size=20,
                    color='white'
                )
            )
        ),
        yaxis=dict(
            title=dict(
                text='Reviews',
                font=dict(
                    family='Roboto, sans-serif',  # Imposta il font a Roboto
                    size=18,
                    color='white'
                )
            )
        ),
        plot_bgcolor='rgba(5, 13, 43, 0.5)',  # Sfondo semi-trasparente scuro per il plot
        paper_bgcolor='rgba(5, 13, 43, 0.5)',  # Sfondo semi-trasparente scuro per la carta
        font=dict(color='white')  # Imposta il colore del testo per il titolo
    )
)

# Creare un DataFrame con le righe ottenute
tabella_voti = pd.DataFrame([riga_max_voto, riga_min_voto])


# Creazione del grafico a barre combinato
fig_combined = go.Figure()

# Aggiungi le barre con il valore maggiore per ogni genere
for _, row in combined_data.iterrows():
    if row['Critics'] >= row['Public']:
        fig_combined.add_trace(go.Bar(
            x=[row['Genere']],
            y=[row['Critics']],
            name='Critics',
            marker_color='#d9d9d9',  # Colore per i critici
            width=0.8,  # Larghezza delle barre
            hovertemplate='<b>Genre</b>: %{x}<br><b>Critics Mean Vote</b>: %{y:.2f}<extra></extra>',
            text=[row['Critics']],
            textposition='outside',
            textfont_color='#d9d9d9',  # Colore del testo uguale al colore della barra
            textangle=90 , # Angolo del testo
        ))
        fig_combined.add_trace(go.Bar(
            x=[row['Genere']],
            y=[row['Public']],
            name='Public',
            marker_color='#009bff',  # Colore per il pubblico
            width=0.8,  # Larghezza delle barre
            hovertemplate='<b>Genre</b>: %{x}<br><b>Public Mean Vote</b>: %{y:.2f}<extra></extra>',
            text=[row['Public']],
            textposition='auto',
            textfont_color='black',  # Colore del testo uguale al colore della barra
            textangle=90,  # Angolo del testo
            textfont_size = 10
        ))
    else:
        fig_combined.add_trace(go.Bar(
            x=[row['Genere']],
            y=[row['Public']],
            name='Public',
            marker_color='#009bff',  # Colore per il pubblico
            width=0.8,  # Larghezza delle barre
            hovertemplate='<b>Genre</b>: %{x}<br><b>Public Mean Vote</b>: %{y:.2f}<extra></extra>',
            text=[row['Public']],
            textposition='outside',
            textfont_color='#009bff',  # Colore del testo uguale al colore della barra
            textangle=90,  # Angolo del testo
            showlegend=False,
        ))
        fig_combined.add_trace(go.Bar(
            x=[row['Genere']],
            y=[row['Critics']],
            name='Critics',
            marker_color='#d9d9d9',  # Colore per i critici
            width=0.8,  # Larghezza delle barre
            hovertemplate='<b>Genre</b>: %{x}<br><b>Critics Mean Vote</b>: %{y:.2f}<extra></extra>',
            text=[row['Critics']],
            textposition='auto',
            textfont_color='black',  # Colore del testo uguale al colore della barra
            textangle=90,  # Angolo del testo
            showlegend=False,  # Nascondi dalla legenda
            textfont_size = 10
        ))

# Imposta il layout del grafico
fig_combined.update_layout(
    template=None,
    title=dict(
        text='Critics vs Public',
        x=0.5,
        xanchor='center',
        font=dict(
            family='Roboto, sans-serif',
            size=24,
            color='white'
        )
    ),
    xaxis=dict(
        title=dict(
            text='Genre',
            font=dict(
                family='Roboto, sans-serif',
                size=20,
                color='white'
            )
        )
    ),
    yaxis=dict(
        title=dict(
            text='Reviews',
            font=dict(
                family='Roboto, sans-serif',
                size=20,
                color='white'
            )
        ),
        range=[0, combined_data[['Critics', 'Public']].max().max() * 1.2]  # Aggiungi uno spazio extra in verticale
    ),
    barmode='overlay',  # Sovrapponi le barre
    plot_bgcolor='rgba(5, 13, 43, 0.5)',
    paper_bgcolor='rgba(5, 13, 43, 0.5)',
    font=dict(color='white'),
)


# Crea la tabella
table_percent = dash_table.DataTable(
    id='genre-scores-table',
    columns=[
        {"name": "Genre", "id": "Genere"},
        {"name": "Critics", "id": "Critics Score"},
        {"name": "Public", "id": "Public Score"},
        {"name": "Diff (%)", "id": "Difference (%)"}
    ],
    data=data_for_table,
    style_table={
        'color': 'black',
        'width': '100%',
        'border': 'none',
        'borderRadius': '10px',
        'backgroundColor': 'rgba(5, 13, 43, 0.8)',
        'padding': '10px'
    },
    style_header={
        'fontSize': '18px',
        'color': 'white',
        'backgroundColor': '#050d2b',
        'fontWeight': 'bold'
    },
    style_cell={
        'fontFamily': 'Roboto',
        'textAlign': 'center',
        'fontWeight': 'bold',
        'border': 'none'
    },
    style_data_conditional=[
        # Condizioni per colorare le righe
        {'if': {'filter_query': '{{Genere}} eq "{}"'.format(genre)}, 'backgroundColor': color}
        for genre, color in color_map.items()
    ] + [
        # Condizioni per colorare le colonne "Public Score" e "Critics Score"
        {'if': {'column_id': 'Public Score'}, 'backgroundColor': '#009bff', 'color': 'black'},
        {'if': {'column_id': 'Critics Score'}, 'backgroundColor': '#d9d9d9', 'color': 'black'},
    ],
    # Ordina la tabella inizialmente in senso decrescente per la colonna "Diff (%)"
    sort_action='native',
    sort_by=[{'column_id': 'Difference (%)', 'direction': 'desc'}]
)

# Aggiunge la tabella al layout
layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H2("Top Genres Scores", style={"color": "white", "textAlign": "center"}), width=12),
    ], style={"marginBottom": "20px"}),
    dbc.Row([
        dbc.Col(table_percent, width=12)
    ], style={"borderRadius": "20px", "padding": "10px", "backgroundColor": "rgba(5, 13, 43, 0.4)"})
], fluid=True)




app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600&display=swap" rel="stylesheet">
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''


fig = go.Figure(
    data=[
        go.Bar(
            x=avg_review_score['Genere'], 
            y=avg_review_score['Voto della recensione'], 
            marker_color=color_column,  # Usa la mappatura dei colori 
            width=0.6,
            hovertemplate='<b>Genre</b>: %{x}<br><b>Mean Vote</b>: %{y:.2f}<extra></extra>',  # Testo personalizzato al passaggio del mouse
            text=avg_review_score['Voto della recensione'],  # Aggiunge il testo sopra ogni barra
            textposition='auto',  # Posizione automatica del testo
        )
    ],
    layout=go.Layout(
        template=None,  # Disabilita qualsiasi template globale
        title=dict(
            text='Critics',
            x=0.5,
            xanchor='center',
            font=dict(
                family='Roboto, sans-serif',  # Imposta il font a Roboto
                size=24,
                color='white'
            )
        ),
        xaxis=dict(
            title=dict(
                text='Genre',
                font=dict(
                    family='Roboto, sans-serif',  # Imposta il font a Roboto
                    size=20,
                    color='white'
                )
            )
        ),
        yaxis=dict(
            title=dict(
                text='Reviews',
                font=dict(
                    family='Roboto, sans-serif',  # Imposta il font a Roboto
                    size=18,
                    color='white'
                )
            )
        ),
        plot_bgcolor='rgba(5, 13, 43, 0.5)',  # Sfondo semi-trasparente scuro per il plot
        paper_bgcolor='rgba(5, 13, 43, 0.5)',  # Sfondo semi-trasparente scuro per la carta
        font=dict(color='white')  # Imposta il colore del testo per il titolo
    )
)

top_genres_table_critic = html.Div(
    dbc.Col(
        html.Div(
            dash_table.DataTable(
                id='top-genres-table',
                columns=[
                    {"name": "Position", "id": "Posizione", "type": "numeric"},
                    {"name": "Genre", "id": "Genere"},
                    {"name": "Review Score", "id": "Voto della recensione", "type": "numeric"}
                ],
                data=[
                    {"Posizione": f"{idx + 1}.", "Genere": row[1], "Voto della recensione": row[2]}
                    for idx, row in enumerate(top_genres_data.head(3).itertuples(), start=0)
                ],
                style_table={
                    'color': 'black',
                    'width': '100%',
                    'border': 'none',  
                    'borderRadius': '10px',  
                    'backgroundColor': 'rgba(5, 13, 43, 0.8)',  
                    'padding': '10px'  
                },
                style_header={
                    'fontSize': '18px',
                    'color': 'white',
                    'backgroundColor': '#050d2b', 
                    'fontWeight': 'bold' 
                },
                style_cell={
                    'fontFamily': 'Roboto',
                    'textAlign': 'center',
                    'fontWeight': 'bold',
                    'border': 'none'  
                },
                style_data_conditional=[
                    {'if': {'row_index': 0}, 'backgroundColor': '#ff00a4'},  
                    {'if': {'row_index': 1}, 'backgroundColor': '#cb00ff'},  
                    {'if': {'row_index': 2}, 'backgroundColor': '#5000ff'}  
                ],
            ),
        ),
        width=12
    ),
    style={"borderRadius": "20px", "padding": "10px", "backgroundColor": "rgba(5, 13, 43, 0.4)"}
)


top_genres_table_public = html.Div(
    dbc.Col(
        html.Div(
            dash_table.DataTable(
                id='top-genres-table-critic',
                columns=[
                    {"name": "Position", "id": "Posizione", "type": "numeric"},
                    {"name": "Genre", "id": "Genere"},
                    {"name": "Review Score", "id": "Voto della recensione", "type": "numeric"}
                ],
                data=[
                    {"Posizione": f"{idx + 1}.", "Genere": genre, "Voto della recensione": score}
                    for idx, (genre, score) in enumerate(media_voti_per_genere.head(3).items(), start=0)
                ],
                style_table={
                    'color': 'black',
                    'width': '100%',
                    'border': 'none',
                    'borderRadius': '10px',
                    'backgroundColor': 'rgba(5, 13, 43, 0.8)',
                    'padding': '10px'
                },
                style_header={
                    'fontSize': '18px',
                    'color': 'white',
                    'backgroundColor': '#050d2b',
                    'fontWeight': 'bold'
                },
                style_cell={
                    'fontFamily': 'Roboto',
                    'textAlign': 'center',
                    'fontWeight': 'bold',
                    'border': 'none'
                },
                style_data_conditional=[
                    {'if': {'row_index': 0}, 'backgroundColor': '#cb00ff'},
                    {'if': {'row_index': 1}, 'backgroundColor': '#00b6ff'},
                    {'if': {'row_index': 2}, 'backgroundColor': '#94fff6'}
                ],
            ),
        ),
        width=12
    ),
    style={"borderRadius": "20px", "padding": "10px", "backgroundColor": "rgba(5, 13, 43, 0.4)"}
)

dbc.Tabs(
    [
        dbc.Tab(label="Critics", tab_id="critics", style={"color": "#76cfdc", "backgroundColor": "#a3cefb", "borderColor": "#a3cefb", "padding": "15px 20px", "marginRight": "10px", "borderRadius": "5px", "boxShadow": "2px 2px 5px grey", "cursor": "pointer", "transition": "background-color 0.3s"}),
        dbc.Tab(label="Public", tab_id="public", style={"color": "white", "backgroundColor": "#333", "borderColor": "#333", "padding": "15px 20px", "marginRight": "10px", "borderRadius": "5px", "boxShadow": "2px 2px 5px grey", "cursor": "pointer", "transition": "background-color 0.3s"}),
    ],
    id="tabs",
    active_tab="critics",
)

tab_style = {
    "color": "black !important",
    "backgroundColor": "black",
    "borderColor": "black",
    "marginRight": "10px",
    "borderRadius": "5px",
    "cursor": "pointer",
    "transition": "background-color 0.3s",
    "outline": "none"
}

# Stile per le tabs attive
active_tab_style = {
    "color": "black !important", # Cambia il colore del testo in nero
    "backgroundColor": "#333",  # Cambia il colore quando la tab è attiva
    "borderColor": "#333",  # Cambia il colore del bordo quando la tab è attiva
    "borderRadius": "5px",
    "cursor": "pointer",
    "transition": "background-color 0.3s",
    "outline": "none"
}

# Definizione del layout dell'app
app.layout = dbc.Container(
    [
        #------------------------------------------------------------TITLE
        dbc.Row(
            [
                dbc.Col(
                    html.Img(src=image_url, height="100px"),
                    width=1,
                    style={"display": "flex", "justifyContent": "center", "alignItems": "center", "background": "#000720"}
                ),
                dbc.Col(
                    html.H1(
                        "Climb to Success: Exploring Games",
                        style={"color": "white", "margin": "auto", 'fontFamily': 'Montserrat', 'fontWeight': '300'}
                    ),
                    width=11
                )
            ],
            style={"backgroundColor": "#050d2b", "height": "100px", "display": "flex", "alignItems": "center", "marginBottom": "20px"}
        ),
        #----------------------------------------------DASH
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            dbc.Tabs(
                                [
                                    dbc.Tab(label="Critics", tab_id="critics", tab_style=tab_style, active_tab_style=active_tab_style),
                                    dbc.Tab(label="Public", tab_id="public", tab_style=tab_style, active_tab_style=active_tab_style),
                                    dbc.Tab(label="Comparison", tab_id="comparison", tab_style=tab_style, active_tab_style=active_tab_style),
                                ],
                                id="tabs",
                                active_tab="critics",
                            ),
                            html.Div(id="tabs-content"),
                        ]
                    ),
                    width=3,
                    style={'backgroundColor': 'rgba(5, 13, 43, 0.9)',"borderRadius": "10px"} 
                ),
                dbc.Col(
                    [
                        # Prima riga (radio button, dropdown e donut chart)
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Div(
                                        [
                                            dcc.RadioItems(
                                                id="radio-item",
                                                options=initial_options,
                                                value="genre",
                                                labelStyle={"color": "#2e82ff", "display": "inline-block", "margin-right": "60px", "font-size": "20px", 'fontFamily': 'Roboto'},
                                                inputStyle={"margin-right": "1px", "transform": "scale(1.1)"},
                                                style={"margin": "5px"}
                                            ),
                                            html.Br(),
                                            dcc.Dropdown(
                                                id="specific-dropdown",
                                                style={"font-size": "18px", 'fontFamily': 'Roboto', "margin": "5px"},
                                                clearable=False
                                            ),
                                        ],
                                        style={"display": "inline-block", "verticalAlign": "top", "margin": "10px"},
                                    ),
                                    style={"backgroundColor": 'rgba(12, 0, 17, 0.4)'},
                                    width=3  # Larghezza della colonna per i radio button e il dropdown
                                ),
                                dbc.Col(
                                    html.Div(
                                        [
                                            html.H3(id="chart-title", style={"textAlign": "center", "font-size": "20px", 'fontFamily': 'Roboto', "color": "white"}),  # Titolo del grafico
                                            dcc.Graph(
                                                id="donut-chart",
                                                figure={
                                                    'layout': {
                                                        'paper_bgcolor': 'rgba(0,0,0,0)',
                                                        'plot_bgcolor': 'rgba(0,0,0,0)',
                                                    }
                                                },
                                            )
                                        ],
                                        style={"padding-left": "10px","padding-right": "10px","padding-top": "10px", "backgroundColor": 'rgba(12, 0, 17, 0.6)', "color": "white", "margin": "10px", "borderRadius": "10px", "height": "330px"},  # Impostare l'altezza del div
                                    ),
                                    width=9  # Larghezza della colonna per il grafico donut
                                ),
                            ],
                            style={"backgroundColor": 'rgba(75, 0, 104, 0.3)', "margin": "10px"},
                        ),
                        # Seconda riga (grafico jitter)
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Div(
                                        dcc.Graph(
                                            id='scatter-plot',
                                            figure=scatter  # Passa la figura qui
                                        ),
                                        style={"padding": "15px", "color": "white", "background-color": "rgba(75, 0, 104, 0.1)", "border-radius": "10px","margin-left": "10px","margin-right": "10px"}  # Rimuovere overflowY e maxHeight per evitare lo scroll
                                    ),
                                    width=12  # Occupa l'intera larghezza della riga
                                ),
                            ],
                        ),
                    ],
                    width=5,  # Impostare la larghezza della colonna
                    #style={"height": "100vh"},
                ),
                dbc.Col(
                    [
                        html.Div(
                            [
                                # Prima riga (line chart e world map)
                                dbc.Row(
                                    [
                                        html.Div([
                                            dcc.Graph(id='line-chart', figure=go.Figure()),
                                        ], style={'backgroundColor': 'rgba(5, 13, 43, 0.5)', "border-radius": "10px", 'overflow': 'hidden'}),

                                        html.Div(id='image-and-text'),

                                        html.Div([
                                            dcc.Graph(id='world-map', figure=create_world_map()),
                                        ], style={'backgroundColor': 'rgba(5, 13, 43, 0.5)', "border-radius": "10px", 'overflow': 'hidden','margin-top': '20px'}),
                                    ],
                                ),
                            ],
                            style={ "padding": "15px", "border-radius": "10px"}
                        ),
                    ],
                    width=4,  # Impostare la larghezza della colonna
                    style={'backgroundColor': 'rgba(5, 13, 43, 0.9)',"borderRadius": "10px"} 
                )
            ],
        )
    ],
    fluid=True,
    style={
        "background": "linear-gradient(to bottom, #000a13, #050d2b, #1a2243, #2c3f6e, #3b5998, #ff007f)",
        "height": "100vh"
    }
)


# Callback per aggiornare il contenuto in base alla selezione della Tab
@app.callback(
    Output("tabs-content", "children"),
    [Input("tabs", "active_tab")]
)
def update_tab_content(active_tab):
    if active_tab == "critics":
        return html.Div(
            [
                dbc.Col(
                    html.Div(
                        [
                            html.Div(
                                "Top 3 Genres",  # Aggiungi del testo qui
                                style={"textAlign": "center", "fontSize": "20px","color":"white",'fontFamily': 'Roboto'}
                            ),
            
                            dbc.Col(
                                html.Div(
                                    dbc.Col(
                                        top_genres_table_critic,
                                    ),
                                ),
                                width=12
                            ),
                            dbc.Col(
                            html.Div(
                                [
                                html.Div(
                                [
                                    html.Img(src=stonks, style={"width": "20px", "height": "20px", "marginRight": "5px"}),
                                    html.Div(
                                    [
                                        html.Strong("Best", style={"fontFamily": "Roboto", "color": "lightgreen","marginRight": "7px"}),
                                        html.Span(f"Name: {riga_max_voto_s['Gioco']}, Genre: {riga_max_voto_s['Genere']}, Score: {riga_max_voto_s['Voto della recensione']}")
                                    ],
                                    style={"display": "flex", "alignItems": "center"}
                                    )
                                ],
                            style={"display": "flex", "alignItems": "center", "backgroundColor": "#050d2b", 'fontFamily': 'Roboto'}
                            ),
                                    html.Div(
                                        [
                                            html.Img(src=not_stonks, style={"width": "20px", "height": "20px", "marginRight": "5px"}),
                                            html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Strong("Worst", style={"fontFamily": "Roboto", "color": "red","marginRight": "7px"}),
                                                    html.Span(f"Name: {riga_min_voto_s['Gioco']}, Genre: {riga_min_voto_s['Genere']}, Score: {riga_min_voto_s['Voto della recensione']}")
                                                ],
                                                style={"display": "flex", "alignItems": "center"}
                                            )
                                        ],
                                        style={"display": "flex", "alignItems": "center", "backgroundColor": "#050d2b", 'fontFamily': 'Roboto'}
                                    )
                                        ],
                                        style={"display": "flex", "alignItems": "center", "marginTop": "10px", "backgroundColor": "#050d2b",'fontFamily': 'Roboto'}
                                    )
                                ],
                                style={"padding": "10px", "backgroundColor": "rgba(5, 13, 43, 0.8)", "color": "white", "borderRadius": "10px"}
                            ),
                            width=12
                        ),
                            dbc.Col(
                                html.Div(
                                    dcc.Graph(id='review-score-bar-chart', figure=fig),
                                    style={"borderRadius": "10px", "padding": "10px", "backgroundColor": "rgba(5, 13, 43, 0.8)"}
                                ),
                                width=12
                            )
                        ],
                        style={"borderRadius": "20px", "padding": "10px", "backgroundColor": "rgba(5, 13, 43, 0.4)"}
                    ),
                    width=12
                ),
            ],
        )
    elif active_tab == "public":
        return html.Div(
            [
                dbc.Col(
                    html.Div(
                        [
                            html.Div(
                                "Top 3 Genres",  # Aggiungi del testo qui
                                style={"textAlign": "center", "fontSize": "20px","color":"white",'fontFamily': 'Roboto'}
                            ),
                            dbc.Col(
                                html.Div(
                                    dbc.Col(
                                        top_genres_table_public,
                                    ),
                                ),
                                width=12
                            ),

                           dbc.Col(
                            html.Div(
                                [
                                html.Div(
                                [
                                    html.Img(src=stonks, style={"width": "20px", "height": "20px", "marginRight": "5px"}),
                                    html.Div(
                                    [
                                        html.Strong("Best", style={"fontFamily": "Roboto", "color": "lightgreen","marginRight": "7px"}),
                                        html.Span(f"Name: {riga_max_voto['Gioco']}, Genre: {riga_max_voto['Genere']}, Score: {riga_max_voto['Voto della recensione']}")
                                    ],
                                    style={"display": "flex", "alignItems": "center"}
                                    )
                                ],
                            style={"display": "flex", "alignItems": "center", "backgroundColor": "#050d2b", 'fontFamily': 'Roboto'}
                            ),
                                    html.Div(
                                        [
                                            html.Img(src=not_stonks, style={"width": "20px", "height": "20px", "marginRight": "5px"}),
                                            html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Strong("Worst", style={"fontFamily": "Roboto", "color": "red","marginRight": "7px"}),
                                                    html.Span(f"Name: {riga_min_voto['Gioco']}, Genre: {riga_min_voto['Genere']}, Score: {riga_min_voto['Voto della recensione']}")
                                                ],
                                                style={"display": "flex", "alignItems": "center"}
                                            )
                                        ],
                                        style={"display": "flex", "alignItems": "center", "backgroundColor": "#050d2b", 'fontFamily': 'Roboto'}
                                    )
                                        ],
                                        style={"display": "flex", "alignItems": "center", "marginTop": "10px", "backgroundColor": "#050d2b",'fontFamily': 'Roboto'}
                                    )
                                ],
                                style={"padding": "10px", "backgroundColor": "rgba(5, 13, 43, 0.8)", "color": "white", "borderRadius": "10px"}
                            ),
                            width=12
                        ),
                            
                            dbc.Col(
                                html.Div(
                                    dcc.Graph(id='review-score-bar-chart-public', figure=fig_metacritic_c),
                                    style={"borderRadius": "10px", "padding": "10px", "backgroundColor": "rgba(5, 13, 43, 0.8)"}
                                ),
                                width=12
                            )
                        ],
                        style={"borderRadius": "20px", "padding": "10px", "backgroundColor": "rgba(5, 13, 43, 0.4)"}
                    ),
                    width=12
                ),
            ],
        )
    elif active_tab == "comparison":
        return html.Div(
            [
                dbc.Col(
                    html.Div(
                        [
                            html.Div(
                                "Differences",
                                style={"textAlign": "center", "fontSize": "20px", "color": "white", 'fontFamily': 'Roboto'}
                            ),
                            dbc.Col(
                                html.Div(
                                    dbc.Col(
                                        table_percent,
                                    ),
                                ),
                                width=12
                            ),
                            dbc.Col(
                                html.Div(
                                    dcc.Graph(id='combined-review-score-bar-chart', figure=fig_combined),
                                     style={"borderRadius": "10px", "padding": "10px", "backgroundColor": "rgba(5, 13, 43, 0.8)"}
                                ),
                                width=12
                            )
                        ],
                        style={"borderRadius": "20px", "padding": "10px", "backgroundColor": "rgba(5, 13, 43, 0.4)"}
                    ),
                    width=12
                ),
            ],
        )
       
# Callback per aggiornare il dropdown specifico
@app.callback(
    Output("specific-dropdown", "options"),
    Output("specific-dropdown", "value"),
    Input("radio-item", "value")
)
def update_specific_dropdown(selected_value):
    if selected_value == "genre":
        return genre_options, genre_options[0]['value']
    elif selected_value == "console":
        return console_options, console_options[0]['value']
    return [], None

# Callback per aggiornare il grafico a torta
@app.callback(
    Output("donut-chart", "figure"),
    Input("radio-item", "value"),
    Input("specific-dropdown", "value")
)
def update_donut_chart(radio_value, specific_value):

    # Imposta una dimensione predefinita per il grafico
    default_height = 330

    if radio_value == "genre" and specific_value:
        # Filtra il DataFrame per il genere specificato
        filtered_df = genre_console_df[genre_console_df['Genere'] == specific_value]
        
        # Estrai le etichette e i valori
        labels = filtered_df['Console']
        values = filtered_df['Percentuale']
        
        # Crea il grafico a torta con i colori personalizzati
        fig = px.pie(filtered_df, values=values, names=labels, hole=0.75, color_discrete_sequence=mixed_scale)
        
        # Aggiorna il layout per rendere trasparente il colore di sfondo
        fig.update_layout({
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'legend_font_color': 'white',
            'height': default_height
        })

        fig.update_traces(insidetextfont=dict(color='black'),outsidetextfont=dict(color='white'), hovertemplate='<b>%{label}</b><br>Percentage: %{value:.2f}%<extra></extra>')
        
        return fig
    
    if radio_value == "console" and specific_value:
        # Filtra il DataFrame per la console specificata
        filtered_df = console_genre_df[console_genre_df['Console'] == specific_value]
        
        # Estrai le etichette e i valori
        labels = filtered_df['Genere']
        values = filtered_df['Percentuale']
        
        # Crea il grafico a torta con la mappa dei colori
        fig = px.pie(filtered_df, values=values, names=labels, hole=0.75, 
                     color=labels, color_discrete_map=color_map)


         # Aggiorna il layout per rendere trasparente il colore di sfondo
        fig.update_layout({
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'legend_font_color': 'white',
            'height': default_height
        })

        fig.update_traces(insidetextfont=dict(color='black'),outsidetextfont=dict(color='white'), hovertemplate='<b>%{label}</b><br>Percentage: %{value:.2f}%<extra></extra>')

        return fig
    
    # Restituisce un grafico vuoto se le condizioni non sono soddisfatte
    return {}
       

# Aggiorna la callback per aggiornare il titolo del grafico
@app.callback(
    Output("chart-title", "children"),
    Input("radio-item", "value"),
    Input("specific-dropdown", "value")
)
def update_chart_title(radio_value, specific_value):
    if radio_value == "genre" and specific_value:
        return f"Distribution of Console: {specific_value}"
    elif radio_value == "console" and specific_value:
        return f"Distribution of Genres: {specific_value}"
    return ""






@app.callback(
    Output('line-chart', 'figure'),
    [Input('world-map', 'clickData')]
)

def update_line_chart(clickData=None):
    if clickData is None:
        # Impostazioni predefinite per il Nord America
        region_sales_column = 'NA_Sales'
        min_sales_threshold = 16
        region_name = 'Nord America'
    else:
        print("Click data:", clickData)  # Stampa i dati del click per debug
        location = clickData['points'][0]['location']
        if location in ['USA', 'CAN']:  # Se è stato cliccato uno di questi paesi
            region_sales_column = 'NA_Sales'  # Altrimenti, utilizza NA_Sales per USA e Canada
            region_name = 'Nord America'
        elif location == 'JPN':
            region_sales_column = 'JP_Sales'  # Utilizza JP_Sales per il Giappone
            region_name = 'Japan'
        elif location in ['ALB', 'AND', 'ARM', 'AUT', 'AZE', 'BLR', 'BEL', 'BIH', 'BGR', 'HRV', 'CYP', 'CZE', 'DNK', 'EST', 'FIN', 'FRA', 'GEO', 'DEU', 'GRC', 'HUN', 'ISL', 'IRL', 'ITA', 'KOS', 'LVA', 'LIE', 'LTU', 'LUX', 'MKD', 'MLT', 'MDA', 'MCO', 'MNE', 'NLD', 'NOR', 'POL', 'PRT', 'ROU', 'SMR', 'SRB', 'SVK', 'SVN', 'ESP', 'SWE', 'CHE', 'VAT']:
            region_sales_column = 'EU_Sales'  # Utilizza EU_Sales per i paesi europei elencati
            region_name = 'EU'
        else:
            # Se il paese cliccato non corrisponde a nessuna delle opzioni sopra, ritorna un grafico vuoto
            return go.Figure()

    # Trova il massimo picco di vendite per ogni anno e il rispettivo genere
    max_sales_by_year = G_Games.groupby(['Year']).apply(lambda x: x.loc[x[region_sales_column].idxmax()]).reset_index(drop=True)
       
    # Crea un grafico a linee
    line_chart = go.Figure()
    line_chart.add_trace(go.Scatter(
        x=max_sales_by_year['Year'],
        y=max_sales_by_year[region_sales_column],
        text=max_sales_by_year['Genre'],
        mode='lines',
        name='',
        line=dict(color='yellow'),  # Imposta il colore della linea a giallo acceso
        hovertemplate='%{y} Mln Sales<br>%{x} <br>%{text}'  # Modifica il template del mouseover
    ))

    line_chart.update_layout(
        title=f'Peak Annual Sales in {region_name}',
        plot_bgcolor='rgba(5, 13, 43, 0.5)',  # Sfondo semi-trasparente scuro per il plot
        paper_bgcolor='rgba(5, 13, 43, 0.5)',  # Sfondo semi-trasparente scuro per il documento
        font=dict(color='white'),  # Imposta il colore del testo su bianco per una migliore leggibilità
        title_font=dict(size=18),
        xaxis=dict(
            title=dict(text='Year', font=dict(weight='bold')),
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.2)',
            zeroline=False,
            color='white'
        ),
        yaxis=dict(
            title=dict(text='Sales (Mln)', font=dict(weight='bold')),
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.2)',
            zeroline=False,
            color='white'
        ),
        height=380
    )
    return line_chart

@app.callback(
    Output('image-and-text', 'children'),
    [Input('world-map', 'clickData')]
)
def update_image_and_text(clickData):
    if clickData is None:
        return [
            html.Img(src=nord_america, style={'height': '20px', 'margin-right': '20px', 'margin-left': '30px'}),
            html.P(f"Average Sales: {media_vendite_nord_america} Mln", style={'color': 'white', 'display': 'inline-block'})
        ]
    else:
        location = clickData['points'][0]['location']
        if location in ['USA', 'CAN']:
            return [
                html.Img(src=nord_america, style={'height': '20px', 'margin-right': '20px', 'margin-left': '30px'}),
                html.P(f"Average Sales: {media_vendite_nord_america} Mln", style={'color': 'white', 'display': 'inline-block'})
            ]
        elif location == 'JPN':
            return [
                html.Img(src=japan, style={'height': '20px', 'margin-right': '20px', 'margin-left': '30px'}),
                html.P(f"Average Sales: {media_vendite_giappone} Mln", style={'color': 'white', 'display': 'inline-block'})
            ]
        elif location in ['ALB', 'AND', 'ARM', 'AUT', 'AZE', 'BLR', 'BEL', 'BIH', 'BGR', 'HRV', 'CYP', 'CZE', 'DNK', 'EST', 'FIN', 'FRA', 'GEO', 'DEU', 'GRC', 'HUN', 'ISL', 'IRL', 'ITA', 'KOS', 'LVA', 'LIE', 'LTU', 'LUX', 'MKD', 'MLT', 'MDA', 'MCO', 'MNE', 'NLD', 'NOR', 'POL', 'PRT', 'ROU', 'SMR', 'SRB', 'SVK', 'SVN', 'ESP', 'SWE', 'CHE', 'VAT']:
            return [
                html.Img(src=europe, style={'height': '20px', 'margin-right': '20px', 'margin-left': '30px'}),
                html.P(f"Average Sales: {media_vendite_europa} Mln", style={'color': 'white', 'display': 'inline-block'})
            ]
        else:
            return [
                html.P("Nessun dato disponibile", style={'color': 'white', 'display': 'inline-block'})
            ]

# Esegui l'app Dash
if __name__ == '__main__':
    app.run_server(debug=True)

