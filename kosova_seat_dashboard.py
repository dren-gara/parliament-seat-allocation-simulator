import streamlit as st
import altair as alt
import pandas as pd

def dhondt_method(votes_dict, total_seats=100, threshold=0.05):
    """Simulates seat allocation using the D'Hondt method for general seats."""
    total_votes = sum(votes_dict.values())
    threshold_votes = total_votes * threshold
    eligible_parties = {party: votes for party, votes in votes_dict.items()
                        if votes >= threshold_votes or threshold == 0}
    
    if not eligible_parties:
        return "No parties passed the threshold!"

    seats_allocated = {party: 0 for party in eligible_parties}
    for _ in range(total_seats):
        quotients = {party: votes / (seats_allocated[party] + 1)
                     for party, votes in eligible_parties.items()}
        winning_party = max(quotients, key=quotients.get)
        seats_allocated[winning_party] += 1

    return seats_allocated

KOSOVO_PARTIES = [
    {"name": "Vetëvendosje! (LVV)", "color": "#E30613"},      # Red
    {"name": "Partia Demokratike e Kosovës (PDK)", "color": "#3D76F0"},  # Blue
    {"name": "Lidhja Demokratike e Kosovës (LDK)", "color": "#00008B"},  # Dark Blue
    {"name": "Aleanca për Ardhmërinë e Kosovës (AAK)", "color": "#FFD700"},  # Gold
    {"name": "Nisma Socialdemokrate (NISMA)", "color": "#EE7D0C"},
]

def initialize_session_state():
    """Initialize session state variables if not already set."""
    if 'general_parties' not in st.session_state:
        # Default to top 5 Kosovo parties (Albanian-majority focus)
        st.session_state.general_parties = [
            {**party, "votes": 100000, "percent": 10.0} for party in KOSOVO_PARTIES
        ]
        st.session_state.num_general_parties = 5
    if 'num_general_parties' not in st.session_state:
        st.session_state.num_general_parties = len(st.session_state.general_parties)
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False
    if 'input_mode_percent' not in st.session_state:
        st.session_state.input_mode_percent = True  # Default to percentages
    if 'total_assumed_votes' not in st.session_state:
        st.session_state.total_assumed_votes = 1_000_000

