import fastf1
import numpy as np
import pandas as pd
session = fastf1.get_session(2025, "Japan", "Race")
session.load()
laps = session.laps
profile_A = clean_data(laps,"VER")
profile_B = clean_data(laps,"NOR")
driver_a = "VER"
driver_b = "NOR"
best_pit(16, 22, 25)
