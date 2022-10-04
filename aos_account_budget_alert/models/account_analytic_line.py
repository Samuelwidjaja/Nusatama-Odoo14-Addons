# -*- coding: utf-8 -*-

import time
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.tools.misc import formatLang
from odoo.tools import float_is_zero, float_compare
from odoo.tools.safe_eval import safe_eval
import odoo.addons.decimal_precision as dp

# class ResUsers(models.Model):
#     _inherit = "res.users"
    
#     password_auth = fields.Char('Password Approval Budget')

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    
    committed_account_id = fields.Many2one('account.account', string='Committed Account')
    committed_amount = fields.Monetary('Committed', required=True, default=0.0)
    #invoice_ids = fields.Many2one('account.move', 'Invoice', ondelete='cascade', index=True)
    # invoice_line_id = fields.Many2one('account.move.line', 'Invoice', ondelete='cascade', index=True)
    invoice_line_ids = fields.Many2many('account.move.line', 
            'account_anayltic_line_move_line_rel',
            'analytic_line_id', 'move_line_id',
        'Invoice Line', ondelete='cascade', index=True)
    