def main():
    # Title and logo
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("Kosova Parliament Seat Allocation Simulator")
    with col2:
        st.image("logo.png", width=120)

    st.markdown("Simulate seat distribution for 100 general seats using the D'Hondt method.")

    # Initialize session state
    initialize_session_state()

    # Sidebar for input
    st.sidebar.header("Input Settings")
    
    # Toggle for percentage input
    st.session_state.input_mode_percent = st.sidebar.checkbox(
        "Input as Vote Percentages (%)",
        value=st.session_state.input_mode_percent,
        help="Enter vote shares in %. Recommended for simulating polls."
    )

    # Editable total assumed votes (only in % mode)
    if st.session_state.input_mode_percent:
        st.session_state.total_assumed_votes = st.sidebar.number_input(
            "Total Assumed Votes (for % → votes conversion)",
            min_value=100_000, max_value=10_000_000, step=50_000,
            value=st.session_state.total_assumed_votes,
            help="Base total votes used to convert percentages. Adjust to real turnout (~800k–1M typical)."
        )

    st.sidebar.subheader("General Parties (100 Seats)")
    st.session_state.num_general_parties = st.sidebar.number_input(
        "Number of parties", min_value=1, max_value=20,
        value=st.session_state.num_general_parties, step=1
    )

    # Adjust party list length
    while len(st.session_state.general_parties) < st.session_state.num_general_parties:
        new_party = {
            "name": f"Other Party {len(st.session_state.general_parties) - 4}",
            "color": "#808080",
            "votes": 50000 if not st.session_state.input_mode_percent else 0,
            "percent": 5.0
        }
        st.session_state.general_parties.append(new_party)

    while len(st.session_state.general_parties) > st.session_state.num_general_parties:
        st.session_state.general_parties.pop()

    with st.sidebar.form(key="general_party_form"):
        total_percent = 0.0
        for i, party in enumerate(st.session_state.general_parties):
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                options = [p["name"] for p in KOSOVO_PARTIES] + ["Custom Party Name"]
                selected = st.selectbox(
                    f"Party {i+1}",
                    options=options,
                    index=options.index(party["name"]) if party["name"] in options else len(options)-1,
                    key=f"gen_party_{i}_select"
                )
                if selected == "Custom Party Name":
                    party["name"] = st.text_input("Custom Name", value=party["name"], key=f"gen_party_{i}_custom_name")
                else:
                    party["name"] = selected
                    party["color"] = next(p["color"] for p in KOSOVO_PARTIES if p["name"] == selected)

            with col2:
                if st.session_state.input_mode_percent:
                    party["percent"] = st.number_input(
                        f"Vote % for {party['name']}",
                        min_value=0.0, max_value=100.0, step=0.1,
                        value=float(party.get("percent", 5.0)),
                        key=f"gen_party_{i}_percent"
                    )
                    total_percent += party["percent"]
                else:
                    party["votes"] = st.number_input(
                        f"Votes for {party['name']}", min_value=0,
                        value=int(party.get("votes", 100000)),
                        step=1000, key=f"gen_party_{i}_votes"
                    )

            with col3:
                party["color"] = st.color_picker(
                    "Color", value=party.get("color", "#FF4B4B"), key=f"gen_party_{i}_color"
                )

        if st.session_state.input_mode_percent:
            st.caption(f"Current total: {total_percent:.2f}%")
            if abs(total_percent - 100.0) > 0.1:
                st.warning("Percentages do not add up to 100%. They will be normalized proportionally.")

        submit_general = st.form_submit_button(label="Calculate Seats")
        if submit_general:
            st.session_state.submitted = True

    # Results
    st.subheader("Results")

    apply_threshold = st.checkbox("Apply 5% threshold", value=True)
    threshold = 0.05 if apply_threshold else 0.0

    if st.session_state.submitted:
        total_percent = sum(p.get("percent", 0) for p in st.session_state.general_parties)

        if st.session_state.input_mode_percent:
            if total_percent == 0:
                st.error("Total percentage is 0%. Cannot allocate seats.")
                st.stop()

            scale_factor = st.session_state.total_assumed_votes / total_percent
            general_votes_dict = {
                party["name"]: party["percent"] * scale_factor
                for party in st.session_state.general_parties
            }
        else:
            general_votes_dict = {party["name"]: party["votes"] for party in st.session_state.general_parties}

        general_result = dhondt_method(general_votes_dict, total_seats=100, threshold=threshold)

        if isinstance(general_result, str):
            st.warning(general_result)
        else:
            st.write("### Seat Allocation (100 General Seats)")
            total_votes = sum(general_votes_dict.values())
            table_data = []
            chart_data = []
            for party, seats in general_result.items():
                votes = general_votes_dict.get(party, 0)
                vote_percent = (votes / total_votes) * 100 if total_votes > 0 else 0
                color = next(p["color"] for p in st.session_state.general_parties if p["name"] == party)
                table_data.append({
                    "Party": party,
                    "Votes": f"{int(votes):,}",
                    "Vote %": f"{vote_percent:.2f}%",
                    "Seats": seats
                })
                chart_data.append({
                    "Party": party,
                    "Seats": seats,
                    "Color": color,
                    "Votes": f"{int(votes):,}",
                    "Vote %": f"{vote_percent:.2f}%"
                })

            df_table = pd.DataFrame(table_data).sort_values(by="Seats", ascending=False)
            st.dataframe(df_table, use_container_width=True)

            df_chart = pd.DataFrame(chart_data).sort_values(by="Seats", ascending=False)
            chart = alt.Chart(df_chart).mark_bar().encode(
                x=alt.X("Party:N", sort=None),
                y="Seats:Q",
                color=alt.Color("Party:N", scale=alt.Scale(domain=df_chart["Party"].tolist(), range=df_chart["Color"].tolist()), legend=None),
                tooltip=["Party", "Seats", "Votes", "Vote %"]
            ).properties(width=600, height=400)
            st.altair_chart(chart, use_container_width=True)

            st.write(f"**Total seats allocated:** {sum(general_result.values())} out of 100")
            st.info(f"Calculated total turnout: ~{int(total_votes):,} votes")

    # Instructions
    st.sidebar.markdown("""
    ### Instructions
    1. Select parties from dropdown (top 5 major Kosovo parties, now including NISMA).
    2. Enter percentages (default) or votes.
    3. Adjust **Total Assumed Votes** for realistic turnout.
    4. Calculate → see D'Hondt results (5% threshold on by default).
    """)

if __name__ == "__main__":
    main()