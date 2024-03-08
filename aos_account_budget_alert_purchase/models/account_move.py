# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools import ustr
from odoo.exceptions import UserError
# committed_analytic_line_ids

class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_budget_alert_info(self):
        if any(self.invoice_line_ids.mapped('purchase_line_id')):
            self.has_budget_alert_warn = self.invoice_line_ids.mapped('purchase_line_id').order_id.has_budget_alert_warn
            self.has_budget_alert_stop = self.invoice_line_ids.mapped('purchase_line_id').order_id.has_budget_alert_stop
            self.budget_alert_info = self.invoice_line_ids.mapped('purchase_line_id').order_id.budget_alert_info
        else:
            return super(AccountMove, self)._get_budget_alert_info()

    @api.model_create_multi
    def create(self, vals_list):
        res_ids = super(AccountMove, self).create(vals_list)
        mlines = res_ids.line_ids.filtered(lambda ml: ml.analytic_account_id.budget_line and not ml.committed_analytic_line_ids and ml.purchase_line_id.committed_analytic_line_ids)
        alines = mlines.mapped('purchase_line_id').mapped('committed_analytic_line_ids')
        mlines.committed_analytic_line_ids = [(6, 0, alines.ids)]
        return res_ids

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    def auth_create_analytic_lines(self):
        """ Create analytic items upon validation of an account.move.line having an analytic account. This
            method first remove any existing analytic item related to the line before creating any new one.
            __aos_account_budget_alert_purchase__
        """
        for obj_line in self:
            amount = (obj_line.credit or 0.0) - (obj_line.debit or 0.0)
            amount_practical = obj_line.company_currency_id.with_context(date=obj_line.date or fields.Date.context_today(obj_line)).compute(amount, obj_line.analytic_account_id.currency_id) if obj_line.analytic_account_id.currency_id else amount
            if obj_line.purchase_line_id.committed_analytic_line_ids and obj_line.analytic_account_id:
                #obj_line.purchase_line_id.committed_analytic_line_ids.invoice_id = obj_line.move_id.id
                obj_line.purchase_line_id.committed_analytic_line_ids.invoice_line_ids = [(6, 0, obj_line.ids)]
                #obj_line.committed_analytic_line_ids.committed_amount = obj_line.price_subtotal if obj_line.move_id.move_type in ('out_invoice', 'in_refund') else -obj_line.price_subtotal
                #obj_line.purchase_line_id.committed_analytic_line_ids.committed_account_id = obj_line.account_id.id
                #obj_line.purchase_line_id.committed_analytic_line_ids.account_id = obj_line.analytic_account_id.id
                #obj_line.committed_analytic_line_ids.product_id = obj_line.product_id.id
                #obj_line.committed_analytic_line_ids.unit_amount = obj_line.quantity
            #print ('=====auth_create_analytic_lines11====',obj_line.move_id.state,obj_line.committed_analytic_line_ids,amount_practical,obj_line.committed_analytic_line_ids.amount,obj_line.committed_analytic_line_ids.committed_amount)
            #print ('---auth_create_analytic_lines22---',obj_line.committed_analytic_line_ids,self._context.get('picking_id'),self._context.get('move_lines'))
            #print ('----auth_create_analytic_lines33-----',obj_line.purchase_line_id.committed_analytic_line_ids, obj_line.analytic_account_id)
            if obj_line.committed_analytic_line_ids and obj_line.analytic_account_id:
                obj_line.committed_analytic_line_ids.committed_account_id = obj_line.account_id.id
                obj_line.committed_analytic_line_ids.account_id = obj_line.analytic_account_id.id
                obj_line.committed_analytic_line_ids.product_id = obj_line.product_id.id
                if obj_line.move_id.state == 'draft':
                    #print ('---draft---',obj_line.committed_analytic_line_ids,'commited',obj_line.committed_analytic_line_ids.committed_amount,'amount',obj_line.committed_analytic_line_ids.amount,'practical',amount_practical)
                    obj_line.committed_analytic_line_ids.unit_amount = \
                        obj_line.committed_analytic_line_ids.filtered(lambda al: al.product_id == obj_line.product_id).unit_amount \
                            - obj_line.quantity if obj_line.move_id.move_type in ('in_invoice', 'out_refund') else -obj_line.quantity
                    obj_line.committed_analytic_line_ids.filtered(lambda al: al.product_id == obj_line.product_id).committed_amount = obj_line.committed_analytic_line_ids.filtered(lambda al: al.product_id == obj_line.product_id).committed_amount + amount_practical if obj_line.move_id.move_type in ('in_invoice', 'out_refund') else -amount_practical
                    obj_line.committed_analytic_line_ids.filtered(lambda al: al.product_id == obj_line.product_id).amount = obj_line.committed_analytic_line_ids.filtered(lambda al: al.product_id == obj_line.product_id).amount - amount_practical if obj_line.move_id.move_type in ('in_invoice', 'out_refund') else amount_practical
                    # obj_line.committed_analytic_line_ids.unit_amount = obj_line.committed_analytic_line_ids.unit_amount - obj_line.quantity if obj_line.move_id.move_type in ('in_invoice', 'out_refund') else -obj_line.quantity
                    # obj_line.committed_analytic_line_ids.committed_amount = obj_line.committed_analytic_line_ids.committed_amount + amount_practical if obj_line.move_id.move_type in ('in_invoice', 'out_refund') else -amount_practical
                    # obj_line.committed_analytic_line_ids.amount = obj_line.committed_analytic_line_ids.amount - amount_practical if obj_line.move_id.move_type in ('in_invoice', 'out_refund') else amount_practical
                    #obj_line.committed_analytic_line_ids.move_id = False
                # elif obj_line.move_id.state == 'posted':
                #     print ('---posted---',obj_line.committed_analytic_line_ids.unit_amount,obj_line.committed_analytic_line_ids.committed_amount,obj_line.committed_analytic_line_ids.amount,amount_practical if obj_line.debit else amount_practical)
                #     obj_line.committed_analytic_line_ids.unit_amount = obj_line.committed_analytic_line_ids.unit_amount + obj_line.quantity if obj_line.move_id.move_type in ('in_invoice', 'out_refund') else obj_line.quantity
                #     obj_line.committed_analytic_line_ids.committed_amount = (obj_line.committed_analytic_line_ids.committed_amount - amount_practical) if not self._context.get('picking_budget') else 0
                #     obj_line.committed_analytic_line_ids.amount = obj_line.committed_analytic_line_ids.amount + amount_practical
                #     obj_line.committed_analytic_line_ids.move_id = obj_line.move_id.id,
                if self._context.get('picking_id'):
                    obj_line.committed_analytic_line_ids.picking_id = self._context.get('picking_id').id
                    obj_line.committed_analytic_line_ids.stock_move_id = self._context.get('move_lines').filtered(lambda ml: ml.product_id == obj_line.product_id and ml.quantity_done == abs(obj_line.quantity))
            elif not obj_line.committed_analytic_line_ids and obj_line.analytic_account_id:
                vals_line = obj_line._auth_prepare_analytic_line()
                self.env['account.analytic.line'].create(vals_line)
            
            
    def _auth_prepare_analytic_line(self):
        """ Prepare the values used to create() an account.analytic.line upon validation of an account.move.line having
            an analytic account. This method is intended to be extended in other modules.
        """
        values_list = super(AccountMoveLine, self)._auth_prepare_analytic_line()
        #print ('==_auth_prepare_analytic_line=',values_list)
        for values in values_list:
            #print ('--values--',values,values.get('invoice_line_id'))
            move_line = self.browse(values.get('invoice_line_id'))
            committed_amount = move_line.purchase_line_id.price_subtotal if move_line.move_id.move_type in ('out_invoice', 'in_refund') else -move_line.purchase_line_id.price_subtotal
            values.update({
                #'purchase_id': move_line.purchase_line_id.order_id.id if move_line.purchase_line_id and not values.get('purchase_line_id') else False,
                'purchase_line_id': move_line.purchase_line_id.id if move_line.purchase_line_id and not values.get('purchase_line_id') else False,
                'committed_amount': move_line.company_currency_id.with_context(date=move_line.move_id.invoice_date or fields.Date.context_today(move_line)).compute(committed_amount, move_line.analytic_account_id.currency_id) if move_line.analytic_account_id.currency_id else committed_amount,
            })
        return values_list
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

    def create_analytic_lines(self):
        """ Create analytic items upon validation of an account.move.line having an analytic account. This
            method first remove any existing analytic item related to the line before creating any new one.
        """
        #DON'T DELETE ANALYTIC LINE JUST UPDATE AMOUNT AND MOVE LINE ID
        #self.mapped('invoice_id').mapped('analytic_invoice_line_ids')
        #self.mapped('analytic_line_ids').unlink()
        print ('==create_analytic_lines purchase==',self.mapped('move_id').mapped('line_ids').mapped('committed_analytic_line_ids'))
        if self.mapped('move_id').mapped('line_ids').mapped('committed_analytic_line_ids'):
            for obj_line in self.mapped('move_id').mapped('line_ids').mapped('committed_analytic_line_ids'):
                move_line = self.filtered(lambda x: x.product_id == obj_line.product_id and x.analytic_account_id == obj_line.account_id and x.account_id == obj_line.committed_account_id)#(x.account_id == obj_line.committed_account_id or x.purchase_line_id == obj_line.purchase_line_id))
                if ((not move_line.move_id.has_budget_alert_warn and not move_line.move_id.has_budget_alert_stop) or self._context.get('action_budget')) and obj_line.account_id == move_line.analytic_account_id:# and obj_line.unit_amount == move_line.quantity:
                    vals_line = move_line._auth_update_analytic_line(obj_line)
                    obj_line.write(vals_line)
        else:
            #self.mapped('analytic_line_ids').unlink()
            for obj_line in self:
                if obj_line.analytic_account_id:
                    vals_line = obj_line._prepare_analytic_line()
                    self.env['account.analytic.line'].create(vals_line)
