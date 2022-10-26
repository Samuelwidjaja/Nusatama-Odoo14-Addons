from odoo import models,api,fields

class WarningInvoice(models.TransientModel):
    _name = "warning.invoice"
    _description = "Warning Invoice Not Paid"

    production_id = fields.Many2one('mrp.production',string="Related Mrp Production",readonly=True)
    invoices = fields.Many2many('account.move',string="Related Invoices",readonly=True)
    invoices_text = fields.Text(string="Invoices Reference",readonly=True)

    def action_confirm(self):
        self.production_id.sudo().update({'state':'on_hold'})