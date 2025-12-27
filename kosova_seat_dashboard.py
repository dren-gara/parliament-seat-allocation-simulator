import streamlit as st
import altair as alt
import pandas as pd

def dhondt_method(votes_dict, total_seats=100, threshold=0.05):
    total_votes = sum(votes_dict.values())
    if total_votes == 0:
        return {}
    threshold_votes = total_votes * threshold
    eligible_parties = {party: votes for party, votes in votes_dict.items()
                        if votes >= threshold_votes or threshold == 0}
    
    if not eligible_parties:
        return {}

    seats_allocated = {party: 0 for party in eligible_parties}
    for _ in range(total_seats):
        quotients = {party: votes / (seats_allocated[party] + 1)
                     for party, votes in eligible_parties.items()}
        winning_party = max(quotients, key=quotients.get)
        seats_allocated[winning_party] += 1

    return seats_allocated

KOSOVO_PARTIES = [
    {"name": "Vetëvendosje! (LVV)", "color": "#E30613"},
    {"name": "Partia Demokratike e Kosovës (PDK)", "color": "#3D76F0"},
    {"name": "Lidhja Demokratike e Kosovës (LDK)", "color": "#00008B"},
    {"name": "Aleanca për Ardhmërinë e Kosovës (AAK)", "color": "#FFD700"},
    {"name": "Nisma Socialdemokrate (NISMA)", "color": "#EE7D0C"},
    {"name": "Lista Serbe (Srpska Lista)", "color": "#000000"},
]

RESERVED_SEATS = {
    "Lista Serbe (Srpska Lista)": 10,
    "Other Minorities": 10,
}

def initialize_session_state():
    if 'general_parties' not in st.session_state:
        st.session_state.general_parties = [
            {**p, "percent": 10.0, "votes": 100000} for p in KOSOVO_PARTIES
        ]
        st.session_state.num_general_parties = len(KOSOVO_PARTIES)
    if 'num_general_parties' not in st.session_state:
        st.session_state.num_general_parties = len(st.session_state.general_parties)
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False
    if 'input_mode_percent' not in st.session_state:
        st.session_state.input_mode_percent = True
    if 'total_assumed_votes' not in st.session_state:
        st.session_state.total_assumed_votes = 900_000
    if 'language' not in st.session_state:
        st.session_state.language = "English"

def translate(key):
    translations = {
        "English": {
            "title": "Kosovo Parliament Seat Allocation Simulator",
            "desc": "Simulate full 120-seat parliament (100 general + 20 reserved minority seats) using D'Hondt method.",
            "system_info": "Kosovo Electoral System Explanation",
            "system_text": """
Kosovo's Assembly has **120 seats**:

- **100 general seats** allocated using D'Hondt (5% threshold for all).
- **20 reserved seats** (guaranteed): 10 for Serb community, 10 for others.

In this simulator, Lista Serbe gets **10 reserved** for simplicity.
A majority needs **61 seats**.
            """,
            "coalition_builder": "Coalition Builder",
            "majority": "Total seats in coalition:",
            "needs": "Needs 61 for majority",
            "has_majority": "Has majority!",
        },
        "Shqip": {
            "title": "Simulues i Ndarjes së Ulëseve në Kuvendin e Kosovës",
            "desc": "Simuloni parlamentin me 120 ulëse (100 të përgjithshme + 20 të rezervuara) duke përdorur metodën D'Hondt.",
            "system_info": "Shpjegim i Sistemit Zgjedhor",
            "system_text": """
Kuvendi ka **120 ulëse**:

- **100 ulëse të përgjithshme** me D'Hondt (prag 5%).
- **20 ulëse të rezervuara**: 10 për serbët, 10 për të tjerët.

Në këtë simulues, Lista Serbe merr **10 fikse të rezervuara** për thjeshtësi.
Shumica kërkon **61 ulëse**.
            """,
            "coalition_builder": "Ndërtues Koalicioni",
            "majority": "Total ulëse në koalicion:",
            "needs": "Nevojiten 61 për shumicë",
            "has_majority": "Ka shumicë!",
        }
    }
    return translations[st.session_state.language].get(key, key)

