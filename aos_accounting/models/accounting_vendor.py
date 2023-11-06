from odoo import fields, models, api, _ , SUPERUSER_ID
from odoo.exceptions import UserError

class AccountingVendor(models.Model):
    _inherit = "account.move"

    mrp_id = fields.Char(string="MO ID " ,related="stock_move_id.origin")
    
    def action_post(self):
        if (self.ref == False or self.ref == '') and self.move_type == 'in_invoice':
            raise UserError("Field Bill Reference Harus Diisi, Mohon Isi Dengan No Tagihan Supplier")
        return super(AccountingVendor, self).action_post()
    

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    mrp_id = fields.Char(string="MO ID " ,related="move_id.mrp_id")
    
