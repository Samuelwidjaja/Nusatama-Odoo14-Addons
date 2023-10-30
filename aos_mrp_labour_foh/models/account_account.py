from odoo import models,fields

class AccountAccount(models.Model):
    _inherit = "account.account"
    
    default_account_labour = fields.Boolean(string="Defaut Account Labour")
    default_account_foh = fields.Boolean(string="Default Account FOH")