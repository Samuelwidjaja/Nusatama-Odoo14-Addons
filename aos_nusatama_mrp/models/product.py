from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
    _inherit = 'product.product'


    def _prepare_in_svl_vals_wip(self,quantity, unit_cost):
        company_id = self.env.context.get('force_company', self.env.company.id)
        company = self.env['res.company'].browse(company_id)
        vals = {
            'product_id': self.id,
            'value': company.currency_id.round(unit_cost),
            'unit_cost': company.currency_id.round(unit_cost/quantity),
            'quantity': quantity,
        }
        if self.cost_method in ('average', 'fifo'):
            vals['remaining_qty'] = quantity
            vals['remaining_value'] = vals['value']
        return vals

    def _prepare_in_svl_vals(self, quantity, unit_cost):
        self.ensure_one()
        if self._context.get('button_mark_done_production_ids') and self._context.get('moves_todo'):
            return self._prepare_in_svl_vals_wip(quantity=quantity, unit_cost=unit_cost)
        
        res = super()._prepare_in_svl_vals(quantity=quantity, unit_cost=unit_cost)
        return res