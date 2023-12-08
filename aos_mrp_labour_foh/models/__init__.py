
from datetime import datetime, timedelta

def float_to_hour(duration):
    """ Convert a number of hours into a time object. """
    td = timedelta(minutes=duration).total_seconds()
    hours = td / 3600.0
    return hours # handle zero hour 12.38, 0.20633333333333334, 0.21

from . import account_account
from . import mrp_labour_foh
from . import account_move
from . import mrp_workorder

    