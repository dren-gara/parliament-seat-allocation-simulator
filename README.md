# Kosovo Parliament Seat Allocation Simulator

This is a Streamlit-based web application that simulates the allocation of seats in the Kosovo Parliament using the D'Hondt method. It models the 120-seat parliament, including 100 general seats (allocated proportionally with a 5% threshold) and 20 reserved seats for minorities (10 for the Serb community via Lista Serbe and 10 for other minorities).

The simulator allows users to input party names, vote percentages or absolute votes, and colors for visualization. It excludes Lista Serbe from general seat allocation, assigning them a fixed 10 reserved seats. Results include a table, bar chart for total seats, wasted votes calculation, and a coalition builder to check for a 61-seat majority.

The app supports bilingual interface (English and Albanian).

## Features

- **D'Hondt Method Simulation**: Allocates 100 general seats based on votes, with optional 5% threshold.
- **Reserved Seats**: Fixed 10 for Lista Serbe (Srpska Lista) and 10 for other minorities.
- **Input Modes**: Enter votes as percentages (normalized to total turnout) or absolute numbers.
- **Visualization**: Bar chart showing total seats (including minorities).
- **Coalition Builder**: Select parties to calculate if they reach a 61-seat majority.
- **Bilingual Support**: Toggle between English and Albanian.
- **Wasted Votes**: Calculates votes below the threshold and effective percentage.
- **Customizable**: Add up to 20 parties, choose names and colors from presets or custom.

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd <repository-folder>
   ```

2. Install dependencies:
   ```
   pip install streamlit altair pandas
   ```

3. Ensure you have a `logo.png` file in the project root for the app header (or replace the image path in code).

## Usage

Run the app locally:
```
streamlit run kosova_seat_dashboard.py
```

- Open in browser (default: http://localhost:8501).
- In the sidebar:
  - Toggle language (English/Shqip).
  - Choose input mode (percentages or votes).
  - Set number of parties.
  - Enter party details (name, votes/%, color).
  - Toggle 5% threshold.
- Submit to calculate and view results.
- Use the coalition builder to test majorities.

## Dependencies

- Python 3.8+
- Streamlit
- Altair
- Pandas

## License

MIT License. Feel free to use, modify, and distribute.