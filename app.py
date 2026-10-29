import streamlit as st
import pandas as pd
import math
from io import BytesIO
import pydeck as pdk


# =========================================================
# CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="GeoExpert",
    page_icon="🏗️",
    layout="wide"
)


# =========================================================
# STYLE
# =========================================================

st.markdown("""
<style>
.main-title {
    font-size: 42px;
    font-weight: 700;
    margin-bottom: 0;
}
.subtitle {
    font-size: 18px;
    color: #666;
}
.decision-box {
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #ddd;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# EN-TETE
# =========================================================

st.markdown(
    '<div class="main-title">🏗️ GeoExpert</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    "Système d'aide à la décision pour l'implantation "
    "des reconnaissances géotechniques"
    "</div>",
    unsafe_allow_html=True
)

st.caption(
    "Prototype d'aide à la décision — les propositions doivent être "
    "validées par un ingénieur géotechnicien."
)

st.divider()


# =========================================================
# FONCTIONS GENERALES
# =========================================================

def offset_coordinates(lat, lon, x_m, y_m):
    """Conversion approximative d'un déplacement métrique local."""
    lat_rad = math.radians(lat)

    lat_deg = lat + y_m / 111000.0

    lon_deg = lon + x_m / (
        111000.0 * max(math.cos(lat_rad), 0.01)
    )

    return lat_deg, lon_deg


# =========================================================
# 32. TYPE DE RECONNAISSANCE
# =========================================================

def determine_type_sondage(
    type_ouvrage,
    contexte_geologique,
    remblai,
    eau,
    pente,
    priorite="Normale"
):

    if type_ouvrage in ["Bâtiment", "Pont"]:

        type_sondage = (
            "Sondage carotté / destructif avec essais "
            "pressiométriques Ménard"
        )

    elif type_ouvrage in ["Route", "Plateforme", "Conduite"]:

        type_sondage = (
            "Sondage géotechnique avec essais "
            "pénétrométriques"
        )

    elif type_ouvrage == "Mur de soutènement":

        type_sondage = (
            "Sondage géotechnique avec caractérisation "
            "des terrains et vérification de la stabilité"
        )

    else:

        type_sondage = "Sondage géotechnique adapté au projet"


    if contexte_geologique == "Terrains rocheux":

        type_sondage = (
            "Sondage carotté avec caractérisation "
            "du substratum rocheux"
        )

    elif contexte_geologique == "Terrains calcaires":

        type_sondage = (
            "Sondage géotechnique avec recherche "
            "de discontinuités et de cavités"
        )

    elif contexte_geologique == "Terrains marneux / argileux":

        type_sondage += (
            " + caractérisation des terrains fins"
        )

    elif contexte_geologique == "Terrains sableux":

        type_sondage += (
            " + caractérisation de la compacité"
        )

    elif contexte_geologique == "Terrains alluviaux":

        type_sondage += (
            " + caractérisation de la variabilité "
            "verticale et latérale"
        )

    elif contexte_geologique == "Remblais / terrains anthropisés":

        type_sondage += (
            " + reconnaissance de l'épaisseur et "
            "de l'hétérogénéité des remblais"
        )

    elif contexte_geologique == "Contexte géologique complexe":

        type_sondage += (
            " + investigations géologiques renforcées"
        )


    if remblai:

        type_sondage += (
            " + reconnaissance spécifique des remblais"
        )

    if eau:

        type_sondage += (
            " + suivi hydrogéologique"
        )

    if pente:

        type_sondage += (
            " + investigations de stabilité"
        )

    if priorite == "Très élevée":

        type_sondage += (
            " + investigation renforcée"
        )

    return type_sondage


# =========================================================
# 33. PROFONDEUR INDICATIVE
# =========================================================

def determine_profondeur(
    type_ouvrage,
    etages,
    sous_sols,
    contexte_geologique,
    niveau,
    remblai,
    eau
):

    if type_ouvrage == "Bâtiment":

        profondeur = 10.0

        if etages >= 5:
            profondeur += 3.0

        elif etages >= 3:
            profondeur += 1.5

        if sous_sols >= 1:
            profondeur += 3.0

        if sous_sols >= 2:
            profondeur += 2.0

    elif type_ouvrage == "Pont":

        profondeur = 15.0

        if niveau == "ÉLEVÉ":
            profondeur += 3.0

    elif type_ouvrage == "Plateforme":

        profondeur = 8.0

    elif type_ouvrage == "Route":

        profondeur = 5.0

    elif type_ouvrage == "Conduite":

        profondeur = 5.0

    elif type_ouvrage == "Mur de soutènement":

        profondeur = 8.0

    else:

        profondeur = 8.0


    if contexte_geologique in [
        "Terrains rocheux",
        "Terrains calcaires",
        "Contexte géologique complexe"
    ]:

        profondeur += 3.0


    if niveau == "ÉLEVÉ":

        profondeur += 2.0

    elif niveau == "MOYEN":

        profondeur += 1.0


    if remblai:

        profondeur += 2.0

    if eau:

        profondeur += 1.0


    return round(profondeur, 1)


# =========================================================
# 35. REGLES GEOTECHNIQUES INTELLIGENTES
# =========================================================

def generate_smart_rules(
    type_ouvrage,
    surface,
    longueur,
    etages,
    sous_sols,
    pente,
    remblai,
    eau,
    contexte_geologique,
    niveau
):

    rules = []


    # OUVRAGE

    if type_ouvrage == "Bâtiment":

        rules.append(
            "Le maillage couvre l'emprise du bâtiment "
            "afin de caractériser les terrains sous les "
            "futures fondations."
        )

        if etages >= 5:

            rules.append(
                "Le nombre d'étages important augmente "
                "le niveau de reconnaissance nécessaire."
            )

        if sous_sols >= 1:

            rules.append(
                "La présence de sous-sols nécessite de "
                "caractériser les terrains au droit des excavations."
            )


    elif type_ouvrage == "Pont":

        rules.append(
            "Les reconnaissances sont prioritairement "
            "associées aux zones d'appui et de fondation."
        )


    elif type_ouvrage == "Route":

        rules.append(
            "Les reconnaissances sont réparties suivant "
            "le tracé afin d'identifier les variations "
            "latérales des terrains."
        )


    elif type_ouvrage == "Conduite":

        rules.append(
            "Les reconnaissances suivent le tracé et "
            "sont renforcées au niveau des changements "
            "potentiels de contexte."
        )


    elif type_ouvrage == "Plateforme":

        rules.append(
            "La reconnaissance vise à caractériser "
            "l'homogénéité de la plateforme."
        )


    elif type_ouvrage == "Mur de soutènement":

        rules.append(
            "Les reconnaissances sont renforcées au droit "
            "de la zone de fondation et du terrain susceptible "
            "de participer à la stabilité."
        )


    # SURFACE

    if surface > 10000:

        rules.append(
            "La superficie très importante justifie une "
            "densification du maillage."
        )

    elif surface > 5000:

        rules.append(
            "La superficie importante justifie une "
            "densification du maillage."
        )


    # PENTE

    if pente:

        rules.append(
            "La pente conduit à renforcer les investigations "
            "dans les zones susceptibles de présenter "
            "des problèmes de stabilité."
        )


    # REMBLAI

    if remblai:

        rules.append(
            "Les remblais nécessitent une reconnaissance "
            "de leur épaisseur, nature et hétérogénéité."
        )


    # EAU

    if eau:

        rules.append(
            "Le contexte hydrogéologique doit être pris "
            "en compte dans le programme de reconnaissance."
        )


    # GEOLOGIE

    if contexte_geologique == "Terrains alluviaux":

        rules.append(
            "Les terrains alluviaux peuvent présenter "
            "une variabilité verticale et latérale importante."
        )

    elif contexte_geologique == "Terrains marneux / argileux":

        rules.append(
            "Les terrains fins nécessitent une attention "
            "particulière vis-à-vis de la compressibilité "
            "et des variations hydriques."
        )

    elif contexte_geologique == "Terrains sableux":

        rules.append(
            "Les terrains sableux nécessitent une "
            "caractérisation de leur compacité."
        )

    elif contexte_geologique == "Terrains calcaires":

        rules.append(
            "Une recherche de discontinuités ou de cavités "
            "est recommandée."
        )

    elif contexte_geologique == "Terrains rocheux":

        rules.append(
            "La qualité et la fracturation du massif "
            "doivent être caractérisées."
        )

    elif contexte_geologique == "Remblais / terrains anthropisés":

        rules.append(
            "Les terrains anthropisés nécessitent une "
            "reconnaissance renforcée de leur hétérogénéité."
        )

    elif contexte_geologique == "Contexte géologique complexe":

        rules.append(
            "La complexité géologique justifie une "
            "densification des reconnaissances."
        )


    # COMPLEXITE

    if niveau == "ÉLEVÉ":

        rules.append(
            "Le niveau de complexité élevé conduit à "
            "augmenter la densité et/ou la profondeur "
            "des reconnaissances."
        )

    elif niveau == "MOYEN":

        rules.append(
            "Le niveau de complexité moyen conduit à "
            "adapter le maillage aux facteurs identifiés."
        )

    else:

        rules.append(
            "Le niveau de complexité faible permet de "
            "privilégier une couverture générale de l'emprise."
        )


    return rules


# =========================================================
# 41–44. SCORE INDIVIDUEL
# =========================================================

def calculate_point_score(
    x,
    y,
    longueur,
    largeur,
    niveau,
    remblai,
    eau,
    pente,
    contexte_geologique,
    type_ouvrage,
    index,
    total
):

    score = 20


    # COMPLEXITE

    if niveau == "ÉLEVÉ":
        score += 20

    elif niveau == "MOYEN":
        score += 10


    # GEOLOGIE

    if contexte_geologique == "Contexte géologique complexe":

        score += 20

    elif contexte_geologique in [
        "Terrains calcaires",
        "Terrains alluviaux",
        "Terrains marneux / argileux",
        "Remblais / terrains anthropisés",
        "Terrains rocheux"
    ]:

        score += 12

    elif contexte_geologique == "Terrains sableux":

        score += 8


    # REMBLAI

    if remblai:
        score += 12


    # EAU

    if eau:
        score += 10


    # PENTE

    if pente:

        if largeur > 0:

            position = abs(y) / max(largeur / 2, 1)

        else:

            position = 0

        if position > 0.6:

            score += 12

        else:

            score += 6


    # PERIPHERIE

    if longueur > 0 and largeur > 0:

        distance_bord_x = (
            longueur / 2 - abs(x)
        )

        distance_bord_y = (
            largeur / 2 - abs(y)
        )

        distance_bord = min(
            distance_bord_x,
            distance_bord_y
        )

        largeur_reference = min(
            longueur,
            largeur
        )

        if distance_bord < largeur_reference * 0.15:

            score += 12

        elif distance_bord < largeur_reference * 0.30:

            score += 6


    # OUVRAGES LINEAIRES / PONTS

    if type_ouvrage == "Pont":

        if index == 0 or index == total - 1:

            score += 15


    if type_ouvrage in ["Route", "Conduite"]:

        if index == 0 or index == total - 1:

            score += 8


    return min(round(score), 100)


# =========================================================
# 45. GENERATION DES POINTS
# =========================================================

def generate_points(
    n,
    lat,
    lon,
    longueur,
    largeur,
    orientation,
    type_ouvrage,
    niveau,
    remblai,
    eau,
    pente,
    contexte_geologique,
    etages,
    sous_sols
):

    points = []

    L = longueur if longueur > 0 else 50.0
    W = largeur if largeur > 0 else 40.0


    # =====================================================
    # BATIMENT / PLATEFORME / MUR / AUTRE
    # =====================================================

    if type_ouvrage in [
        "Bâtiment",
        "Plateforme",
        "Mur de soutènement",
        "Autre"
    ]:

        positions = []


        # ANGLES PRIORITAIRES

        if n >= 4:

            positions.extend([
                (-L / 2, -W / 2),
                (L / 2, -W / 2),
                (L / 2, W / 2),
                (-L / 2, W / 2)
            ])


        # CENTRE

        remaining = n - len(positions)

        if remaining > 0:

            if remaining == 1:

                positions.append((0, 0))

            else:

                cols = math.ceil(
                    math.sqrt(remaining)
                )

                rows = math.ceil(
                    remaining / cols
                )

                for row in range(rows):

                    for col in range(cols):

                        if len(positions) >= n:
                            break

                        if cols == 1:

                            x = 0

                        else:

                            x = (
                                -L * 0.35
                                + col
                                * (
                                    L * 0.70
                                    / (cols - 1)
                                )
                            )


                        if rows == 1:

                            y = 0

                        else:

                            y = (
                                -W * 0.35
                                + row
                                * (
                                    W * 0.70
                                    / (rows - 1)
                                )
                            )


                        candidate = (x, y)

                        if candidate not in positions:

                            positions.append(candidate)


        # CONTEXTE COMPLEXE
        # priorité aux positions périphériques

        if niveau == "ÉLEVÉ":

            positions = sorted(
                positions,
                key=lambda p: (
                    abs(p[0]) + abs(p[1])
                ),
                reverse=True
            )


        for i, (x, y) in enumerate(
            positions[:n]
        ):

            p_lat, p_lon = offset_coordinates(
                lat,
                lon,
                x,
                y
            )

            points.append({

                "Point": f"P{i + 1}",

                "Latitude": round(
                    p_lat,
                    6
                ),

                "Longitude": round(
                    p_lon,
                    6
                ),

                "X_m": round(
                    x,
                    1
                ),

                "Y_m": round(
                    y,
                    1
                )
            })


    # =====================================================
    # ROUTE / CONDUITE / PONT
    # =====================================================

    else:

        total = (
            longueur
            if longueur > 0
            else 100.0
        )


        for i in range(n):

            if n == 1:

                distance = total / 2

            else:

                distance = (
                    i * total / (n - 1)
                )


            distance_centre = (
                distance - total / 2
            )


            if orientation == "Est-Ouest":

                x = distance_centre
                y = 0

            else:

                x = 0
                y = distance_centre


            p_lat, p_lon = offset_coordinates(
                lat,
                lon,
                x,
                y
            )


            points.append({

                "Point": f"P{i + 1}",

                "Latitude": round(
                    p_lat,
                    6
                ),

                "Longitude": round(
                    p_lon,
                    6
                ),

                "X_m": round(
                    x,
                    1
                ),

                "Y_m": round(
                    y,
                    1
                )
            })


    points_df = pd.DataFrame(points)


    # =====================================================
    # ANALYSE INDIVIDUELLE
    # =====================================================

    scores = []
    priorites = []
    justifications = []
    types = []
    profondeurs = []
    fiabilites = []


    for i, row in points_df.iterrows():

        score_point = calculate_point_score(

            row["X_m"],
            row["Y_m"],
            L,
            W,
            niveau,
            remblai,
            eau,
            pente,
            contexte_geologique,
            type_ouvrage,
            i,
            len(points_df)

        )


        scores.append(
            score_point
        )


        # PRIORITE

        if score_point >= 75:

            priorite = "Très élevée"

        elif score_point >= 55:

            priorite = "Élevée"

        elif score_point >= 35:

            priorite = "Moyenne"

        else:

            priorite = "Normale"


        priorites.append(
            priorite
        )


        # TYPE

        type_point = determine_type_sondage(

            type_ouvrage,
            contexte_geologique,
            remblai,
            eau,
            pente,
            priorite

        )

        types.append(
            type_point
        )


        # JUSTIFICATION

        raisons = []


        if (
            abs(row["X_m"]) >= L * 0.35
            or abs(row["Y_m"]) >= W * 0.35
        ):

            raisons.append(
                "Position périphérique"
            )


        if niveau == "ÉLEVÉ":

            raisons.append(
                "Complexité globale élevée"
            )

        elif niveau == "MOYEN":

            raisons.append(
                "Complexité globale moyenne"
            )


        if contexte_geologique != "Non renseigné":

            raisons.append(
                f"Contexte géologique : "
                f"{contexte_geologique}"
            )


        if remblai:

            raisons.append(
                "Présence potentielle de remblais"
            )


        if eau:

            raisons.append(
                "Contexte hydrogéologique"
            )


        if pente:

            raisons.append(
                "Terrain présentant une pente"
            )


        if type_ouvrage == "Pont" and (
            i == 0
            or i == len(points_df) - 1
        ):

            raisons.append(
                "Zone d'appui potentielle"
            )


        if type_ouvrage in ["Route", "Conduite"]:

            raisons.append(
                "Position sur le tracé"
            )


        if not raisons:

            raisons.append(
                "Couverture régulière de l'emprise"
            )


        justifications.append(
            " ; ".join(raisons)
        )


        # PROFONDEUR INDIVIDUELLE

        profondeur_point = determine_profondeur(

            type_ouvrage,
            etages,
            sous_sols,
            contexte_geologique,
            niveau,
            remblai,
            eau

        )


        if score_point >= 75:

            profondeur_point += 2

        elif score_point >= 55:

            profondeur_point += 1


        profondeurs.append(
            round(
                profondeur_point,
                1
            )
        )


        # FIABILITE

        if (
            niveau == "ÉLEVÉ"
            and (
                remblai
                or pente
                or eau
                or contexte_geologique
                == "Contexte géologique complexe"
            )
        ):

            fiabilite = "Moyenne"

        elif geologie_globale and etude_ancienne_globale:

            fiabilite = "Élevée"

        elif geologie_globale:

            fiabilite = "Moyenne"

        else:

            fiabilite = "Faible"


        fiabilites.append(
            fiabilite
        )


    points_df["Score de priorité"] = scores

    points_df["Priorité"] = priorites

    points_df[
        "Reconnaissance recommandée"
    ] = types

    points_df[
        "Profondeur indicative (m)"
    ] = profondeurs

    points_df[
        "Justification locale"
    ] = justifications

    points_df[
        "Niveau de fiabilité"
    ] = fiabilites

    points_df[
        "Type"
    ] = "Reconnaissance géotechnique"


    return points_df


# =========================================================
# 46. ZONES DE VIGILANCE
# =========================================================

def create_vigilance_zones(points_df):

    zones = points_df[
        points_df["Score de priorité"] >= 75
    ].copy()

    return zones


# =========================================================
# 47. RESUME DECISIONNEL AUTOMATIQUE
# =========================================================

def generate_decision_summary(
    points_df,
    niveau,
    type_ouvrage,
    contexte_geologique
):

    if len(points_df) == 0:

        return "Aucun point n'a été généré."


    point_max = points_df.loc[
        points_df["Score de priorité"].idxmax()
    ]


    nb_tres_prioritaires = sum(
        points_df["Priorité"]
        == "Très élevée"
    )


    nb_prioritaires = sum(
        points_df["Priorité"]
        == "Élevée"
    )


    resume = (

        f"GeoExpert identifie un niveau de "
        f"complexité **{niveau}** pour cet ouvrage. "

        f"{len(points_df)} points de reconnaissance "
        f"ont été proposés. "

    )


    if nb_tres_prioritaires > 0:

        resume += (

            f"{nb_tres_prioritaires} point(s) présentent "
            f"une priorité très élevée. "

        )


    if nb_prioritaires > 0:

        resume += (

            f"{nb_prioritaires} point(s) présentent "
            f"une priorité élevée. "

        )


    resume += (

        f"Le point présentant le score de priorité "
        f"le plus élevé est **{point_max['Point']}**, "
        f"avec un score de "
        f"**{point_max['Score de priorité']}/100**. "

    )


    resume += (

        f"Sa justification principale est : "
        f"{point_max['Justification locale']}. "

    )


    if niveau == "ÉLEVÉ":

        resume += (

            "Une campagne de reconnaissance renforcée "
            "est recommandée."

        )

    elif niveau == "MOYEN":

        resume += (

            "Une campagne adaptée aux facteurs identifiés "
            "est recommandée."

        )

    else:

        resume += (

            "Une campagne préliminaire de base "
            "est proposée."

        )


    resume += (

        " Cette proposition constitue une aide à la décision "
        "et doit être vérifiée par l'ingénieur géotechnicien."

    )


    return resume


# =========================================================
# VARIABLES GLOBALES POUR LES POINTS
# =========================================================

geologie_globale = False
etude_ancienne_globale = False


# =========================================================
# ONGLET PRINCIPAL
# =========================================================

tab1, tab2, tab3 = st.tabs([
    "🏗️ Analyse du projet",
    "📚 Méthodologie",
    "⚠️ Limites du système"
])


# =========================================================
# TAB 1
# =========================================================

with tab1:

    # =====================================================
    # 1. INFORMATIONS GENERALES
    # =====================================================

    st.header(
        "📋 1. Informations générales du projet"
    )


    nom_projet = st.text_input(
        "Nom du projet"
    )


    ville = st.text_input(
        "Ville / Localisation"
    )


    col1, col2 = st.columns(2)


    with col1:

        latitude = st.number_input(
            "Latitude du point de référence",
            value=33.5731,
            format="%.6f"
        )


    with col2:

        longitude = st.number_input(
            "Longitude du point de référence",
            value=-7.5898,
            format="%.6f"
        )


    type_ouvrage = st.selectbox(
        "Type d'ouvrage",
        [
            "Sélectionner...",
            "Bâtiment",
            "Plateforme",
            "Route",
            "Pont",
            "Conduite",
            "Mur de soutènement",
            "Autre"
        ]
    )


    # =====================================================
    # 2. CARACTERISTIQUES
    # =====================================================

    if type_ouvrage != "Sélectionner...":

        st.divider()

        st.header(
            "📐 2. Caractéristiques de l'ouvrage"
        )


        surface = 0.0
        longueur = 0.0
        largeur = 0.0
        etages = 0
        sous_sols = 0
        nb_appuis = 0
        diametre = 0.0
        pk_debut = 0.0
        pk_fin = 0.0


        if type_ouvrage == "Bâtiment":

            surface = st.number_input(
                "Surface d'emprise du bâtiment (m²)",
                min_value=0.0,
                step=100.0
            )

            longueur = st.number_input(
                "Longueur du bâtiment (m)",
                min_value=0.0,
                step=1.0
            )

            largeur = st.number_input(
                "Largeur du bâtiment (m)",
                min_value=0.0,
                step=1.0
            )

            etages = st.number_input(
                "Nombre d'étages",
                min_value=0,
                step=1
            )

            sous_sols = st.number_input(
                "Nombre de sous-sols",
                min_value=0,
                step=1
            )


        elif type_ouvrage == "Plateforme":

            surface = st.number_input(
                "Surface de la plateforme (m²)",
                min_value=0.0,
                step=100.0
            )

            longueur = st.number_input(
                "Longueur (m)",
                min_value=0.0,
                step=10.0
            )

            largeur = st.number_input(
                "Largeur (m)",
                min_value=0.0,
                step=10.0
            )


        elif type_ouvrage == "Route":

            longueur = st.number_input(
                "Longueur du tracé (m)",
                min_value=0.0,
                step=100.0
            )

            largeur = st.number_input(
                "Largeur de la chaussée (m)",
                min_value=0.0,
                step=1.0
            )


        elif type_ouvrage == "Pont":

            longueur = st.number_input(
                "Longueur du pont (m)",
                min_value=0.0,
                step=10.0
            )

            largeur = st.number_input(
                "Largeur du pont (m)",
                min_value=0.0,
                step=1.0
            )

            nb_appuis = st.number_input(
                "Nombre d'appuis",
                min_value=1,
                step=1
            )


        elif type_ouvrage == "Conduite":

            longueur = st.number_input(
                "Longueur de la conduite (m)",
                min_value=0.0,
                step=100.0
            )

            diametre = st.number_input(
                "Diamètre de la conduite (mm)",
                min_value=0.0,
                step=50.0
            )

            pk_debut = st.number_input(
                "PK début",
                min_value=0.0,
                step=1.0
            )

            pk_fin = st.number_input(
                "PK fin",
                min_value=0.0,
                step=1.0
            )


        else:

            surface = st.number_input(
                "Surface estimée de l'ouvrage (m²)",
                min_value=0.0,
                step=100.0
            )


        # =================================================
        # 3. GEOMETRIE
        # =================================================

        st.divider()

        st.header(
            "📍 3. Géométrie et orientation"
        )


        orientation = "Est-Ouest"


        if type_ouvrage in [
            "Route",
            "Conduite",
            "Pont"
        ]:

            orientation = st.selectbox(
                "Orientation simplifiée du tracé",
                [
                    "Est-Ouest",
                    "Nord-Sud"
                ]
            )


        if longueur > 0 and largeur > 0:

            surface_calculee = (
                longueur * largeur
            )

            st.info(
                f"Emprise géométrique : "
                f"{longueur:.1f} m × "
                f"{largeur:.1f} m = "
                f"{surface_calculee:.1f} m²"
            )

        elif surface > 0:

            st.info(
                f"Surface déclarée : "
                f"{surface:.1f} m²"
            )

        else:

            st.warning(
                "Renseignez les dimensions principales "
                "du projet pour permettre l'implantation."
            )


        # =================================================
        # 4. CONTEXTE
        # =================================================

        st.divider()

        st.header(
            "🌍 4. Contexte du site"
        )


        col1, col2 = st.columns(2)


        with col1:

            pente = st.checkbox(
                "Terrain présentant une pente"
            )

            remblai = st.checkbox(
                "Présence potentielle de remblai"
            )

            constructions = st.checkbox(
                "Présence de constructions voisines"
            )


        with col2:

            eau = st.checkbox(
                "Présence d'eau / contexte hydrogéologique particulier"
            )

            geologie = st.checkbox(
                "Informations géologiques disponibles"
            )

            etude_ancienne = st.checkbox(
                "Étude géotechnique antérieure disponible"
            )


        geologie_globale = geologie
        etude_ancienne_globale = etude_ancienne


        # =================================================
        # 4 BIS. GEOLOGIE
        # =================================================

        st.divider()

        st.header(
            "🗺️ 4 bis. Contexte géologique du site"
        )


        contexte_geologique = st.selectbox(
            "Contexte géologique général",
            [
                "Non renseigné",
                "Terrains alluviaux",
                "Terrains marneux / argileux",
                "Terrains sableux",
                "Terrains calcaires",
                "Terrains rocheux",
                "Terrains volcaniques",
                "Remblais / terrains anthropisés",
                "Contexte géologique complexe"
            ]
        )


        st.caption(
            "Le contexte géologique constitue une "
            "information d'entrée pour orienter "
            "les reconnaissances."
        )


        # =================================================
        # 5. ANALYSE
        # =================================================

        st.divider()

        st.header(
            "🧠 5. Analyse et décision"
        )


        analyser = st.button(
            "🧠 Analyser le projet",
            type="primary",
            use_container_width=True
        )


        if analyser:

            # =================================================
            # SCORE GLOBAL
            # =================================================

            score = 0

            facteurs = []

            regles = []


            # GEOLOGIE

            if contexte_geologique == (
                "Contexte géologique complexe"
            ):

                score += 2

                facteurs.append(
                    "Contexte géologique complexe identifié."
                )

            elif contexte_geologique in [
                "Terrains alluviaux",
                "Terrains marneux / argileux",
                "Remblais / terrains anthropisés",
                "Terrains rocheux",
                "Terrains calcaires"
            ]:

                score += 1

                facteurs.append(
                    f"Contexte géologique : "
                    f"{contexte_geologique}."
                )

            else:

                facteurs.append(
                    f"Contexte géologique : "
                    f"{contexte_geologique}."
                )


            # TYPE OUVRAGE

            if type_ouvrage in [
                "Pont",
                "Bâtiment"
            ]:

                score += 2

                facteurs.append(
                    "Type d'ouvrage nécessitant "
                    "une reconnaissance détaillée."
                )

            elif type_ouvrage in [
                "Plateforme",
                "Route",
                "Conduite",
                "Mur de soutènement"
            ]:

                score += 1

                facteurs.append(
                    "Ouvrage pris en compte dans "
                    "l'analyse géotechnique."
                )


            # BATIMENT

            if type_ouvrage == "Bâtiment":

                if surface > 5000:

                    score += 2

                    facteurs.append(
                        "Emprise importante du bâtiment."
                    )

                elif surface > 2000:

                    score += 1

                    facteurs.append(
                        "Emprise significative du bâtiment."
                    )


                if etages >= 5:

                    score += 2

                    facteurs.append(
                        "Nombre d'étages important."
                    )


                if sous_sols >= 1:

                    score += 1

                    facteurs.append(
                        "Présence de sous-sols."
                    )


            # PONT

            if type_ouvrage == "Pont" and nb_appuis >= 3:

                score += 2

                facteurs.append(
                    "Nombre important d'appuis."
                )


            # CONDITIONS

            if pente:

                score += 2

                facteurs.append(
                    "Terrain présentant une pente."
                )


            if remblai:

                score += 2

                facteurs.append(
                    "Présence potentielle de remblai."
                )


            if constructions:

                score += 1

                facteurs.append(
                    "Présence de constructions voisines."
                )


            if eau:

                score += 2

                facteurs.append(
                    "Contexte hydrogéologique à prendre en compte."
                )


            if not geologie:

                score += 1

                facteurs.append(
                    "Informations géologiques non renseignées."
                )


            # =================================================
            # NIVEAU
            # =================================================

            if score <= 3:

                niveau = "FAIBLE"

            elif score <= 6:

                niveau = "MOYEN"

            else:

                niveau = "ÉLEVÉ"


            # =================================================
            # NOMBRE DE POINTS
            # =================================================

            if type_ouvrage == "Bâtiment":

                if surface > 5000:

                    nb_points = 8

                    regles.append(
                        "Grande emprise → densification "
                        "de l'implantation."
                    )

                elif surface > 2000:

                    nb_points = 6

                    regles.append(
                        "Emprise significative → "
                        "maillage renforcé."
                    )

                else:

                    nb_points = 4

                    regles.append(
                        "Emprise courante → "
                        "couverture de base."
                    )


                if niveau == "ÉLEVÉ":

                    nb_points += 1

                    regles.append(
                        "Complexité élevée → "
                        "ajout d'un point."
                    )


                if sous_sols >= 1:

                    nb_points += 1

                    regles.append(
                        "Sous-sol → "
                        "point supplémentaire proposé."
                    )


            elif type_ouvrage == "Plateforme":

                if surface > 10000:

                    nb_points = 8

                elif surface > 5000:

                    nb_points = 6

                else:

                    nb_points = 4


                regles.append(
                    "Nombre de points lié à "
                    "l'emprise de la plateforme."
                )


                if niveau == "ÉLEVÉ":

                    nb_points += 1


            elif type_ouvrage == "Pont":

                nb_points = max(
                    2,
                    int(nb_appuis)
                )

                regles.append(
                    "Points associés aux zones d'appui."
                )


                if niveau == "ÉLEVÉ":

                    nb_points += 1


            elif type_ouvrage in [
                "Route",
                "Conduite"
            ]:

                nb_points = max(
                    3,
                    math.ceil(
                        max(longueur, 100)
                        / 200
                    )
                )

                regles.append(
                    "Répartition indicative le long "
                    "du tracé avec un pas maximal "
                    "de 200 m."
                )


                if niveau == "ÉLEVÉ":

                    nb_points += 1


            else:

                nb_points = 4

                regles.append(
                    "Maillage de base pour un "
                    "ouvrage non standard."
                )


            nb_points = min(
                max(nb_points, 2),
                12
            )


            # =================================================
            # RISQUES
            # =================================================

            risques = []


            if pente:

                risques.append(
                    "Risque de mouvements de terrain / "
                    "instabilité lié à la pente."
                )


            if remblai:

                risques.append(
                    "Hétérogénéité possible des remblais "
                    "et risque de tassements différentiels."
                )


            if eau:

                risques.append(
                    "Présence potentielle d'eau souterraine."
                )


            if sous_sols >= 1:

                risques.append(
                    "Excavations liées aux sous-sols "
                    "nécessitant une caractérisation du terrain."
                )


            if type_ouvrage == "Bâtiment" and etages >= 5:

                risques.append(
                    "Charges importantes transmises au sol."
                )


            if type_ouvrage == "Pont":

                risques.append(
                    "Conditions géotechniques à vérifier "
                    "au droit des appuis et fondations."
                )


            if type_ouvrage in [
                "Route",
                "Plateforme"
            ]:

                risques.append(
                    "Variabilité possible des sols "
                    "le long de l'emprise."
                )


            if not risques:

                risques.append(
                    "Aucun facteur géotechnique particulier "
                    "identifié à ce stade."
                )


            # =================================================
            # 32. TYPE
            # =================================================

            type_sondage = determine_type_sondage(
                type_ouvrage,
                contexte_geologique,
                remblai,
                eau,
                pente
            )


            # =================================================
            # 33. PROFONDEUR
            # =================================================

            profondeur_indicative = determine_profondeur(
                type_ouvrage,
                etages,
                sous_sols,
                contexte_geologique,
                niveau,
                remblai,
                eau
            )


            # =================================================
            # 34. POINTS / SONDAGES / ESSAIS
            # =================================================

            nombre_points_implantation = nb_points

            nombre_sondages = nb_points


            if type_ouvrage == "Pont":

                nombre_sondages = max(
                    nb_points,
                    int(nb_appuis)
                )


            if type_ouvrage in [
                "Bâtiment",
                "Pont"
            ]:

                nombre_essais_pressiometriques = (
                    nb_points
                )

            else:

                nombre_essais_pressiometriques = 0


            if type_ouvrage in [
                "Route",
                "Plateforme",
                "Conduite"
            ]:

                nombre_essais_penetro = (
                    nb_points
                )

            else:

                nombre_essais_penetro = 0


            # =================================================
            # RECONNAISSANCES
            # =================================================

            reconnaissances = [

                f"{type_sondage}.",

                f"Profondeur indicative : "
                f"{profondeur_indicative:.1f} m."

            ]


            if nombre_essais_pressiometriques > 0:

                reconnaissances.append(

                    f"Essais pressiométriques Ménard "
                    f"associés aux sondages principaux "
                    f"({nombre_essais_pressiometriques} "
                    f"points indicatifs)."

                )


            if nombre_essais_penetro > 0:

                reconnaissances.append(

                    f"Essais pénétrométriques complémentaires "
                    f"({nombre_essais_penetro} points indicatifs)."

                )


            if eau:

                reconnaissances.append(
                    "Suivi du niveau d'eau / "
                    "reconnaissance hydrogéologique."
                )


            if remblai:

                reconnaissances.append(
                    "Investigations spécifiques des zones "
                    "potentiellement remblayées."
                )


            # =================================================
            # 35. REGLES
            # =================================================

            regles_intelligentes = generate_smart_rules(

                type_ouvrage,
                surface,
                longueur,
                etages,
                sous_sols,
                pente,
                remblai,
                eau,
                contexte_geologique,
                niveau

            )


            # =================================================
            # CONFIANCE
            # =================================================

            informations_renseignees = 0


            if ville:
                informations_renseignees += 1


            if longueur > 0 or surface > 0:
                informations_renseignees += 1


            if geologie:
                informations_renseignees += 1


            if etude_ancienne:
                informations_renseignees += 1


            if informations_renseignees >= 3:

                confiance = "Élevée"

            elif informations_renseignees >= 2:

                confiance = "Moyenne"

            else:

                confiance = "Faible"


            # =================================================
            # 45. GENERATION
            # =================================================

            points_df = generate_points(

                nb_points,
                latitude,
                longitude,
                longueur,
                largeur,
                orientation,
                type_ouvrage,
                niveau,
                remblai,
                eau,
                pente,
                contexte_geologique,
                etages,
                sous_sols

            )


            # =================================================
            # 46. VIGILANCE
            # =================================================

            zones_vigilance = create_vigilance_zones(
                points_df
            )


            # =================================================
            # 47. RESUME
            # =================================================

            decision_summary = generate_decision_summary(

                points_df,
                niveau,
                type_ouvrage,
                contexte_geologique

            )


            # =================================================
            # RESULTATS
            # =================================================

            st.divider()

            st.header(
                "📊 6. Résultats de l'analyse"
            )


            c1, c2, c3, c4 = st.columns(4)


            with c1:

                st.metric(
                    "Indice de complexité",
                    score
                )


            with c2:

                st.metric(
                    "Niveau",
                    niveau
                )


            with c3:

                st.metric(
                    "Points proposés",
                    nb_points
                )


            with c4:

                st.metric(
                    "Confiance",
                    confiance
                )


            # FACTEURS

            st.subheader(
                "🔎 Facteurs pris en compte"
            )


            for facteur in facteurs:

                st.write(
                    "•",
                    facteur
                )


            # RISQUES

            st.subheader(
                "⚠️ Risques géotechniques identifiés"
            )


            for risque in risques:

                st.write(
                    "•",
                    risque
                )


            # =================================================
            # 32
            # =================================================

            st.subheader(
                "🔬 32. Type de reconnaissance proposé"
            )


            st.info(
                f"**Reconnaissance principale :** "
                f"{type_sondage}"
            )


            # =================================================
            # 33
            # =================================================

            st.subheader(
                "📏 33. Profondeur indicative"
            )


            st.metric(
                "Profondeur indicative",
                f"{profondeur_indicative:.1f} m"
            )


            st.caption(
                "⚠️ Valeur indicative du prototype. "
                "La profondeur définitive doit être "
                "déterminée par l'ingénieur géotechnicien."
            )


            # =================================================
            # 34
            # =================================================

            st.subheader(
                "📊 34. Points, sondages et essais"
            )


            s1, s2, s3, s4 = st.columns(4)


            with s1:

                st.metric(
                    "Points d'implantation",
                    nombre_points_implantation
                )


            with s2:

                st.metric(
                    "Sondages",
                    nombre_sondages
                )


            with s3:

                st.metric(
                    "Essais pressiométriques",
                    nombre_essais_pressiometriques
                )


            with s4:

                st.metric(
                    "Essais pénétrométriques",
                    nombre_essais_penetro
                )


            # RECONNAISSANCES

            st.subheader(
                "🧪 Reconnaissances géotechniques recommandées"
            )


            for reconnaissance in reconnaissances:

                st.write(
                    "•",
                    reconnaissance
                )


            # =================================================
            # 35
            # =================================================

            st.subheader(
                "🧠 35. Règles géotechniques intelligentes"
            )


            for regle in regles_intelligentes:

                st.write(
                    "•",
                    regle
                )


            # =================================================
            # 41–44
            # =================================================

            st.divider()

            st.header(
                "🎯 41–44. Analyse individuelle des points"
            )


            st.info(
                "Chaque point reçoit un score individuel "
                "de priorité compris entre 0 et 100. "
                "Le score permet de hiérarchiser les points "
                "selon leur position et les caractéristiques "
                "géotechniques du projet."
            )


            p1, p2, p3, p4 = st.columns(4)


            with p1:

                st.metric(
                    "Score maximal",
                    f"{points_df['Score de priorité'].max()}/100"
                )


            with p2:

                st.metric(
                    "Score moyen",
                    f"{points_df['Score de priorité'].mean():.0f}/100"
                )


            with p3:

                st.metric(
                    "Priorité très élevée",
                    sum(
                        points_df["Priorité"]
                        == "Très élevée"
                    )
                )


            with p4:

                st.metric(
                    "Priorité élevée",
                    sum(
                        points_df["Priorité"]
                        == "Élevée"
                    )
                )


            st.subheader(
                "📋 Tableau détaillé des points"
            )


            st.dataframe(

                points_df[

                    [
                        "Point",
                        "Latitude",
                        "Longitude",
                        "X_m",
                        "Y_m",
                        "Score de priorité",
                        "Priorité",
                        "Reconnaissance recommandée",
                        "Profondeur indicative (m)",
                        "Justification locale",
                        "Niveau de fiabilité"
                    ]

                ],

                use_container_width=True,
                hide_index=True

            )


            # =================================================
            # 46
            # =================================================

            st.subheader(
                "🚨 46. Zones de vigilance"
            )


            if len(zones_vigilance) > 0:

                st.warning(
                    f"{len(zones_vigilance)} point(s) "
                    "ont été identifiés comme zones de "
                    "vigilance renforcée."
                )


                st.dataframe(

                    zones_vigilance[

                        [
                            "Point",
                            "Latitude",
                            "Longitude",
                            "Score de priorité",
                            "Priorité",
                            "Justification locale"
                        ]

                    ],

                    use_container_width=True,
                    hide_index=True

                )

            else:

                st.success(
                    "Aucune zone de vigilance renforcée "
                    "n'a été identifiée."
                )


            # =================================================
            # 47
            # =================================================

            st.subheader(
                "🎯 47. Résumé décisionnel automatique"
            )


            st.info(
                decision_summary
            )


            # =================================================
            # RECOMMANDATION
            # =================================================

            st.subheader(
                "🏗️ Recommandation du système"
            )


            if niveau == "ÉLEVÉ":

                st.error(
                    "Le système identifie un contexte "
                    "géotechnique à complexité ÉLEVÉE. "
                    "Une campagne de reconnaissance renforcée "
                    "est recommandée."
                )

            elif niveau == "MOYEN":

                st.warning(
                    "Le système identifie un contexte "
                    "géotechnique à complexité MOYENNE. "
                    "Une campagne adaptée aux facteurs "
                    "identifiés est recommandée."
                )

            else:

                st.success(
                    "Le système identifie un contexte "
                    "géotechnique à complexité FAIBLE. "
                    "Une campagne préliminaire de base "
                    "est proposée."
                )


            # =================================================
            # SYNTHESE
            # =================================================

            st.subheader(
                "📄 Synthèse de la décision"
            )


            synthese = pd.DataFrame({

                "Paramètre": [

                    "Projet",
                    "Localisation",
                    "Type d'ouvrage",
                    "Contexte géologique",
                    "Indice de complexité",
                    "Niveau",
                    "Confiance",
                    "Points d'implantation",
                    "Nombre de sondages",
                    "Profondeur indicative",
                    "Type de reconnaissance",
                    "Score individuel maximal",
                    "Nombre de points très prioritaires"

                ],

                "Valeur": [

                    nom_projet
                    if nom_projet
                    else "Non renseigné",

                    ville
                    if ville
                    else "Non renseignée",

                    type_ouvrage,

                    contexte_geologique,

                    score,

                    niveau,

                    confiance,

                    nombre_points_implantation,

                    nombre_sondages,

                    f"{profondeur_indicative:.1f} m",

                    type_sondage,

                    points_df[
                        "Score de priorité"
                    ].max(),

                    sum(
                        points_df["Priorité"]
                        == "Très élevée"
                    )

                ]

            })


            st.dataframe(
                synthese,
                use_container_width=True,
                hide_index=True
            )


            # =================================================
            # 48. CARTE
            # =================================================

            st.subheader(
                "🗺️ 48. Carte intelligente des points"
            )


            st.caption(
                "Les points sont représentés selon leur "
                "niveau de priorité. Les informations "
                "détaillées sont disponibles au survol."
            )


            map_df = points_df.copy()


            L = (
                longueur
                if longueur > 0
                else 50.0
            )


            W = (
                largeur
                if largeur > 0
                else 40.0
            )


            nord_ouest = offset_coordinates(
                latitude,
                longitude,
                -L / 2,
                W / 2
            )


            nord_est = offset_coordinates(
                latitude,
                longitude,
                L / 2,
                W / 2
            )


            sud_est = offset_coordinates(
                latitude,
                longitude,
                L / 2,
                -W / 2
            )


            sud_ouest = offset_coordinates(
                latitude,
                longitude,
                -L / 2,
                -W / 2
            )


            polygon_df = pd.DataFrame({

                "polygon": [[

                    [
                        nord_ouest[1],
                        nord_ouest[0]
                    ],

                    [
                        nord_est[1],
                        nord_est[0]
                    ],

                    [
                        sud_est[1],
                        sud_est[0]
                    ],

                    [
                        sud_ouest[1],
                        sud_ouest[0]
                    ]

                ]]

            })


            polygon_layer = pdk.Layer(

                "PolygonLayer",

                data=polygon_df,

                get_polygon="polygon",

                get_fill_color=[
                    100,
                    100,
                    100,
                    35
                ],

                get_line_color=[
                    50,
                    50,
                    50,
                    200
                ],

                get_line_width=3,

                stroked=True,

                filled=True

            )


            def priority_color(priority):

                if priority == "Très élevée":

                    return [
                        180,
                        0,
                        0,
                        255
                    ]

                elif priority == "Élevée":

                    return [
                        230,
                        70,
                        30,
                        255
                    ]

                elif priority == "Moyenne":

                    return [
                        240,
                        170,
                        0,
                        255
                    ]

                else:

                    return [
                        40,
                        150,
                        70,
                        255
                    ]


            map_df[
                "Couleur"
            ] = map_df[
                "Priorité"
            ].apply(
                priority_color
            )


            points_layer = pdk.Layer(

                "ScatterplotLayer",

                data=map_df,

                get_position=[
                    "Longitude",
                    "Latitude"
                ],

                get_radius=10,

                get_fill_color="Couleur",

                radius_min_pixels=7,

                radius_max_pixels=16,

                pickable=True

            )


            text_layer = pdk.Layer(

                "TextLayer",

                data=map_df,

                get_position=[
                    "Longitude",
                    "Latitude"
                ],

                get_text="Point",

                get_size=16,

                get_color=[
                    0,
                    0,
                    0,
                    255
                ],

                get_text_anchor="middle",

                get_alignment_baseline="bottom",

                pickable=True

            )


            view_state = pdk.ViewState(

                latitude=latitude,

                longitude=longitude,

                zoom=15,

                pitch=0

            )


            deck = pdk.Deck(

                layers=[
                    polygon_layer,
                    points_layer,
                    text_layer
                ],

                initial_view_state=view_state,

                tooltip={

                    "html":
                    "<b>Point :</b> {Point}<br/>"
                    "<b>Latitude :</b> {Latitude}<br/>"
                    "<b>Longitude :</b> {Longitude}<br/>"
                    "<b>Score :</b> {Score de priorité}/100<br/>"
                    "<b>Priorité :</b> {Priorité}<br/>"
                    "<b>Reconnaissance :</b> "
                    "{Reconnaissance recommandée}<br/>"
                    "<b>Profondeur :</b> "
                    "{Profondeur indicative (m)} m<br/>"
                    "<b>Fiabilité :</b> "
                    "{Niveau de fiabilité}<br/>"
                    "<b>Justification :</b> "
                    "{Justification locale}"

                }

            )


            st.pydeck_chart(
                deck,
                use_container_width=True
            )


            st.markdown(
                """
                **Légende de la carte :**

                🔴 **Très élevée** — vigilance renforcée  
                🟠 **Élevée** — point prioritaire  
                🟡 **Moyenne** — attention normale  
                🟢 **Normale** — couverture générale
                """
            )


            # =================================================
            # 49. EXPORT EXCEL
            # =================================================

            st.subheader(
                "📥 49. Export complet des résultats"
            )


            excel_buffer = BytesIO()


            with pd.ExcelWriter(
                excel_buffer,
                engine="openpyxl"
            ) as writer:

                points_df.to_excel(
                    writer,
                    index=False,
                    sheet_name="Implantation"
                )


                synthese.to_excel(
                    writer,
                    index=False,
                    sheet_name="Synthèse"
                )


                facteurs_df = pd.DataFrame({

                    "Facteurs identifiés":
                    facteurs

                })


                facteurs_df.to_excel(
                    writer,
                    index=False,
                    sheet_name="Facteurs"
                )


                risques_df = pd.DataFrame({

                    "Risques identifiés":
                    risques

                })


                risques_df.to_excel(
                    writer,
                    index=False,
                    sheet_name="Risques"
                )


                regles_df = pd.DataFrame({

                    "Règles appliquées":
                    regles_intelligentes

                })


                regles_df.to_excel(
                    writer,
                    index=False,
                    sheet_name="Règles"
                )


                vigilance_df = zones_vigilance[

                    [
                        "Point",
                        "Latitude",
                        "Longitude",
                        "Score de priorité",
                        "Priorité",
                        "Justification locale"
                    ]

                ]


                vigilance_df.to_excel(
                    writer,
                    index=False,
                    sheet_name="Vigilance"
                )


            excel_data = (
                excel_buffer.getvalue()
            )


            st.download_button(

                "📊 Télécharger le dossier Excel complet",

                data=excel_data,

                file_name=(
                    "GeoExpert_resultats_complets.xlsx"
                ),

                mime=(
                    "application/vnd.openxmlformats-"
                    "officedocument.spreadsheetml.sheet"
                ),

                use_container_width=True

            )


            # =================================================
            # 50. CONCLUSION
            # =================================================

            st.subheader(
                "📝 50. Conclusion de l'analyse"
            )


            if niveau == "ÉLEVÉ":

                conclusion = (

                    f"GeoExpert identifie un niveau de "
                    f"complexité géotechnique élevé. "
                    f"{nb_points} points d'implantation "
                    f"ont été proposés avec une hiérarchisation "
                    f"individuelle des priorités. "
                    f"Une reconnaissance renforcée est recommandée."

                )

            elif niveau == "MOYEN":

                conclusion = (

                    f"GeoExpert identifie un niveau de "
                    f"complexité géotechnique moyen. "
                    f"{nb_points} points d'implantation "
                    f"ont été proposés et classés selon leur "
                    f"niveau de priorité."

                )

            else:

                conclusion = (

                    f"GeoExpert identifie un niveau de "
                    f"complexité géotechnique faible. "
                    f"{nb_points} points d'implantation "
                    f"sont proposés pour assurer une "
                    f"couverture générale de l'emprise."

                )


            st.info(
                conclusion
            )


            st.caption(
                "⚠️ Les résultats de GeoExpert sont issus "
                "des règles du prototype. Ils constituent "
                "une aide à la décision et ne remplacent "
                "pas la validation de l'ingénieur "
                "géotechnicien ni les prescriptions "
                "normatives applicables."
            )


# =========================================================
# TAB 2 — METHODOLOGIE
# =========================================================

with tab2:

    st.header(
        "📚 Méthodologie de GeoExpert"
    )


    st.write(
        "GeoExpert repose sur une approche d'aide à la "
        "décision basée sur des règles géotechniques "
        "préétablies."
    )


    st.subheader(
        "1. Données d'entrée"
    )


    st.write(
        """
        Le système utilise notamment :

        • les coordonnées du projet ;  
        • le type d'ouvrage ;  
        • les dimensions principales ;  
        • le nombre d'étages et de sous-sols lorsque nécessaire ;  
        • le contexte géologique ;  
        • la présence potentielle de remblais ;  
        • la présence d'eau ;  
        • la pente du terrain ;  
        • les informations géologiques disponibles ;  
        • l'existence éventuelle d'une étude antérieure.
        """
    )


    st.subheader(
        "2. Évaluation de la complexité"
    )


    st.write(
        "Les informations saisies sont transformées "
        "en un indice de complexité global."
    )


    st.write(
        """
        Le niveau obtenu est classé en trois catégories :

        • FAIBLE  
        • MOYEN  
        • ÉLEVÉ
        """
    )


    st.subheader(
        "3. Détermination du nombre de points"
    )


    st.write(
        "Le nombre de points proposé dépend du type "
        "d'ouvrage, de son emprise, de sa longueur et "
        "du niveau de complexité."
    )


    st.subheader(
        "4. Hiérarchisation individuelle"
    )


    st.write(
        "Chaque point reçoit ensuite un score individuel "
        "compris entre 0 et 100."
    )


    st.write(
        """
        Le score prend notamment en compte :

        • la position du point dans l'emprise ;  
        • la proximité des limites ;  
        • la complexité globale ;  
        • le contexte géologique ;  
        • les remblais ;  
        • l'eau ;  
        • la pente ;  
        • le type d'ouvrage.
        """
    )


    st.subheader(
        "5. Décision"
    )


    st.write(
        """
        Le système transforme ensuite les résultats en :

        • type de reconnaissance recommandé ;  
        • profondeur indicative ;  
        • priorité individuelle ;  
        • justification locale ;  
        • zones de vigilance ;  
        • synthèse décisionnelle.
        """
    )


    st.subheader(
        "6. Cartographie"
    )


    st.write(
        "Une représentation cartographique permet de "
        "visualiser la position des points proposés et "
        "leur niveau de priorité."
    )


    st.subheader(
        "7. Export"
    )


    st.write(
        "Les résultats peuvent être exportés dans un "
        "fichier Excel structuré comprenant les résultats "
        "d'implantation, la synthèse, les facteurs, les "
        "risques, les règles et les zones de vigilance."
    )


# =========================================================
# TAB 3 — LIMITES
# =========================================================

with tab3:

    st.header(
        "⚠️ Limites du système"
    )


    st.warning(
        "GeoExpert est un prototype d'aide à la décision "
        "et ne constitue pas un logiciel de dimensionnement "
        "géotechnique."
    )


    st.subheader(
        "Limites principales"
    )


    st.write(
        """
        • Les profondeurs proposées sont indicatives.

        • Les nombres de sondages constituent des propositions
          préliminaires.

        • Les positions générées ne remplacent pas une
          implantation réalisée à partir d'un plan topographique
          précis.

        • Le contexte géologique doit être confirmé par les
          données disponibles sur le site.

        • Les règles utilisées doivent être confrontées aux
          pratiques et prescriptions applicables au projet.

        • Le système ne remplace pas l'interprétation d'un
          ingénieur géotechnicien.

        • Les résultats doivent être vérifiés avant toute
          utilisation opérationnelle.
        """
    )


    st.subheader(
        "Rôle de GeoExpert"
    )


    st.info(
        "L'objectif de GeoExpert est d'aider l'ingénieur "
        "à organiser, comparer et hiérarchiser les "
        "reconnaissances géotechniques à partir des "
        "informations disponibles."
    )


    st.success(
        "GeoExpert = aide à la décision + structuration "
        "des données + hiérarchisation des reconnaissances."
    )