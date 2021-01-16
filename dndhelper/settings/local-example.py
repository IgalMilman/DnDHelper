# Make this unique, and don't share it with anybody.

import os
import sys

AUTO_LOGOUT_DELAY = 3600 # Default logout delay
try:
    exec(open("private/django-sensitive-data.cnf").read())
except:
    print("Error with LOCAL_EXTRA_SETTINGS")
    print(os.getcwd())
    sys.exit(1)

SESSION_COOKIE_AGE = AUTO_LOGOUT_DELAY * 60
