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

def initialize_session_state():
    """Initialize session state variables if not already set."""
    if 'general_parties' not in st.session_state:
        st.session_state.general_parties = [
            {"name": f"Party {chr(65+i)}", "votes": 10000 * (i + 1), "color": "#FF4B4B"} 
            for i in range(3)
        ]
    if 'num_general_parties' not in st.session_state:
        st.session_state.num_general_parties = 3
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False

def main():
    # Create two columns for title and logo
    col1, col2 = st.columns([4, 1])  # Adjust ratio as needed (3:1 means title takes more space)
    with col1:
        st.title("Kosova Parliament Seat Allocation Simulator")
    with col2:
        st.image("logo.png", width=120)  # Adjust width for size

    st.markdown("Simulate seat distribution for 100 general seats using the D'Hondt method.")

    # Initialize session state
    initialize_session_state()

    # Sidebar for input
    st.sidebar.header("Input Party Data")
    st.sidebar.subheader("General Parties (100 Seats)")
    st.session_state.num_general_parties = st.sidebar.number_input(
        "Number of parties", min_value=1, max_value=20, 
        value=st.session_state.num_general_parties, step=1
    )

    # Adjust general parties list based on number
    while len(st.session_state.general_parties) < st.session_state.num_general_parties:
        st.session_state.general_parties.append({
            "name": f"Party {chr(65 + len(st.session_state.general_parties))}", 
            "votes": 10000 * (len(st.session_state.general_parties) + 1),
            "color": "#FF4B4B"
        })
    while len(st.session_state.general_parties) > st.session_state.num_general_parties:
        st.session_state.general_parties.pop()

    with st.sidebar.form(key="general_party_form"):
        for i, party in enumerate(st.session_state.general_parties):
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                party["name"] = st.text_input(
                    f"Party {i+1} Name", value=party["name"], key=f"gen_party_{i}_name"
                )
            with col2:
                party["votes"] = st.number_input(
                    f"Votes for {party['name']}", min_value=0, value=party["votes"], 
                    step=1000, key=f"gen_party_{i}_votes"
                )
            with col3:
                if "color" not in party:
                    party["color"] = "#FF4B4B"
                party["color"] = st.color_picker(
                    "Color", value=party["color"], key=f"gen_party_{i}_color"
                )
        submit_general = st.form_submit_button(label="Calculate Seats")
        if submit_general:
            st.session_state.submitted = True

    # Main area for results
    st.subheader("Results")

    # Threshold checkbox
    apply_threshold = st.checkbox("Apply 5% threshold", value=False)
    threshold = 0.05 if apply_threshold else 0.0

    # Calculate and display results if submitted
    if st.session_state.submitted:
        general_votes_dict = {party["name"]: party["votes"] for party in st.session_state.general_parties}
        general_result = dhondt_method(general_votes_dict, total_seats=100, threshold=threshold)

        if isinstance(general_result, str):
            st.warning(general_result)
        else:
            st.write("### Seat Allocation (100 Seats)")
            total_votes = sum(general_votes_dict.values())
            table_data = []
            chart_data = []
            for party, seats in general_result.items():
                votes = general_votes_dict.get(party, 0)
                vote_percent = (votes / total_votes) * 100 if total_votes > 0 else 0
                color = next(p["color"] for p in st.session_state.general_parties if p["name"] == party)
                table_data.append({
                    "Party": party, 
                    "Votes": f"{votes:,}", 
                    "Vote %": f"{vote_percent:.2f}%", 
                    "Seats": seats
                })
                chart_data.append({
                    "Party": party, 
                    "Votes": f"{votes:,}", 
                    "Vote %": f"{vote_percent:.2f}%", 
                    "Seats": seats,
                    "Color": color
                })
            st.table(table_data)

            # Sort by seats and create Altair bar chart
            df = pd.DataFrame(chart_data).sort_values(by="Seats", ascending=False)
            chart = alt.Chart(df).mark_bar().encode(
                x=alt.X("Party", sort=None),
                y="Seats",
                color=alt.Color("Party", scale=alt.Scale(domain=df["Party"].tolist(), range=df["Color"].tolist()), legend=None),
                tooltip=["Party", "Seats", "Votes", "Vote %"]
            ).properties(width=600, height=400)
            st.altair_chart(chart, use_container_width=True)
            st.write(f"**Total seats allocated:** {sum(general_result.values())}")

    # Instructions
    st.sidebar.markdown("""
    ### Instructions
    1. Enter party names, vote totals, and choose bar colors for the 100 D'Hondt seats.
    2. Submit the form to see results.
    3. Toggle the 5% threshold to filter parties (updates automatically after submission).
    """)

if __name__ == "__main__":
    main()