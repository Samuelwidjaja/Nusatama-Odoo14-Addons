# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools import ustr
from odoo.exceptions import UserError

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _prepare_analytic_line(self):
        """ Note: This method is called only on the move.line that having an analytic account, and
            so that should create analytic entries.
        """
        values_list = super(AccountMoveLine, self)._prepare_analytic_line()
        print ('===values====',values_list)
        for values in values_list:
            move_line = self.browse(values.get('move_id'))
            stock_move = move_line.mapped('move_id').mapped('stock_move_id')
            values.update({
                'stock_move_ids': [(6, 0, stock_move.ids)],
                'invoice_line_ids': [(6, 0, move_line.ids)],
            })
        return values_list
    