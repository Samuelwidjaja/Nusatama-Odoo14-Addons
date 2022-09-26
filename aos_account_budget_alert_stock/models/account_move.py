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
    
    # def _auth_prepare_analytic_line(self):
    #     """ Prepare the values used to create() an account.analytic.line upon validation of an account.move.line having
    #         an analytic account. This method is intended to be extended in other modules.
    #     """
    #     values_list = super(AccountMoveLine, self)._auth_prepare_analytic_line()
    #     #print ('==_auth_prepare_analytic_line=',values_list)
    #     for values in values_list:
    #         move_line = self.browse(values.get('invoice_line_ids')[0][2])
    #         stock_move = move_line.mapped('move_id').mapped('stock_move_id')
    #         values.update({
    #             'stock_move_ids': [(6, 0, stock_move.ids)]
    #         })
    #     return values_list
        # result = []
        # for move_line in self:
        #     amount = 0.0
        #     committed_amount = move_line.price_subtotal if move_line.move_id.move_type in ('out_invoice', 'in_refund') else -move_line.price_subtotal
        #     #amount = (move_line.credit or 0.0) - (move_line.debit or 0.0)
        #     #default_name = move_line.name or (move_line.ref or '/' + ' -- ' + (move_line.partner_id and move_line.partner_id.name or '/'))
        #     result.append({
        #         'name': move_line.name,
        #         'date': move_line.move_id.date,
        #         'account_id': move_line.analytic_account_id.id,
        #         'tag_ids': [(6, 0, move_line.analytic_tag_ids.ids)],
        #         'unit_amount': 0,#move_line.quantity,
        #         'product_id': move_line.product_id and move_line.product_id.id or False,
        #         'product_uom_id': move_line.product_uom_id and move_line.product_uom_id.id or False,
        #         'committed_amount': move_line.company_currency_id.with_context(date=move_line.move_id.invoice_date or fields.Date.context_today(move_line)).compute(committed_amount, move_line.analytic_account_id.currency_id) if move_line.analytic_account_id.currency_id else committed_amount,
        #         'amount': move_line.company_currency_id.with_context(date=move_line.move_id.invoice_date or fields.Date.context_today(move_line)).compute(amount, move_line.analytic_account_id.currency_id) if move_line.analytic_account_id.currency_id else amount,
        #         'ref': move_line.move_id.ref or False,
        #         'invoice_id': move_line.move_id.id,
        #         'invoice_line_id': move_line.id,
        #         'committed_account_id': move_line.account_id.id,
        #         'move_id': False,
        #         'user_id': move_line.move_id.user_id.id or move_line._uid,
        #     })
        # return result