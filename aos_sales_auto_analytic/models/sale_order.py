from odoo import fields, models, api, _ , SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"
    customer_reference = fields.Char()
    
    def action_confirm(self):
        result = super(SaleOrder, self).action_confirm()
        if not self.analytic_account_id:
            self._saleorder_analytic_account_value()
        return result
        
    def _saleorder_analytic_account_value(self):  
        result = {}        
        new_analytic= self.env["account.analytic.account"].with_user(SUPERUSER_ID).create({
            "name" : "%s" % self.name,
            "partner_id" : self.partner_id.id
        })
        self.write({"analytic_account_id":  new_analytic.id})
        result[self.id] = new_analytic
        return result
        
    
    
        