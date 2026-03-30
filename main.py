def cleaned_data(laps,driver):
    raw_driver_data=laps[laps['Driver']==driver]
    # Check if driver even exists in data
    if raw_driver_data.empty:
        return "driver data not enough"
        
    raw_driver_data['LapTime in sec']=raw_driver_data['LapTime'].dt.total_seconds()
    driver_data=raw_driver_data.copy()
    driver_data=driver_data[driver_data['LapNumber']>=2].reset_index()
    driver_data=driver_data[driver_data['PitInTime'].isna() & driver_data['PitOutTime'].isna()]
    
    if driver_data.empty:
        return "driver data not enough"

    total_lap=raw_driver_data['LapNumber'].max()
    starting_fuel=110
    fuel_burn=starting_fuel/total_lap
    fuel_burn=fuel_burn*0.05
    driver_data['LapTime in sec']=driver_data['LapTime'].dt.total_seconds()
    driver_data['Fuel Corrected Time'] = driver_data['LapTime in sec'] - ((starting_fuel - (driver_data['LapNumber'] * fuel_burn)) * 0.05)
    driver_data['Cummulative']=driver_data['Fuel Corrected Time'].diff()
    average_fuel_burn=driver_data['Cummulative'].mean()
    driver_data['True Fuel Pace']=driver_data['LapTime in sec']+((starting_fuel - (driver_data['LapNumber'] * fuel_burn)) * average_fuel_burn)
    cleaned_data=driver_data[['Driver','LapNumber','LapTime in sec','Stint','TyreLife','Compound','Fuel Corrected Time','True Fuel Pace']]
    
    deg_result={}
    compound=cleaned_data['Compound'].unique()
    
    # Requirement: Must have more than one compound to run a strategy
    if len(compound) < 2:
        return "driver data not enough"

    for comp in compound:
        comp_data=cleaned_data[cleaned_data['Compound']==comp]
        if len(comp_data) < 5:
            deg_result[comp]={
                'Degradation':"Not enough data",
                'Average Pace':"Not enough data"
            }
        else:
            deg,base_pace=np.polyfit(comp_data['TyreLife'],comp_data['True Fuel Pace'],1)
            deg_result[comp]={
                'Degradation':float(deg),
                'Average Pace':float(base_pace)
            }
            
    new_tyre={}
    for comp in compound:
        comp_data=cleaned_data[cleaned_data['Compound']==comp].reset_index()
        if len(comp_data) > 2:
            new_lap=comp_data.loc[1,'True Fuel Pace']
            next_lap=comp_data.loc[2,'True Fuel Pace']
            new_tyre_adv=f"{next_lap-new_lap}"
            new_tyre[comp]=new_tyre_adv
            
    strategy={}

    if 'MEDIUM' in compound and 'HARD' in compound and 'SOFT' not in compound:
        medium_mh=int(total_lap*(40/100))
        hard_mh=int(total_lap-medium_mh)
        fb=fuel_burn
        totaltime_mh=0
        time_mh=[]
        med_p=float(deg_result['MEDIUM']['Average Pace'])
        med_d=float(deg_result['MEDIUM']['Degradation'])
        hard_d=float(deg_result['HARD']['Degradation'])
        hard_p=float(deg_result['HARD']['Average Pace'])
        for i in range(1,medium_mh+1):
            laptime=med_p+(med_d*i)-(fb*i)
            time_mh.append([i,float(round(laptime,3))])
            totaltime_mh+=laptime
        totaltime_mh+=22
        time_mh[-1][1]+=20

        for i in range(1,hard_mh+1):
            race_lap=medium_mh+i
            laptime=hard_p+(hard_d*i)-(fb*race_lap)
            totaltime_mh+=laptime
            time_mh.append([race_lap,float(round(laptime,3))])
        strategy['M-H']=f"{totaltime_mh:.3f}"

        hard_hm=int(total_lap*(60/100))
        medium_hm=int(total_lap-hard_hm)
        totaltime_hm=0
        time_hm=[]
        for i in range(1,hard_hm+1):
            laptime=hard_p+(hard_d*i)-(fuel_burn*i)
            time_hm.append([i,float(round(laptime,3))])
            totaltime_hm+=laptime
        totaltime_hm+=20
        time_hm[-1][1]+=20
        for i in range(1,medium_hm+1):
                race_lap=hard_hm+i
                laptime=med_p+(med_d*i)-(fuel_burn*race_lap)
                time_hm.append([race_lap,float(round(laptime,3))])
                totaltime_hm+=laptime
        strategy['H-M']=f"{totaltime_hm:.3f}"

    if ('SOFT' in compound) and ('HARD' in compound or 'MEDIUM' in compound):
                soft_sms = int(total_lap * 0.25)
                medium_sms = int(total_lap * 0.50)
                soft2_sms = int(total_lap - (soft_sms + medium_sms))
                total_time_sms = 0
                time_sms = []
                
                # Check for enough data before pulling floats
                if deg_result.get('MEDIUM', {}).get('Average Pace') == "Not enough data" or \
                   deg_result.get('SOFT', {}).get('Average Pace') == "Not enough data":
                    strategy['S-M-S'] = "Not enough data"
                else:
                    med_p=float(deg_result['MEDIUM']['Average Pace'])
                    med_d=float(deg_result['MEDIUM']['Degradation'])
                    soft_p=float(deg_result['SOFT']['Average Pace'])
                    soft_d=float(deg_result['SOFT']['Degradation'])
                    
                    for i in range(1, soft_sms + 1):
                        laptime = soft_p + (soft_d * i) - (fuel_burn * i)
                        total_time_sms += laptime
                    total_time_sms += 22
                    for i in range(1, medium_sms + 1):
                        race_lap = soft_sms + i
                        laptime = med_p + (med_d * i) - (fuel_burn * race_lap)
                        total_time_sms += laptime
                    total_time_sms += 22
                    for i in range(1, soft2_sms + 1):
                        race_lap = soft_sms + medium_sms + i
                        laptime = soft_p + (soft_d * i) - (fuel_burn * race_lap)
                        total_time_sms += laptime
                    strategy['S-M-S'] = f"{total_time_sms:.3f}"

                # S-M-H Strategy
                if 'HARD' in deg_result and deg_result['HARD']['Average Pace'] != "Not enough data":
                    soft_smh = int(total_lap * 0.20)
                    med_smh = int(total_lap * 0.30)
                    hard_smh = int(total_lap - (soft_smh + med_smh))
                    total_time_smh = 0
                    hard_p=float(deg_result['HARD']['Average Pace'])
                    hard_d=float(deg_result['HARD']['Degradation'])

                    for i in range(1, soft_smh + 1):
                        laptime = soft_p + (soft_d * i) - (fuel_burn * i)
                        total_time_smh += laptime
                    total_time_smh += 22
                    for i in range(1, med_smh + 1):
                        race_lap = soft_smh + i
                        laptime = med_p + (med_d * i) - (fuel_burn * race_lap)
                        total_time_smh += laptime
                    total_time_smh += 22
                    for i in range(1, hard_smh + 1):
                        race_lap = soft_smh + med_smh + i
                        laptime = hard_p + (hard_d * i) - (fuel_burn * race_lap)
                        total_time_smh += laptime
                    strategy['S-M-H'] = f"{total_time_smh:.3f}"
                    
    return {
        'Fuel Burn':f"{average_fuel_burn:.3f}",
        'Degradation':deg_result,
        'Average PitStop Time':22,
        'New Tyre Advantage':new_tyre,
        'Strategy':strategy
    }
