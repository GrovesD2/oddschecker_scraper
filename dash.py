import pandas as pd
import streamlit as st

import main

st.header('ROB - Ripping Off Bookmakers')

# Button to run the scanner
if st.sidebar.button(label = 'Run scanner'):  
    main.main()

df = pd.read_csv('current_opportunities.csv')

# Filters for the results -----------------------------------------------------

st.sidebar.subheader('Filters')

game = st.sidebar.selectbox(
    'Game',
    ['any'] + df['game'].unique().tolist()
)

lower_perc = st.sidebar.number_input(
    'Lower return threshold (%)',
    min_value = 0,
    max_value = 99,
    step = 1,    
)

upper_perc = st.sidebar.number_input(
    'Upper return threshold (%)',
    value = 1000,
    min_value = int(lower_perc),
    max_value = 1000,
    step = 1,
)

# Apply the filters to the results -------------------------------------------

if game != 'any':
    df = df[df['game'] == game]
    
df = (
    df[
       (df['return'] > lower_perc/100) &
       (df['return'] < upper_perc/100)
    ]
    .sort_values('return', ascending = False)
    .reset_index(drop = True)
)

# Filter for the game number -------------------------------------------------

st.sidebar.subheader('Game Controls')

idx = st.sidebar.number_input(
    'Game number',
    min_value = 0,
    max_value = len(df)-1,
    step = 1,
)


# This is the filtered version of the dataframe to the game we are considering
df_filt = df.iloc[[int(idx)]]

# Get the information from the filtered dataframe ----------------------------

n_outcomes = df_filt['n_outcomes'][0]
player_1 = df_filt['name_0'][0]
player_2 = df_filt['name_1'][0]
time = df_filt['time'][0]

capital = st.sidebar.number_input(
    'Rough captial to place on bet',
    value = 100.,
    min_value = 0.,
    step = 0.01,
)

max_ret = round(capital*df_filt['return'][0], 2)
perc = round(100*(df_filt['return'][0]), 2)

st.subheader('Exact Arbitrage Betting')

# Write out the precise arbitrage amount to place on each outcome
if n_outcomes == 3:
    arb_bet_values = {
        f'Bet on {player_1}': round(df_filt['bet_0'][0]*capital, 2),
        f'Bet on {player_2}': round(df_filt['bet_2'][0]*capital, 2),
        'Bet on draw': round(df_filt['bet_1'][0]*capital, 2),
    }
elif n_outcomes == 2:
    arb_bet_values = {
        f'Bet on {player_1}': round(df_filt['bet_0'][0]*capital, 2),
        f'Bet on {player_2}': round(df_filt['bet_1'][0]*capital, 2),
    }
    
game_info, arb_info = st.columns(2)

with game_info:
    st.write(
        'Sport : ' + df_filt['game'][0] + '  \n'
        'Game : ' + player_1 + ' vs ' + player_2 + '  \n'
        'Time : ' + str(time) + '  \n'
        'Arb return: £' + str(max_ret) + f' ({perc}%)' + ' \n'
    )

with arb_info:
    st.write('Arbitrage betting split:' + '  \n ' + 
        '  \n '.join([
            key + ' £' + str(round(value, 2))
            for key, value in arb_bet_values.items()
        ])
    )

# Write the fractional odds that were scraped from oddschecker (to visually
# confirm whether the odds are the same)
st.subheader('Scraped Odds')

if n_outcomes == 2:
    odds_str = (
        player_1 + ' : ' + str(df['fractional_odds_0'][0])
        + '  \n'
        + player_2 + ' : ' + str(df['fractional_odds_1'][0])
    )

elif n_outcomes == 3:
    odds_str = (
        player_1 + ' : ' + str(df['fractional_odds_0'][0])
        + '  \n'
        + player_2 + ' : ' + str(df['fractional_odds_2'][0])
        + '  \n'
        + 'Draw : ' + df['fractional_odds_1'][0]
    )

st.write(odds_str)

# Values for betting ---------------------------------------------------------

st.subheader('Adjusted Betting')

if n_outcomes == 2:
    
    bet1, bet2 = st.columns(2)
    
    with bet1:
        p1_bet = st.number_input(
            f'Bet on {player_1}',
            value = arb_bet_values[f'Bet on {player_1}'],
            step = 0.01,
        )
    with bet2:
        p2_bet = st.number_input(
            f'Bet on {player_2}',
            value = arb_bet_values[f'Bet on {player_2}'],
            step = 0.01,
        )
        
    returns = {
        f'Profit on {player_1}': (df_filt['odds_0'][0])*p1_bet - p2_bet,
        f'Profit on {player_2}': (df_filt['odds_1'][0])*p2_bet - p1_bet,
    }
    
elif n_outcomes == 3:
    
    bet1, bet2, bet3 = st.columns(3)
    
    with bet1:
        p1_bet = st.number_input(
            f'Bet on {player_1}',
            value = arb_bet_values[f'Bet on {player_1}'],
            step = 0.01,
        )
    with bet2:
        draw_bet = st.number_input(
            'Bet on draw',
            value = arb_bet_values['Bet on draw'],
            step = 0.01,
        ) 
    with bet3:
        p2_bet = st.number_input(
            f'Bet on {player_2}',
            value = arb_bet_values[f'Bet on {player_2}'],
            step = 0.01,
        )
        
    returns = {
        f'Profit on {player_1}': df_filt['odds_0'][0]*p1_bet - p2_bet - draw_bet,
        'Profit on draw': df_filt['odds_1'][0]*draw_bet - p1_bet - p2_bet,
        f'Profit on {player_2}': df_filt['odds_2'][0]*p2_bet - p1_bet - draw_bet,
    }
        
st.write(
    '  \n '.join([
        key + ' £' + str(round(value, 2)) 
        for key, value in returns.items()
    ])
)
    
st.subheader('The Filtered Dataframe')
st.write(df)