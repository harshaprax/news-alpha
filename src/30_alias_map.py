#!/usr/bin/env python3
"""
Build enhanced alias mapping for tickers with word boundary matching
"""

import pandas as pd
from pathlib import Path

def main():
    # Read universe
    universe_path = Path("data/clean/universe.csv")
    universe = pd.read_csv(universe_path)
    
    # Create enhanced alias mappings with mode (contains vs word boundary)
    alias_map = []
    
    # Technology sector aliases (word boundary for brand names)
    tech_aliases = {
        'AAPL': [('apple', 'word'), ('iphone', 'word'), ('ipad', 'word'), ('mac', 'word'), 
                 ('ios', 'word'), ('app store', 'contains'), ('tim cook', 'contains'),
                 ('macbook', 'word'), ('airpods', 'word'), ('apple watch', 'contains')],
        'MSFT': [('microsoft', 'word'), ('windows', 'word'), ('azure', 'word'), 
                 ('office', 'word'), ('xbox', 'word'), ('bing', 'word'), ('satya nadella', 'contains'),
                 ('teams', 'word'), ('surface', 'word'), ('linkedin', 'word')],
        'NVDA': [('nvidia', 'word'), ('geforce', 'word'), ('cuda', 'word'), ('ai', 'word'), 
                 ('gpu', 'word'), ('jensen huang', 'contains'), ('rtx', 'word'),
                 ('tensor', 'word'), ('dlss', 'word'), ('omniverse', 'word')],
        'AMZN': [('amazon', 'word'), ('aws', 'word'), ('prime', 'word'), ('alexa', 'word'), 
                 ('jeff bezos', 'contains'), ('andy jassy', 'contains'), ('amazon web services', 'contains'),
                 ('kindle', 'word'), ('echo', 'word'), ('amazon prime', 'contains')],
        'GOOGL': [('google', 'word'), ('alphabet', 'word'), ('youtube', 'word'), ('android', 'word'), 
                  ('chrome', 'word'), ('sundar pichai', 'contains'), ('google cloud', 'contains'),
                  ('gmail', 'word'), ('maps', 'word'), ('search', 'contains')],
        'META': [('meta', 'word'), ('facebook', 'word'), ('instagram', 'word'), ('whatsapp', 'word'), 
                 ('mark zuckerberg', 'contains'), ('vr', 'word'), ('metaverse', 'word'),
                 ('oculus', 'word'), ('reality labs', 'contains'), ('threads', 'word')],
        'AVGO': [('broadcom', 'word'), ('semiconductor', 'contains'), ('chip', 'contains'),
                 ('hock tan', 'contains'), ('vmware', 'word'), ('symantec', 'word')],
        'ORCL': [('oracle', 'word'), ('database', 'contains'), ('larry ellison', 'contains'),
                 ('java', 'word'), ('mysql', 'word'), ('cloud', 'contains')],
        'CRM': [('salesforce', 'word'), ('saas', 'word'), ('marc benioff', 'contains'),
                ('crm', 'word'), ('slack', 'word'), ('tableau', 'word')],
        'AMD': [('amd', 'word'), ('ryzen', 'word'), ('radeon', 'word'), ('lisa su', 'contains'),
                ('epyc', 'word'), ('zen', 'word'), ('radeon', 'word')],
        'INTC': [('intel', 'word'), ('cpu', 'word'), ('pat gelsinger', 'contains'),
                 ('core', 'word'), ('xeon', 'word'), ('foundry', 'contains')],
        'ADBE': [('adobe', 'word'), ('photoshop', 'word'), ('creative cloud', 'contains'),
                 ('shantanu narayen', 'contains'), ('pdf', 'word'), ('acrobat', 'word')],
        'NFLX': [('netflix', 'word'), ('streaming', 'contains'), ('reed hastings', 'contains'),
                 ('ted sarandos', 'contains'), ('stranger things', 'contains'), ('squid game', 'contains')],
        'PYPL': [('paypal', 'word'), ('venmo', 'word'), ('dan schulman', 'contains'),
                 ('payment', 'contains'), ('digital wallet', 'contains'), ('crypto', 'contains')]
    }
    
    # Financial sector aliases
    fin_aliases = {
        'JPM': [('jpmorgan', 'word'), ('jp morgan', 'contains'), ('jamie dimon', 'contains'), 
                ('chase', 'word'), ('investment bank', 'contains'), ('jpm', 'word')],
        'BAC': [('bank of america', 'contains'), ('bofa', 'word'), ('brian moynihan', 'contains'),
                ('merrill lynch', 'contains'), ('boa', 'word'), ('banking', 'contains')],
        'WFC': [('wells fargo', 'contains'), ('charlie scharf', 'contains'), ('wfc', 'word'),
                ('banking', 'contains'), ('mortgage', 'contains'), ('wealth management', 'contains')],
        'GS': [('goldman sachs', 'contains'), ('david solomon', 'contains'), ('gs', 'word'),
               ('investment bank', 'contains'), ('goldman', 'word'), ('sachs', 'word')],
        'MS': [('morgan stanley', 'contains'), ('james gorman', 'contains'), ('ms', 'word'),
               ('investment bank', 'contains'), ('wealth management', 'contains'), ('stanley', 'word')],
        'V': [('visa', 'word'), ('credit card', 'contains'), ('payment', 'contains'),
              ('al kelly', 'contains'), ('digital payments', 'contains'), ('visa network', 'contains')],
        'MA': [('mastercard', 'word'), ('credit card', 'contains'), ('payment', 'contains'),
               ('michael miebach', 'contains'), ('digital payments', 'contains'), ('ma', 'word')],
        'C': [('citigroup', 'word'), ('jane fraser', 'contains'), ('citi', 'word'),
              ('banking', 'contains'), ('investment bank', 'contains'), ('citibank', 'word')],
        'AXP': [('american express', 'contains'), ('amex', 'word'), ('stephen squerri', 'contains'),
                ('credit card', 'contains'), ('travel', 'contains'), ('membership', 'contains')],
        'BLK': [('blackrock', 'word'), ('larry fink', 'contains'), ('asset management', 'contains'),
                ('etf', 'word'), ('ishares', 'word'), ('investment management', 'contains')]
    }
    
    # Healthcare sector aliases
    health_aliases = {
        'JNJ': [('johnson & johnson', 'contains'), ('janssen', 'word'), ('talc', 'word'),
                ('alex gorsky', 'contains'), ('pharmaceutical', 'contains'), ('medical device', 'contains')],
        'PFE': [('pfizer', 'word'), ('vaccine', 'contains'), ('albert bourla', 'contains'),
                ('pharmaceutical', 'contains'), ('covid', 'contains'), ('mrna', 'word')],
        'UNH': [('unitedhealth', 'word'), ('optum', 'word'), ('andrew witty', 'contains'),
                ('healthcare', 'contains'), ('insurance', 'contains'), ('unh', 'word')],
        'MRK': [('merck', 'word'), ('keytruda', 'word'), ('ken frazier', 'contains'),
                ('pharmaceutical', 'contains'), ('cancer', 'contains'), ('vaccine', 'contains')],
        'ABBV': [('abbvie', 'word'), ('humira', 'word'), ('richard gonzalez', 'contains'),
                 ('pharmaceutical', 'contains'), ('immunology', 'contains'), ('oncology', 'contains')],
        'TMO': [('thermo fisher', 'contains'), ('marc casper', 'contains'), ('scientific', 'contains'),
                 ('laboratory', 'contains'), ('life sciences', 'contains'), ('tmo', 'word')],
        'ABT': [('abbott', 'word'), ('robert ford', 'contains'), ('medical device', 'contains'),
                ('diagnostics', 'contains'), ('nutrition', 'contains'), ('cardiovascular', 'contains')],
        'DHR': [('danaher', 'word'), ('ralph keister', 'contains'), ('life sciences', 'contains'),
                ('diagnostics', 'contains'), ('biotechnology', 'contains'), ('dhr', 'word')],
        'BMY': [('bristol myers', 'contains'), ('giovanni caforio', 'contains'), ('squibb', 'word'),
                ('pharmaceutical', 'contains'), ('oncology', 'contains'), ('immunology', 'contains')],
        'AMGN': [('amgen', 'word'), ('robert bradway', 'contains'), ('biotechnology', 'contains'),
                 ('oncology', 'contains'), ('cardiovascular', 'contains'), ('amgn', 'word')]
    }
    
    # Energy sector aliases
    energy_aliases = {
        'XOM': [('exxon', 'word'), ('exxonmobil', 'word'), ('darren woods', 'contains'),
                ('oil', 'contains'), ('gas', 'contains'), ('petroleum', 'contains')],
        'CVX': [('chevron', 'word'), ('mike wirth', 'contains'), ('oil', 'contains'),
                ('gas', 'contains'), ('petroleum', 'contains'), ('energy', 'contains')],
        'COP': [('conocophillips', 'word'), ('ryan lance', 'contains'), ('oil', 'contains'),
                ('gas', 'contains'), ('exploration', 'contains'), ('production', 'contains')],
        'SLB': [('schlumberger', 'word'), ('oilfield services', 'contains'), ('drilling', 'contains'),
                ('oil', 'contains'), ('gas', 'contains'), ('energy services', 'contains')],
        'EOG': [('eog resources', 'contains'), ('oil', 'contains'), ('gas', 'contains'),
                ('exploration', 'contains'), ('production', 'contains'), ('shale', 'contains')],
        'KMI': [('kinder morgan', 'contains'), ('pipeline', 'contains'), ('natural gas', 'contains'),
                ('energy infrastructure', 'contains'), ('transportation', 'contains'), ('kmi', 'word')],
        'PSX': [('phillips 66', 'contains'), ('refining', 'contains'), ('petroleum', 'contains'),
                ('gasoline', 'contains'), ('chemicals', 'contains'), ('psx', 'word')],
        'MPC': [('marathon petroleum', 'contains'), ('refining', 'contains'), ('petroleum', 'contains'),
                ('gasoline', 'contains'), ('chemicals', 'contains'), ('mpc', 'word')],
        'VLO': [('valero energy', 'contains'), ('refining', 'contains'), ('petroleum', 'contains'),
                ('gasoline', 'contains'), ('ethanol', 'contains'), ('vlo', 'word')],
        'WMB': [('williams companies', 'contains'), ('natural gas', 'contains'), ('pipeline', 'contains'),
                ('energy infrastructure', 'contains'), ('transportation', 'contains'), ('wmb', 'word')]
    }
    
    # Consumer Discretionary aliases
    cd_aliases = {
        'TSLA': [('tesla', 'word'), ('elon musk', 'contains'), ('model 3', 'contains'), 
                 ('model y', 'contains'), ('cybertruck', 'word'), ('electric vehicle', 'contains'),
                 ('ev', 'word'), ('autopilot', 'word'), ('gigafactory', 'word')],
        'HD': [('home depot', 'contains'), ('home improvement', 'contains'), ('craig menear', 'contains'),
               ('retail', 'contains'), ('hardware', 'contains'), ('construction', 'contains')],
        'MCD': [('mcdonalds', 'word'), ('fast food', 'contains'), ('chris kempczinski', 'contains'),
                ('burger', 'contains'), ('franchise', 'contains'), ('restaurant', 'contains')],
        'NKE': [('nike', 'word'), ('sportswear', 'contains'), ('john donahoe', 'contains'),
                ('athletic', 'contains'), ('sneakers', 'contains'), ('jordan', 'word')],
        'LOW': [('lowes', 'word'), ('home improvement', 'contains'), ('marvin ellison', 'contains'),
                ('retail', 'contains'), ('hardware', 'contains'), ('construction', 'contains')],
        'SBUX': [('starbucks', 'word'), ('coffee', 'contains'), ('kevin johnson', 'contains'),
                 ('cafe', 'contains'), ('beverage', 'contains'), ('retail', 'contains')],
        'TJX': [('tjx', 'word'), ('tj maxx', 'contains'), ('marshalls', 'word'), ('homegoods', 'word'),
                ('off-price', 'contains'), ('retail', 'contains')],
        'BKNG': [('booking', 'word'), ('priceline', 'word'), ('travel', 'contains'),
                 ('hotel', 'contains'), ('vacation rental', 'contains'), ('online travel', 'contains')],
        'CMG': [('chipotle', 'word'), ('mexican grill', 'contains'), ('brian niccol', 'contains'),
                ('fast casual', 'contains'), ('restaurant', 'contains'), ('burrito', 'contains')],
        'LMT': [('lockheed martin', 'contains'), ('defense', 'contains'), ('aerospace', 'contains'),
                ('military', 'contains'), ('fighter jet', 'contains'), ('f-35', 'word')],
        'BA': [('boeing', 'word'), ('aircraft', 'contains'), ('dave calhoun', 'contains'),
               ('airplane', 'contains'), ('737', 'word'), ('787', 'word'), ('defense', 'contains')]
    }
    
    # Consumer Staples aliases
    cs_aliases = {
        'WMT': [('walmart', 'word'), ('retail', 'contains'), ('doug mcmillon', 'contains'),
                ('supermarket', 'contains'), ('grocery', 'contains'), ('discount', 'contains')],
        'COST': [('costco', 'word'), ('wholesale', 'contains'), ('craig jelinek', 'contains'),
                 ('membership', 'contains'), ('warehouse', 'contains'), ('bulk', 'contains')],
        'KO': [('coca cola', 'contains'), ('soft drink', 'contains'), ('james quincey', 'contains'),
               ('soda', 'contains'), ('beverage', 'contains'), ('sprite', 'word')],
        'PEP': [('pepsi', 'word'), ('soft drink', 'contains'), ('ramon laguarta', 'contains'),
                ('soda', 'contains'), ('beverage', 'contains'), ('frito lay', 'contains')],
        'PG': [('procter & gamble', 'contains'), ('consumer goods', 'contains'), ('jon moeller', 'contains'),
               ('household', 'contains'), ('personal care', 'contains'), ('tide', 'word')],
        'CL': [('colgate', 'word'), ('palmolive', 'word'), ('oral care', 'contains'),
               ('toothpaste', 'contains'), ('personal care', 'contains'), ('cl', 'word')],
        'KMB': [('kimberly clark', 'contains'), ('tissue', 'contains'), ('paper products', 'contains'),
                ('personal care', 'contains'), ('diapers', 'contains'), ('kmb', 'word')],
        'GIS': [('general mills', 'contains'), ('cereal', 'contains'), ('food', 'contains'),
                ('breakfast', 'contains'), ('yogurt', 'contains'), ('gis', 'word')],
        'K': [('kellogg', 'word'), ('cereal', 'contains'), ('breakfast', 'contains'),
              ('food', 'contains'), ('snacks', 'contains'), ('k', 'word')],
        'SYY': [('sysco', 'word'), ('food service', 'contains'), ('restaurant supply', 'contains'),
                ('food distribution', 'contains'), ('wholesale', 'contains'), ('syy', 'word')]
    }
    
    # Industrials aliases
    ind_aliases = {
        'CAT': [('caterpillar', 'word'), ('construction', 'contains'), ('doug oberhelman', 'contains'),
                ('heavy machinery', 'contains'), ('mining', 'contains'), ('equipment', 'contains')],
        'HON': [('honeywell', 'word'), ('aerospace', 'contains'), ('darius adamczyk', 'contains'),
                ('industrial', 'contains'), ('automation', 'contains'), ('technology', 'contains')],
        'GE': [('general electric', 'contains'), ('aviation', 'contains'), ('larry culp', 'contains'),
               ('power', 'contains'), ('renewable energy', 'contains'), ('healthcare', 'contains')],
        'UPS': [('ups', 'word'), ('shipping', 'contains'), ('carol tome', 'contains'),
                ('logistics', 'contains'), ('delivery', 'contains'), ('package', 'contains')],
        'RTX': [('raytheon', 'word'), ('technologies', 'contains'), ('defense', 'contains'),
                ('aerospace', 'contains'), ('military', 'contains'), ('rtx', 'word')],
        'MMM': [('3m', 'word'), ('industrial', 'contains'), ('mike roman', 'contains'),
                ('manufacturing', 'contains'), ('innovation', 'contains'), ('post-it', 'word')],
        'DE': [('deere', 'word'), ('john deere', 'contains'), ('agriculture', 'contains'),
               ('farming', 'contains'), ('construction', 'contains'), ('equipment', 'contains')],
        'ITW': [('illinois tool works', 'contains'), ('industrial', 'contains'), ('manufacturing', 'contains'),
                ('tools', 'contains'), ('equipment', 'contains'), ('itw', 'word')],
        'EMR': [('emerson', 'word'), ('electric', 'contains'), ('industrial', 'contains'),
                ('automation', 'contains'), ('technology', 'contains'), ('emr', 'word')],
        'FDX': [('fedex', 'word'), ('shipping', 'contains'), ('logistics', 'contains'),
                ('delivery', 'contains'), ('express', 'contains'), ('freight', 'contains')]
    }
    
    # Utilities aliases
    util_aliases = {
        'NEE': [('nextera energy', 'contains'), ('renewable', 'contains'), ('jim robo', 'contains'),
                ('solar', 'contains'), ('wind', 'contains'), ('clean energy', 'contains')],
        'DUK': [('duke energy', 'contains'), ('electric', 'contains'), ('lynn good', 'contains'),
                ('power', 'contains'), ('utilities', 'contains'), ('energy', 'contains')],
        'SO': [('southern company', 'contains'), ('electric', 'contains'), ('tom fanning', 'contains'),
               ('power', 'contains'), ('utilities', 'contains'), ('energy', 'contains')],
        'EXC': [('exelon', 'word'), ('nuclear', 'contains'), ('chris crane', 'contains'),
                ('electric', 'contains'), ('power', 'contains'), ('utilities', 'contains')],
        'AEP': [('american electric power', 'contains'), ('electric', 'contains'), ('nick akins', 'contains'),
                ('power', 'contains'), ('utilities', 'contains'), ('energy', 'contains')],
        'XEL': [('xcel energy', 'contains'), ('electric', 'contains'), ('power', 'contains'),
                ('utilities', 'contains'), ('energy', 'contains'), ('renewable', 'contains')],
        'SRE': [('sempra energy', 'contains'), ('natural gas', 'contains'), ('electric', 'contains'),
                ('utilities', 'contains'), ('energy', 'contains'), ('infrastructure', 'contains')],
        'PEG': [('public service enterprise', 'contains'), ('electric', 'contains'), ('power', 'contains'),
                ('utilities', 'contains'), ('energy', 'contains'), ('gas', 'contains')],
        'WEC': [('wec energy group', 'contains'), ('electric', 'contains'), ('power', 'contains'),
                ('utilities', 'contains'), ('energy', 'contains'), ('gas', 'contains')],
        'ES': [('eversource energy', 'contains'), ('electric', 'contains'), ('power', 'contains'),
               ('utilities', 'contains'), ('energy', 'contains'), ('gas', 'contains')]
    }
    
    # Communication Services aliases
    comm_aliases = {
        'DIS': [('disney', 'word'), ('streaming', 'contains'), ('bob chapek', 'contains'),
                ('entertainment', 'contains'), ('theme parks', 'contains'), ('movies', 'contains')],
        'T': [('at&t', 'word'), ('telecom', 'contains'), ('john stankey', 'contains'),
              ('wireless', 'contains'), ('internet', 'contains'), ('5g', 'word')],
        'VZ': [('verizon', 'word'), ('telecom', 'contains'), ('hans vestberg', 'contains'),
               ('wireless', 'contains'), ('internet', 'contains'), ('5g', 'word')],
        'CMCSA': [('comcast', 'word'), ('cable', 'contains'), ('brian roberts', 'contains'),
                  ('internet', 'contains'), ('broadband', 'contains'), ('nbc', 'word')],
        'CHTR': [('charter', 'word'), ('spectrum', 'word'), ('cable', 'contains'),
                 ('internet', 'contains'), ('broadband', 'contains'), ('chtr', 'word')],
        'TMUS': [('t-mobile', 'word'), ('telecom', 'contains'), ('mike sievert', 'contains'),
                 ('wireless', 'contains'), ('5g', 'word'), ('tmobile', 'word')]
    }
    
    # Materials aliases
    mat_aliases = {
        'LIN': [('linde', 'word'), ('industrial gases', 'contains'), ('steve angel', 'contains'),
                ('chemicals', 'contains'), ('manufacturing', 'contains'), ('lin', 'word')],
        'NEM': [('newmont', 'word'), ('gold mining', 'contains'), ('tom palmer', 'contains'),
                ('mining', 'contains'), ('gold', 'contains'), ('precious metals', 'contains')],
        'FCX': [('freeport-mcmoran', 'word'), ('copper', 'contains'), ('richard adkerson', 'contains'),
                ('mining', 'contains'), ('metals', 'contains'), ('fcx', 'word')],
        'APD': [('air products', 'contains'), ('industrial gases', 'contains'), ('chemicals', 'contains'),
                ('manufacturing', 'contains'), ('apd', 'word'), ('hydrogen', 'contains')],
        'SHW': [('sherwin-williams', 'word'), ('paint', 'contains'), ('coatings', 'contains'),
                ('chemicals', 'contains'), ('manufacturing', 'contains'), ('shw', 'word')],
        'ECL': [('ecolab', 'word'), ('chemicals', 'contains'), ('cleaning', 'contains'),
                ('water treatment', 'contains'), ('manufacturing', 'contains'), ('ecl', 'word')],
        'DD': [('dupont', 'word'), ('chemicals', 'contains'), ('manufacturing', 'contains'),
               ('materials', 'contains'), ('innovation', 'contains'), ('dd', 'word')],
        'DOW': [('dow', 'word'), ('chemicals', 'contains'), ('manufacturing', 'contains'),
                ('materials', 'contains'), ('plastics', 'contains'), ('dow chemical', 'contains')],
        'PPG': [('ppg', 'word'), ('paint', 'contains'), ('coatings', 'contains'),
                ('chemicals', 'contains'), ('manufacturing', 'contains'), ('industrial', 'contains')],
        'IFF': [('international flavors', 'contains'), ('fragrances', 'contains'), ('chemicals', 'contains'),
                ('manufacturing', 'contains'), ('food', 'contains'), ('iff', 'word')]
    }
    
    # Real Estate aliases
    re_aliases = {
        'PLD': [('prologis', 'word'), ('warehouse', 'contains'), ('hamid moghadam', 'contains'),
                ('logistics', 'contains'), ('industrial real estate', 'contains'), ('pld', 'word')],
        'AMT': [('american tower', 'contains'), ('cell towers', 'contains'), ('tom bartlett', 'contains'),
                ('telecom', 'contains'), ('wireless', 'contains'), ('infrastructure', 'contains')],
        'SPG': [('simon property', 'contains'), ('malls', 'contains'), ('david simon', 'contains'),
                ('retail real estate', 'contains'), ('shopping centers', 'contains'), ('spg', 'word')],
        'CCI': [('crown castle', 'contains'), ('cell towers', 'contains'), ('telecom', 'contains'),
                ('wireless', 'contains'), ('infrastructure', 'contains'), ('cci', 'word')],
        'EQIX': [('equinix', 'word'), ('data centers', 'contains'), ('cloud', 'contains'),
                 ('internet', 'contains'), ('technology', 'contains'), ('eqix', 'word')],
        'PSA': [('public storage', 'contains'), ('self storage', 'contains'), ('storage', 'contains'),
                ('real estate', 'contains'), ('psa', 'word'), ('rental', 'contains')],
        'EXR': [('extra space storage', 'contains'), ('self storage', 'contains'), ('storage', 'contains'),
                ('real estate', 'contains'), ('exr', 'word'), ('rental', 'contains')],
        'AVB': [('avalonbay', 'word'), ('apartments', 'contains'), ('residential', 'contains'),
                ('real estate', 'contains'), ('rental', 'contains'), ('avb', 'word')],
        'EQR': [('equity residential', 'contains'), ('apartments', 'contains'), ('residential', 'contains'),
                ('real estate', 'contains'), ('rental', 'contains'), ('eqr', 'word')],
        'MAA': [('mid-america apartment', 'contains'), ('apartments', 'contains'), ('residential', 'contains'),
                ('real estate', 'contains'), ('rental', 'contains'), ('maa', 'word')]
    }
    
    # Combine all aliases
    all_aliases = {
        **tech_aliases,
        **fin_aliases,
        **health_aliases,
        **energy_aliases,
        **cd_aliases,
        **cs_aliases,
        **ind_aliases,
        **util_aliases,
        **comm_aliases,
        **mat_aliases,
        **re_aliases
    }
    
    # Create alias map DataFrame
    for ticker, aliases in all_aliases.items():
        for alias, mode in aliases:
            alias_map.append({'ticker': ticker, 'alias': alias, 'mode': mode})
    
    # Add SPY benchmark
    alias_map.append({'ticker': 'SPY', 'alias': 'spy', 'mode': 'word'})
    alias_map.append({'ticker': 'SPY', 'alias': 's&p 500', 'mode': 'contains'})
    alias_map.append({'ticker': 'SPY', 'alias': 'sp500', 'mode': 'word'})
    alias_map.append({'ticker': 'SPY', 'alias': 'spdr', 'mode': 'word'})
    alias_map.append({'ticker': 'SPY', 'alias': 'etf', 'mode': 'contains'})
    
    alias_df = pd.DataFrame(alias_map)
    
    # Save to parquet
    output_path = Path("data/clean/alias_map.parquet")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    alias_df.to_parquet(output_path, index=False)
    
    print(f"Alias map shape: {alias_df.shape}")
    print(f"Unique tickers: {alias_df['ticker'].nunique()}")
    print(f"Contains mode: {len(alias_df[alias_df['mode'] == 'contains'])}")
    print(f"Word mode: {len(alias_df[alias_df['mode'] == 'word'])}")
    print("\nPreview:")
    print(alias_df.head(10))
    print(f"\nSaved to: {output_path}")

if __name__ == "__main__":
    main()
