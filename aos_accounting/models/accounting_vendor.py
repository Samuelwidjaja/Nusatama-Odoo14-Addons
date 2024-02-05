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
    
    
    #override method
    @api.depends('product_id', 'account_id', 'partner_id', 'date')
    def _compute_analytic_account_id(self):
        for record in self:
            if not record.exclude_from_invoice_tab or not record.move_id.is_invoice(include_receipts=True):
                if record.account_id.user_type_id.internal_group == 'expense':
                    continue
                rec = self.env['account.analytic.default'].account_get(
                    product_id=record.product_id.id,
                    partner_id=record.partner_id.commercial_partner_id.id or record.move_id.partner_id.commercial_partner_id.id,
                    account_id=record.account_id.id,
                    user_id=record.env.uid,
                    date=record.date,
                    company_id=record.move_id.company_id.id
                )
                if rec:
                    record.analytic_account_id = rec.analytic_id

# class AccountAnalyticDefault(models.Model):
#     _inherit = "account.analytic.default"
    
#     # inherit existing method
#     # do not add analytic account if account type is expense
#     @api.model
#     def account_get(self, product_id=None, partner_id=None, account_id=None, user_id=None, date=None, company_id=None):
#         # account_type_id = self.env.ref('account.data_account_type_expenses', raise_if_not_found=False)
        
#         account = self.env['account.account'].browse(account_id)
#         if account.user_type_id.internal_group == 'expense':
#             return self.env['account.analytic.default']

#         return super(AccountAnalyticDefault, self).account_get(product_id, partner_id, account_id, user_id, date, company_id)