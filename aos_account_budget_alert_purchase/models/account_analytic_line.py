# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    
    # committed_account_id = fields.Many2one('account.account', string='Committed Account')
    # committed_amount = fields.Monetary('Committed', required=True, default=0.0)
    # purchase_id = fields.Many2one('purchase.order', 'Purchase', ondelete='cascade', index=True)
    purchase_line_id = fields.Many2one('purchase.order.line', 'Purchase Line', ondelete='restrict', index=True)
    # purchase_line_ids = fields.Many2many('purchase.order.line', 
    #         'account_anayltic_line_purchase_line_rel',
    #         'analytic_line_id', 'purchase_line_id',
    #         string='Purchase Line', ondelete='cascade', index=True)


    def unlink(self):
        # OVERRIDE to unlink the inherited account.move (move_id field) as well.
        #analytic_lines = self.with_context(force_delete=True)
        #res = super(AccountAnalyticLine, self).unlink()
        if not self.with_context(force_delete=True).purchase_line_id:
            #analytic_lines.unlink()
            return super(AccountAnalyticLine, self).unlink()
    
    