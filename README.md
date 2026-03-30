 Race Strategy Simulation Model
This project simulates Formula 1 race strategies using driver lap data, tyre degradation, and fuel correction.

📊 Overview
The model takes real lap data of a driver and generates optimal pit stop strategies by simulating race progression under different tyre compounds.

It compares multiple strategies and identifies the fastest approach based on total race time.

⚙️ Features
Fuel-corrected lap time calculation

Tyre degradation estimation using linear regression

Strategy simulation (M-H, H-M, S-M-S, S-M-H)

Lap-by-lap race time modeling

Strategy comparison based on cumulative race time

📥 Input Data
The model requires:

Driver lap times

Lap number

Tyre compound (Soft / Medium / Hard)

Tyre life

Pit stop data

📤 Output
Optimal race strategy

Estimated total race time

Pit stop timing

Tyre degradation values per compound

🧠 Methodology
Clean and filter lap data

Apply fuel correction to normalize lap times

Estimate tyre degradation using regression (numpy.polyfit)

Simulate lap-by-lap race for different strategies

Compare total race time across strategies

⚠️ Limitations
Linear tyre degradation assumption

Fixed pit stop time (~22 seconds)

No traffic, DRS, or safety car modeling

Simplified fuel consumption model

🔮 Future Improvements
Integration with real F1 data using FastF1

Non-linear tyre degradation modeling

Traffic and race condition simulation

Strategy optimization using algorithms

🛠️ Tech Stack
Python

Pandas

NumPy

📌 Note
This is a simplified simulation model built to understand the impact of tyre degradation and fuel load on race strategy.

🤝 Feedback
Open to feedback, suggestions, and improvements.

🔗 Example Use Case
Provide lap data of a driver → model processes the data → outputs the fastest strategy and race time estimate.
