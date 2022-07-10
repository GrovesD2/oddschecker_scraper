import numpy as np
import pandas as pd

def odds_cols(num_outcomes: int):
    '''
    Helper function to give the number of cols
    '''
    return ['odds_' + str(n) for n in range(0, num_outcomes)]


def clean_odds_df(df: pd.DataFrame,
                  num_outcomes: int) -> pd.DataFrame:
    '''
    Filter out any games which are in play, and change the string fractional
    odds to floats
    '''

    df = df[df['time'] != 'In Play']
    
    for col in odds_cols(num_outcomes):
        df[col] = pd.eval(df[col])
    
    return df.reset_index(drop = True)


def is_arb_bet(odds: np.array) -> bool:
    '''
    Find the determinant of the equations that we wish to solve to find if
    arbitrage bets exist
    '''
    
    lin_eq = -np.ones((len(odds), len(odds)))
    np.fill_diagonal(lin_eq, odds.values)
    
    if np.linalg.det(lin_eq) > 0:
        return True
    else:
        return False
    

def get_bet_outcomes(odds):
    '''
    If an arbitrage bet exists, then we can find the ratio of what to place on
    each outcome, as well as the expected return
    '''
    
    # Form the lhs of the linear system
    lhs = -np.ones((len(odds) + 1, len(odds) + 1))
    np.fill_diagonal(lhs, np.append(odds.values, 0))
    lhs[-1, :] = -lhs[-1, :]
    
    # All elements on the rhs are zero except the last, this is set to 1 to
    # normalise the return, simply multiply this answer by the total bet amount
    rhs = np.zeros(len(odds) + 1)
    rhs[-1] = 1
    
    return np.linalg.solve(lhs, rhs).tolist()