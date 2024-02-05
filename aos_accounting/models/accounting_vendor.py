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
    
    
    @api.model_create_multi
    def create(self, vals_list):
        # if line ids has account type expense and has analytic set to false
        # trigger when create from ui
        # just for invoice and cause for invoice we need context move_type from action or using with_context
        invoice_type = self.env.context.get('default_move_type') or self.env.context.get('move_type') or False
        if invoice_type and invoice_type in ('out_invoice', 'out_refund'):
            for vals in vals_list:
                account = self.env['account.account'].browse(vals.get('account_id', []))
                if account.user_type_id.internal_group == 'expense' and vals.get('analytic_account_id', False):
                    vals['analytic_account_id'] = False
        return super(AccountMoveLine, self).create(vals_list)