# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from . import general_ledger_report
from . import account_report_common_account
from . import report_partner_ledger
from . import report_tax
from . import report_trial_balance
from . import report_aged_partner
from . import report_journal_audit
from . import report_financial
from . import cash_flow_report
from . import account_bank_book
from . import account_cash_book
from . import account_day_book
from . import account_asset_report
from . import multiple_invoice_report
from . import report_financial_excel
from . import report_trial_balance_excel

# Default Column and row for report excel
DEFAULT_COLUMN = {'default_header_row':6,'default_header_col':0,'default_row':7,'default_col':0}

# Default Column in Alphabet for set total
# Key is number cell e.g 1 2 3
# Value is alphabet of number cell e.g C D AB AZ
DEFAULT_COLUMN_ALPHABET = [
    'A','B','C','D','E','F','G','H','I','J','K','L',
    'M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',

    'AA','AB','AC','AD','AE','AF','AG','AH','AI','AJ','AK','AL',
    'AM','AN','AO','AP','AQ','AR','AS','AT','AU','AV','AW','AX','AY','AZ',

    'BA','BB','BC','BD','BE','BF','BG','BH','BI','BJ','BK','BL',
    'BM','BN','BO','BP','BQ','BR','BS','BT','BU','BV','BW','BX','BY','BZ',

    'CA','CB','CC','CD','CE','CF','CG','CH','CI','CJ','CK','CL',
    'CM','CN','CO','CP','CQ','CR','CS','CT','CU','CV','CW','CX','CY','CZ',

    'DA','DB','DC','DD','DE','DF','DG','DH','DI','DJ','DK','DL',
    'DM','DN','DO','DP','DQ','DR','DS','DT','DU','DV','DW','DX','DY','DZ',

    'EA','EB','EC','ED','EE','EF','EG','EH','EI','EJ','EK','EL',
    'EM','EN','EO','EP','EQ','ER','ES','ET','EU','EV','EW','EX','EY','EZ',
]