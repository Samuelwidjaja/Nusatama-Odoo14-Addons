# -*- coding: utf-8 -*-

import time
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.tools.misc import formatLang
from odoo.tools import float_is_zero, float_compare
from odoo.tools.safe_eval import safe_eval
import odoo.addons.decimal_precision as dp

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    
    # committed_account_id = fields.Many2one('account.account', string='Committed Account')
    # committed_amount = fields.Monetary('Committed', required=True, default=0.0)
    # picking_id = fields.Many2one('stock.picking', 'Picking', ondelete='cascade', index=True)
    stock_move_ids = fields.Many2many('stock.move', 
        'account_anayltic_line_stock_move_rel',
        'stock_move_id', 'analytic_line_id', 
        string='Moves', ondelete='cascade', index=True)
    
    