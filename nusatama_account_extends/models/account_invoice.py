from odoo import models,fields,api

class AccountInvoice(models.Model):
    _inherit='account.move'

    no_faktur = fields.Char(string='No Faktur')
    open_date = fields.Date(string='Date By Validate')

    def set_open_date(self):
        self.write({'open_date': fields.Date.today()})

    def action_invoice_open(self):
        res = super(AccountInvoice,self).action_invoice_open()
        self.set_open_date()
        return res