import scraper

# Mapping of the type of game to consider, to the number of outcomes
GAMES = {
    'tennis': 2,
    'basketball': 2,
    'ufc-mma': 2,
    'baseball': 2,
    
    'football': 3,
    'rugby-union': 3,
    'boxing': 3,
}

if __name__ == '__main__':
    df = scraper.main(GAMES)