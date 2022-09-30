import re
import bs4
import utils
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver

BASE_URL = 'https://www.oddschecker.com/'


def get_html(url: str):
    '''
    Get the HTML from the url, using Chromedriver to load the page
    '''
    driver = webdriver.Chrome()
    driver.get(url)
    return driver.page_source

    
def get_match_info(matches: bs4.element.ResultSet,
                   n_outcomes: int) -> pd.DataFrame:
    '''
    Over all possible matches from the scraped html, get the information and
    output as a pandas dataframe. 

    Note: sometimes the data does not scrape correctly, i.e. we could be 
    missing one of the odds because of it refreshing. Therefore, if we don't
    have the right amount of information (e.g. side/players (2), time of play
    (1) and odds (n)) then we move onto the next
    '''

    data = []
    for match in matches:
        
        # Replace anything between <> with a !, this can be used to split and
        # obtain the information we want
        match_str = re.sub(re.compile('<.*?>'), '!', str(match))
        
        # Once the item is split on !, we don't want any blank strings or
        # the string saying "All Odds"
        info = [
            item for item in match_str.split('!') 
            if item not in ['', 'All Odds']
        ]
        
        # This is a logical check to see if we have all the info we need, if
        # we don't then the scrape did not work and we move onto the next. The
        # info we need is date, name_1, name_2 and the odds
        if len(info) == n_outcomes + 3:
            data.append(info)
            
    # Turn the data into a pandas dataframe, if the scrape was successful
    if len(data) > 0:
        return pd.DataFrame(
            columns = ['time', 'name_0', 'name_1'] + utils.odds_cols(n_outcomes),
            data = data
        )
    else:
        return None

        
def classify_bets(df: pd.DataFrame,
                  n_outcomes: int) -> pd.DataFrame:
    
    # Determine the outcome of each bet
    bet_outcomes = (
        df[utils.odds_cols(n_outcomes)]
        .apply(utils.get_bet_outcomes, axis = 1)
    )
    bet_outcomes = pd.DataFrame(
        data = bet_outcomes.tolist(),
        columns = ['bet_' + str(n) for n in range(0, n_outcomes)] + ['return'],
    )
   
    df = pd.concat([df, bet_outcomes], axis = 1)
    
    return df[df['return'] > 0]
    
    
def main(games: dict) -> pd.DataFrame:
    '''
    Main function for calling the scraper and finding the arb bets
    
    Parameters
    ----------
    games: dict
        A mapping of {url: number of outcomes}
    '''
    
    dfs = []
    for game, n_outcomes in games.items():
        
        print('Scraping', game)
        
        # Read in the html and parse with beautiful soup
        html = get_html(BASE_URL + game)
        soup = BeautifulSoup(html, 'html.parser')
        
        # Turn the matches into a pandas datafame
        df = get_match_info(
            soup.findAll('tr', {'class': 'match-on'}),
            n_outcomes,
        )
        
        if df is not None:
                
            try:
            
                # Perform cleaning steps to the dataframe
                df = utils.clean_odds_df(df, n_outcomes)
                
                # Find arb bets and get the betting ratios (if they exist)
                df = classify_bets(df, n_outcomes)
                
                if len(df) > 0:
                
                    # Add the game identifier and add to the list of dfs
                    df.loc[:, 'game'] = game
                    df.loc[:, 'n_outcomes'] = n_outcomes
                    dfs.append(df)
                
            except Exception as e:
                
                print(f'{game} failed:', e)
        
    if len(dfs) > 0:
        return utils.format_cols(
            pd.concat(dfs, axis = 0, ignore_index = True)
        )
    else:
        return None