from odoo import models

class StockRule(models.Model):
    _inherit = "stock.rule"

    def _prepare_mo_vals(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values, bom):
        res = super(StockRule,self)._prepare_mo_vals(product_id, product_qty, product_uom, location_id, name, origin, company_id, values, bom)
        try:
            res.update({'partner_id':values.get('group_id',self.env['procurement.group']).sale_id.partner_id.id})
            return res
        except Exception:
            return res