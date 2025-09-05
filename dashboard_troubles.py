import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import plotly.graph_objects as go

# --- Données radar ---
profils = ["TPB", "Bipolarité", "Schizophrénie", "Pervers narcissique"]
axes = ["Émotions / humeur", "Relations interpersonnelles", "Impulsivité / comportements",
        "Perception / cognition", "Image de soi / identité", "Risques / comorbidités"]
n_axes = len(axes)

data_radar = {
    "TPB": [9, 9, 7, 6, 8, 8],
    "Bipolarité": [8, 6, 9, 7, 7, 8],
    "Schizophrénie": [6, 5, 4, 9, 5, 7],
    "Pervers narcissique": [7, 9, 6, 7, 8, 8]
}

colors = ["#FF6F61", "#6B5B95", "#88B04B", "#FFA500"]

# --- Données textuelles uniformisées ---
profils_info = {
    "TPB": {
        "Symptômes": ["Instabilité émotionnelle", "Relations interpersonnelles instables", 
                      "Image de soi instable", "Impulsivité", "Comportements auto-agressifs", 
                      "Colère intense", "Dissociation transitoire", "Addictions"],
        "Comorbidités": ["Troubles de l’humeur", "Troubles anxieux", "Addictions", 
                         "Troubles alimentaires", "Autres troubles personnalité"]
    },
    "Bipolarité": {
        "Symptômes": ["Phase maniaque : humeur élevée/irritable, énergie excessive, logorrhée, impulsivité",
                      "Phase dépressive : humeur basse, perte d’intérêt, fatigue, idées suicidaires", "Addictions"],
        "Comorbidités": ["Troubles anxieux", "Addictions", "Troubles du sommeil", 
                         "Maladies métaboliques", "Comportements suicidaires"]
    },
    "Schizophrénie": {
        "Symptômes": ["Hallucinations", "Idées délirantes", "Pensée désorganisée", 
                      "Comportement catatonique", "Retrait social", "Affect plat", 
                      "Anhédonie", "Troubles cognitifs", "Addictions"],
        "Comorbidités": ["Troubles anxieux", "Troubles de l’humeur", "Addictions", 
                         "Troubles personnalité", "Risque suicidaire", "Troubles métaboliques"]
    },
    "Pervers narcissique": {
        "Symptômes": ["Besoin intense d’admiration", "Manque d’empathie", 
                      "Hypersensibilité aux critiques", "Sentiment d’insécurité", 
                      "Humeur instable", "Addictions"],
        "Comorbidités": ["Troubles anxieux", "Dépression", "Addictions", "Comportements addictifs",
                         "Traits de personnalité comorbides", "Troubles psychosomatiques"]
    }
}

# --- Streamlit Interface ---
st.title("Dashboard interactif : Profils cumulés et réseau symptômes/comorbidités")
st.sidebar.title("Sélection des profils")
profils_selected = st.sidebar.multiselect("Choisir un ou plusieurs profils", profils, default=profils)

st.sidebar.title("Filtres réseau")
filter_options = st.sidebar.multiselect("Afficher catégories", ["Profils", "Symptômes", "Comorbidités"], 
                                        default=["Profils", "Symptômes", "Comorbidités"])

# --- Radar cumulatif ---
st.subheader("Radar cumulatif")
angles = np.linspace(0, 2*np.pi, len(axes), endpoint=False).tolist()
angles += angles[:1]

fig, ax = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))
for profil in profils_selected:
    values = data_radar[profil] + data_radar[profil][:1]
    ax.plot(angles, values, label=profil, color=colors[profils.index(profil)], linewidth=2)
    ax.fill(angles, values, color=colors[profils.index(profil)], alpha=0.25)

ax.set_xticks(angles[:-1])
ax.set_xticklabels(axes)
ax.set_yticks([2,4,6,8,10])
ax.set_yticklabels(["2","4","6","8","10"])
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
st.pyplot(fig)

# --- Graphique réseau interactif ---
st.subheader("Réseau interactif : Profils → Symptômes → Comorbidités")

G = nx.Graph()

# Ajouter noeuds et edges
for profil in profils_selected:
    G.add_node(profil, type='profil')
    for symp in profils_info[profil]["Symptômes"]:
        G.add_node(symp, type='symptôme')
        G.add_edge(profil, symp)
    for com in profils_info[profil]["Comorbidités"]:
        G.add_node(com, type='comorbidité')
        G.add_edge(profil, com)
        for symp in profils_info[profil]["Symptômes"]:
            if com.lower() in symp.lower() or symp.lower() in com.lower():
                G.add_edge(symp, com)

# Appliquer filtres
nodes_to_keep = []
for node in G.nodes():
    node_type = G.nodes[node]['type']
    if (node_type == 'profil' and 'Profils' in filter_options) or \
       (node_type == 'symptôme' and 'Symptômes' in filter_options) or \
       (node_type == 'comorbidité' and 'Comorbidités' in filter_options):
        nodes_to_keep.append(node)

G_filtered = G.subgraph(nodes_to_keep)

# Position des noeuds
pos = nx.spring_layout(G_filtered, k=0.5, iterations=50)

# Tracer réseau avec plotly
edge_x = []
edge_y = []
for edge in G_filtered.edges():
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    edge_x.extend([x0, x1, None])
    edge_y.extend([y0, y1, None])

edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=1, color='#888'), hoverinfo='none', mode='lines')

node_x = []
node_y = []
node_text = []
node_color = []

color_map = {'profil':'#FF6F61', 'symptôme':'#88B04B', 'comorbidité':'#6B5B95'}

for node in G_filtered.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)
    node_text.append(node)
    node_color.append(color_map[G_filtered.nodes[node]['type']])

node_trace = go.Scatter(
    x=node_x, y=node_y, text=node_text, mode='markers+text', textposition="top center",
    hoverinfo='text', marker=dict(color=node_color, size=20)
)

fig_network = go.Figure(data=[edge_trace, node_trace])
fig_network.update_layout(showlegend=False, margin=dict(l=20,r=20,t=20,b=20))
st.plotly_chart(fig_network, use_container_width=True)
