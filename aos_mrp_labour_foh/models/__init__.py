


def float_to_hour(duration):
    """ Convert a number of hours into a time object. """
    hours, seconds = divmod(duration * 60, 3600)  # split to hours and seconds
    minutes, seconds = divmod(seconds, 60)  # split the seconds to minutes and seconds
    return hours + (minutes / 100.0) # handle zero hour

from . import account_account
from . import mrp_labour_foh
from . import account_move
from . import mrp_workorder

    