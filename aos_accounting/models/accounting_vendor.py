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
    
    
    # 

class AccountAnalyticDefault(models.Model):
    _inherit = "account.analytic.default"
    
    # inherit existing method
    # do not add analytic account if account type is expense
    @api.model
    def account_get(self, product_id=None, partner_id=None, account_id=None, user_id=None, date=None, company_id=None):
        account_type_id = self.env.ref('account.data_account_type_expenses', raise_if_not_found=False)
        
        account = self.env['account.account'].browse(account_id)
        if account.user_type_id.id == account_type_id.id:
            return self.env['account.analytic.default']

        return super(AccountAnalyticDefault, self).account_get(product_id, partner_id, account_id, user_id, date, company_id)