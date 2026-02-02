import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from parsers.amazon import AmazonParser
    from parsers.cisco import CiscoParser
    from parsers.crowdstrike import CrowdstrikeParser
    from parsers.datadog import DatadogParser
    from parsers.microsoft import MicrosoftParser
    from parsers.spotify import SpotifyParser
    from parsers.gen import GenParser
    from parsers.paypal import PayPalParser
    from parsers.meta import MetaParser
    from parsers.netflix import NetflixParser
    from parsers.trend_micro import TrendMicroParser
    
    print("SUCCESS: All parsers imported successfully.")
except Exception as e:
    print(f"FAILURE: Import validation failed: {e}")
    sys.exit(1)
