# -*- coding: utf-8 -*-
# IS Fianl Project
# Weihao Yuan （Melvin), Zeyang Wu (Duncan)

# import pandas to read csv file
import pandas as pd
import os

# define location （Please change the location）

os.chdir("C:\\Users\waiho\Documents\MSBA\WQ 2018\IS 5201\Final Project")

# Define Function 

def forecast(file_train, file_valid):

    # Step 1: import data
   
    trData = pd.read_csv(file_train)
    vaData = pd.read_csv(file_valid)
    
    # Step 2: Calculate days to departure

    # Calculate days to departure
    trData['days_to_departure'] = pd.to_datetime(trData['departure_date']) - pd.to_datetime(trData['booking_date'])
    vaData['days_to_departure'] = pd.to_datetime(vaData['departure_date']) - pd.to_datetime(vaData['booking_date'])
    
    # Convert data type time to number
    trData['days_to_departure'] = trData['days_to_departure'].dt.days
    vaData['days_to_departure'] = vaData['days_to_departure'].dt.days

    # 2.5Get Weekday of departure date, displaying in Strings format
    trData['weekday'] = pd.to_datetime(trData['departure_date'])
    trData['weekday'] = trData['weekday'].dt.weekday_name

    vaData['weekday'] = pd.to_datetime(vaData['departure_date'])
    vaData['weekday'] = vaData['weekday'].dt.weekday_name    
    
    
    # Step 3: Convert data from both dataset to pivot tables
    tr_matrix = trData.pivot_table(index=['weekday','departure_date'],columns='days_to_departure', values='cum_bookings')

    # Step 4: Calculate the additive matrix 
    # Additive model
    additive_tr_matrix =  pd.DataFrame().reindex_like(tr_matrix)

    for k in range(0,(len(tr_matrix.columns)-1)):
        additive_tr_matrix.iloc[:,k] = tr_matrix.iloc[:,0] - tr_matrix.iloc[:,k]

    additive_tr_matrix.iloc[:,-1] = tr_matrix.iloc[:,-1]

    # Finish Additive model
    
    # Step 5: Calculate the historical average remaining tickets
    
    add_weekday = additive_tr_matrix.groupby(level=0,axis=0).mean()
    
    # Convert the pivot table to the structure similar to the validation data set
    
    add_weekday = add_weekday.stack().rename('remaining').reset_index()

    # Step 6: Merge add_weekday to validation data set based on variables weekday and days to departure 

    va_merge = pd.merge(vaData,add_weekday, left_on=['weekday','days_to_departure'],right_on=['weekday','days_to_departure'])

    # Step 7 : Calculate new variable

    va_merge['forecast'] = va_merge['cum_bookings'] + va_merge['remaining']
    va_merge['error_forecast'] = va_merge['final_demand'] - va_merge['forecast']
    va_merge['error_naive'] = va_merge['final_demand'] - va_merge['naive_forecast']

    # Step 8: Subset data without days to departure = 0
    
    cal_merge = va_merge.loc[va_merge['days_to_departure'] != 0,]

    # Step 9: Calculate MASE
    
    MASE = cal_merge['error_forecast'].abs().sum() / cal_merge['error_naive'].abs().sum()
    
    # Step 10: Output 
    
    print("The MASE is: " + str(MASE))
    print(pd.DataFrame(va_merge[['departure_date', 'booking_date','forecast']]))
    