def main():
    st.set_page_config(page_title="Kosovo Election Simulator", layout="wide")
    
    initialize_session_state()

    st.sidebar.selectbox("Gjuha / Language", ["English", "Shqip"], 
                         index=0 if st.session_state.language == "English" else 1,
                         key="lang_select")
    st.session_state.language = st.session_state.lang_select

    col1, col2 = st.columns([4, 1])
    with col1:
        st.title(translate("title"))
    with col2:
        st.image("logo.png", width=120)

    st.markdown(translate("desc"))

    with st.expander(translate("system_info")):
        st.markdown(translate("system_text"))

    st.sidebar.header("Input Settings")
    
    st.session_state.input_mode_percent = st.sidebar.checkbox(
        "Input as Vote Percentages (%)", value=True
    )

    if st.session_state.input_mode_percent:
        st.session_state.total_assumed_votes = st.sidebar.number_input(
            "Total Assumed Votes", min_value=100_000, max_value=2_000_000, step=50_000,
            value=st.session_state.total_assumed_votes
        )

    apply_threshold = st.sidebar.checkbox("Apply 5% threshold", value=True)
    threshold = 0.05 if apply_threshold else 0.0

    st.sidebar.subheader("Parties (100 General Seats)")
    st.session_state.num_general_parties = st.sidebar.number_input(
        "Number of parties", min_value=1, max_value=20, value=st.session_state.num_general_parties
    )

    while len(st.session_state.general_parties) < st.session_state.num_general_parties:
        st.session_state.general_parties.append({"name": "Other Party", "percent": 2.0, "color": "#808080"})
    while len(st.session_state.general_parties) > st.session_state.num_general_parties:
        st.session_state.general_parties.pop()

    with st.sidebar.form("party_form"):
        total_percent = 0.0
        options = [p["name"] for p in KOSOVO_PARTIES] + ["Custom Party Name"]
        for i, party in enumerate(st.session_state.general_parties):
            cols = st.columns([2, 2, 1])
            with cols[0]:
                current_idx = options.index(party["name"]) if party["name"] in options else 0
                selected = st.selectbox(f"Party {i+1}", options, index=current_idx, key=f"sel_{i}")
                if selected == "Custom Party Name":
                    party["name"] = st.text_input("Custom Name", value=party.get("name", "Custom"), key=f"cust_{i}")
                else:
                    party["name"] = selected
                    party["color"] = next(p["color"] for p in KOSOVO_PARTIES if p["name"] == selected)
            with cols[1]:
                if st.session_state.input_mode_percent:
                    default_percent = party.get("percent", 5.0)
                    party["percent"] = st.number_input(f"% {party['name']}", 0.0, 100.0, step=0.1, value=default_percent, key=f"perc_{i}")
                    total_percent += party["percent"]
                else:
                    party["votes"] = st.number_input(f"Votes {party['name']}", min_value=0, step=1000, value=party.get("votes", 100000), key=f"vote_{i}")
            with cols[2]:
                party["color"] = st.color_picker("Color", value=party.get("color", "#808080"), key=f"col_{i}")

        if st.session_state.input_mode_percent:
            st.caption(f"Total: {total_percent:.2f}%")
            if abs(total_percent - 100) > 0.1:
                st.warning("Will be normalized proportionally.")

        if st.form_submit_button("Calculate Seats"):
            st.session_state.submitted = True

    if st.session_state.submitted:
        total_percent_calc = sum(p.get("percent", 0) for p in st.session_state.general_parties)
        if st.session_state.input_mode_percent and total_percent_calc == 0:
            st.error("No votes entered.")
            st.stop()

        if st.session_state.input_mode_percent:
            scale = st.session_state.total_assumed_votes / total_percent_calc if total_percent_calc > 0 else 0
            votes_dict = {p["name"]: p["percent"] * scale for p in st.session_state.general_parties}
        else:
            votes_dict = {p["name"]: p["votes"] for p in st.session_state.general_parties}

        # Exclude Lista Serbe from general allocation
        lista_votes = votes_dict.pop("Lista Serbe (Srpska Lista)", 0)

        general_seats = dhondt_method(votes_dict, total_seats=100, threshold=threshold)

        total_seats_dict = {party: general_seats.get(party, 0) for party in votes_dict}
        total_seats_dict["Lista Serbe (Srpska Lista)"] = 10
        total_seats_dict["Other Minorities"] = total_seats_dict.get("Other Minorities", 0) + 10

        total_votes = sum(votes_dict.values()) + lista_votes
        wasted_votes = int(sum(v for p, v in votes_dict.items() if p not in general_seats))
        effective_threshold = (wasted_votes / total_votes * 100) if total_votes > 0 else 0

        st.subheader("Results (Full 120 Seats)")

        table_data = []
        chart_data_bar = []

        # General seat winners
        for party, g_seats in general_seats.items():
            votes = votes_dict.get(party, 0)
            perc = (votes / total_votes * 100) if total_votes > 0 else 0
            t_seats = total_seats_dict.get(party, g_seats)
            color = next((p["color"] for p in st.session_state.general_parties if p["name"] == party), "#808080")
            table_data.append({
                "Party": party,
                "Vote %": f"{perc:.2f}%",
                "Votes": f"{int(votes):,}",
                "General Seats": g_seats,
                "Reserved": 0,
                "Total Seats": t_seats,
            })
            chart_data_bar.append({"Party": party, "Seats": t_seats, "Color": color})

        # Lista Serbe (fixed 10 seats)
        lista_perc = (lista_votes / total_votes * 100) if total_votes > 0 else 0
        table_data.append({
            "Party": "Lista Serbe (Srpska Lista)",
            "Vote %": f"{lista_perc:.2f}%",
            "Votes": f"{int(lista_votes):,}",
            "General Seats": 0,
            "Reserved": 10,
            "Total Seats": 10,
        })
        chart_data_bar.append({"Party": "Lista Serbe (Srpska Lista)", "Seats": 10, "Color": "#002395"})

        # Other Minorities (fixed 10 seats)
        table_data.append({
            "Party": "Other Minorities",
            "Vote %": "-",
            "Votes": "-",
            "General Seats": 0,
            "Reserved": 10,
            "Total Seats": 10,
        })
        chart_data_bar.append({"Party": "Other Minorities", "Seats": 10, "Color": "#696969"})  # Dim gray

        df_table = pd.DataFrame(table_data).sort_values("Total Seats", ascending=False)
        st.dataframe(df_table, use_container_width=True)

        st.info(f"**Wasted votes** (below threshold): {wasted_votes:,} ({effective_threshold:.2f}%)")
        st.info(f"Calculated turnout: {int(total_votes):,} votes")

        # Single full-width bar chart including minorities
        st.write("**Total Seats in Parliament (120 seats)**")
        df_bar = pd.DataFrame(chart_data_bar).sort_values("Seats", ascending=False)
        bar = alt.Chart(df_bar).mark_bar().encode(
            x=alt.X("Party:N", sort=None),
            y=alt.Y("Seats:Q", title="Seats"),
            color=alt.Color("Party:N", scale=alt.Scale(domain=df_bar["Party"].tolist(), range=df_bar["Color"].tolist()), legend=None),
            tooltip=["Party", "Seats"]
        ).properties(height=500, width=800)
        st.altair_chart(bar, use_container_width=True)

        st.subheader(translate("coalition_builder"))
        coalition_parties = st.multiselect("Select parties for coalition", options=[row["Party"] for row in table_data])
        if coalition_parties:
            coalition_seats = sum(total_seats_dict.get(p, 0) for p in coalition_parties)
            st.write(f"**{translate('majority')} {coalition_seats}**")
            if coalition_seats >= 61:
                st.success(translate("has_majority"))
            else:
                st.warning(f"{translate('needs')} ({61 - coalition_seats} more)")

    st.sidebar.markdown("### Instructions / Udhëzime")
    st.sidebar.markdown("1. Enter party names, percentages (or votes), and colors.\n2. Click **Calculate Seats** to see results.\n3. Lista Serbe gets 0 general + 10 reserved seats.")

if __name__ == "__main__":
    main()