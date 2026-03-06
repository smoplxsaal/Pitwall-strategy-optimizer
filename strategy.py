def clean_data(laps, driver):
    raw_driver_data = laps[laps['Driver'] == driver].copy()
    raw_driver_data['LapTimeSeconds'] = raw_driver_data['LapTime'].dt.total_seconds()
    driver_data = raw_driver_data[
        raw_driver_data['PitInTime'].isna() &
        raw_driver_data['PitOutTime'].isna()
    ].copy()
    driver_data = driver_data.pick_quicklaps().pick_accurate()
    Fuel = driver_data[driver_data['Compound'] == 'HARD']
    if len(Fuel) < 5:
        return {"error": "Not enough HARD data for fuel estimation"}
    Fuel_burn, _ = np.polyfit(Fuel['TyreLife'], Fuel['LapTimeSeconds'], 1)
    deg_results = {}
    compounds = driver_data['Compound'].unique()
    for comp in compounds:
        comp_data = driver_data[driver_data['Compound'] == comp]
        if len(comp_data) < 5:
            continue
        slope, _ = np.polyfit(comp_data['TyreLife'],
                              comp_data['LapTimeSeconds'], 1)
        deg_results[comp] = slope - Fuel_burn
    formatted_deg = {comp: f"{val:.3f}" for comp, val in deg_results.items()}
    if raw_driver_data['PitInTime'].notna().sum() == 0:
        return {"error": "No pit stop found"}
    pit_lap = raw_driver_data[raw_driver_data['PitInTime'].notna()].index[0]
    old_lap = raw_driver_data.loc[pit_lap - 1, 'LapTimeSeconds']
    new_lap = raw_driver_data.loc[pit_lap + 2, 'LapTimeSeconds']
    Fresh_Tyre_delta = old_lap - new_lap
    inlap = raw_driver_data.loc[pit_lap, 'LapTimeSeconds']
    InLap_penalty = inlap - old_lap
    return {
        "fuel_burn": Fuel_burn,
        "degradation": deg_results,
        "fresh_delta": Fresh_Tyre_delta,
        "inlap_penalty": InLap_penalty
            }

def predict_gap(driver_a, driver_b, L, N):
    lap_A = laps[laps['Driver'] == driver_a].copy()
    lap_B = laps[laps['Driver'] == driver_b].copy()
    lap_A['LapTimeSec'] = lap_A['LapTime'].dt.total_seconds()
    lap_B['LapTimeSec'] = lap_B['LapTime'].dt.total_seconds()
    delta_A = lap_A[lap_A['LapNumber'] <= L]['LapTimeSec'].sum()
    delta_B = lap_B[lap_B['LapNumber'] <= L]['LapTimeSec'].sum()
    gap = delta_B - delta_A
    lap_time_A = lap_A[lap_A['LapNumber'] == L]['LapTimeSec'].values[0]
    lap_time_B = lap_B[lap_B['LapNumber'] == L]['LapTimeSec'].values[0]
    fuel_A = profile_A["fuel_burn"]
    fuel_B = profile_B["fuel_burn"]
    deg_A = list(profile_A["degradation"].values())[0]
    deg_B = list(profile_B["degradation"].values())[0]
    possible_gaps = []
    for i in range(N):
        lap_time_A = lap_time_A - fuel_A + deg_A
        lap_time_B = lap_time_B - fuel_B + deg_B
        gap = gap + (lap_time_B - lap_time_A)
        possible_gaps.append(gap)
    return possible_gaps


def best_pit(start_lap, end_lap, predict_till):
    result = {}
    for pit_lap in range(start_lap, end_lap + 1):
        N = predict_till - pit_lap
        gap_built = predict_gap(driver_a, driver_b, pit_lap, N)
        final_gap = gap_built[-1]
        result[pit_lap] = round(float(final_gap), 1)
    best_lap = min(result, key=result.get)
    print(f"Best lap: {best_lap}")
    print(f"Expected Gain: {abs(result[best_lap]):.3f}")
    return result
