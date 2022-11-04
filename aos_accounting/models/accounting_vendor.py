from odoo import fields, models, api, _ , SUPERUSER_ID
from odoo.exceptions import UserError

class AccountingVendor(models.Model):
    _inherit = "account.move"
    
    def action_post(self):
        if (self.ref == False or self.ref == '') and self.move_type == 'in_invoice':
            raise UserError("Field Bill Reference Harus Diisi, Mohon Isi Dengan No Tagihan Supplier")
        return super(AccountingVendor, self).action_post()
        