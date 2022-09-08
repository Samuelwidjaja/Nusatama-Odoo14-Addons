from odoo import fields, models, api, _ , SUPERUSER_ID
from odoo.exceptions import UserError

class AccountingVendor(models.Model):
    _inherit = "account.move"
    
    def action_post(self):
        super(AccountingVendor, self).action_post()
        if self.ref == False:
            raise UserError("Field Bill Reference Harus Diisi, Mohon Isi Dengan No Tagihan Supplier")