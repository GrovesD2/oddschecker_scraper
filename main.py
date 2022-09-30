import scraper

# Mapping of the type of game to consider to the number of outcomes
GAMES = {
    'tennis': 2,
    'basketball': 2,
    'ufc-mma': 2,
    'baseball': 2,
    'chess': 2,
    'e-sports': 2,
    'volleyball': 2,
    
    'football': 3,
    'rugby-union': 3,
    'rugby-league': 3,
    'boxing': 3,
    'gaelic-games': 3,
}

def main():
    '''
    Main running function (also called in the dash)
    '''
    
    df = scraper.main(GAMES)
    
    if df is not None:
        df.to_csv('current_opportunities.csv', index = False)
    else:
        print('No arbitrage bets detected')
    
    return 

if __name__ == '__main__':
    main()