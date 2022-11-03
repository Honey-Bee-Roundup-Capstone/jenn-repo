import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import seaborn as sns

def get_bee_data():
    '''
    Reads the Raw data of the Bee Informed State Bee Loss Table (2022) CSV,
    Drops columns that contain data we don't plan to utilize.
    Drops the first column since they're the 'Python Column Names',
    Renames columns into a more Python friendly format,
    Saves the new working CSV as bee_colony_loss.csv
    '''
    # Read Raw CSV:
    df = pd.read_csv("BeeInformed_States_Loss_Table_by_Year_public_ready_2022.csv")
    # Drops several columns with data from their statistical accounting, which is nice they included, but we're looking more for numbers to work with for our own stats.
    df = df.drop(columns=["Column name as written in R Script", 'State abbreviation', "Method of tallying multi-states operations (included in all states, excluded from all states, exlusively multi-states)", 
       'Bootstrap replication',
       'Bootstrap method',
       'Bootstrap estimate of the Total Loss (weigthed average)',
       'Boostrap-based 95% confidence interval(low) of the weighted average loss',
       'Boostrap-based 95% confidence interval(high) of the weighted average loss',
       'Bootstrap estimate of the Average Loss (unweigthed average)',
       'Boostrap-based 95% confidence interval(low) of the unweighted average loss',
       'Boostrap-based 95% confidence interval(high) of the unweighted average loss',
       'glm-based 95% confidence interval(low) of the weighted average loss',
       'glm-based 95% confidence interval(high) of the weighted average loss',
       'standard deviation of operational losses',
       'standard error of the unweithed average estimate',
       'glm-based 95% confidence interval(low) of the unweighted average loss',
       'glm-based 95% confidence interval(high) of the unweighted average loss',
       'Total number of colonies "at risk" (colonies at the start, new colonies added, without colonies sold or given away)'])
    # Due to the format the CSV comes in, the first line is "Python" column names, so we'll drop the first row since we're stuck with the R column names for our columns.
    df = df.iloc[1:, :]
    # Renaming Columns to be more Python Friendly.
    df.columns = ["state", "year", "season", "beekeepers", "total_loss", "average_loss", "starting_colonies", "colonies_lost", "ending_colonies", "beekeepers_exclusive_to_state", "colonies_exclusive_to_state"]
    df.to_csv("bee_colony_loss.csv")
    return df
    

def prep_bees():
    '''This function loads the bee_colony_loss.csv into a dataframe, cleans and sorts it, and returns a dataframe.'''
    # read the csv into a pandas dataframe
    df = pd.read_csv('bee_colony_loss.csv')
    # drop the unnamed column
    df = df.drop(columns='Unnamed: 0')
    # sort by descending year and ascending state
    df = df.sort_values(['year','state'], ascending=[False,True])
    # drop nulls
    df = df.dropna()
    # lowercase all strings in state and replace spaces with underscores
    df.state = df.state.str.lower().str.replace(' ','_')
    # lowercase all strings in the season column
    df.season = df.season.str.lower()
    # remove observations that have 10 or less beekeepers
    df = df[df.beekeepers > 10]
    # drop duplicate rows
    df = df.drop_duplicates()
    # change total_loss column to float
    df.total_loss = df.total_loss.astype(float)
    # change average_loss column to float
    df.average_loss = df.average_loss.astype(float)
    # change ending_colonies column to int
    df.ending_colonies = df.ending_colonies.astype(int)
    # change colonies_lost column to int
    df.colonies_lost = df.colonies_lost.astype(int)
    # pull only annual season data
    df = df[df.season == "annual"]
    #pull non multistates and non continental usa data
    df = df[(df.state != "multistates")& (df.state != "non_continental_usa")]
    # create column net gain / loss for each state
    df['colonies_net_gain'] = df.ending_colonies - df.starting_colonies
    # create a column for beekeeper to colony ratio
    df['beekeeper_colony_ratio'] = df.ending_colonies / df.beekeepers
    # look at only beekeepers exclusive to state
    df = df[df.beekeepers_exclusive_to_state == 100]
    # return the cleaned and sorted dataframe
    return df

def state_ansi():
    ''' This function will load state ansi from csv and turn state with its corresponding ansi'''
    #read the csv
    df = pd.read_csv("state_ansi.txt",sep = "|")
    #lower case column names 
    df.columns = df.columns.str.lower()
    #lower case string values on the column and replace wmpty spaces with underscore
    df.state_name = df.state_name.str.lower().str.replace(' ','_')
    #rename column names and drop unnecessary columns
    df = df.rename(columns = {"state":"ansi", "state_name":"state"}).drop(columns = ["stusab", "statens"])
    
    #return back dataframe
    return df

def geo_data():
    ''' This function will load state ansi from csv and turn state with its corresponding ansi'''
    #read csv
    df = pd.read_csv("state_geocords.csv", index_col = [0] )
    #rename column
    df= df.rename(columns = {"name":"state"})
    # lowercase values of column and replace spaces with underscore
    df.state = df.state.str.lower().str.replace(' ','_')
    #pull only useful column
    df = df[["state","latitude","longitude"]]
    
    #return back dataframe
    return df

def bee_merged():
    '''This function will call in three different function and merge them all'''
    #call in prep bees function
    df = prep_bees()
    #call in function for state  ansi data
    df1 = state_ansi()
    #call in function for geo data
    df2 = geo_data()
    #left join prep_bees dataset with state_ansi
    df = df.merge(df1, on = 'state', how = 'left')
    #left join prep_bees dataster with geo_state
    df = df.merge(df2, on="state", how = "left")
    
    #return back dataframe
    return df


def bee_wrangle():
    '''
    initial clean data creation, then loading of clean data and addition of state ansi and geo data
    returns df merged and ready to go.
    after initial prep, bee_merged() is only item that needs to be called to get data going.
    '''
    # Pulling the initial data to clean it, saves as bee_colony_loss.csv:
    df = get_bee_data()
    # loads the clean data, state ansi data, geo location data and then left joins them on state to the clean data.
    df = bee_merged()
    # Returns brand new DataFrame ready to go!
    return df