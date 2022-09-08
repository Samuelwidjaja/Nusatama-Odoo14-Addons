"""
- sale.message
"""
from odoo import models, fields


class SaleMessage(models.TransientModel):
    _name = 'sale.message'
    _description = "Sale module message info."

    message = fields.Text(string="Message")

    def action_set_dir_approved(self):
        active_ids = self._context.get('active_ids', [])
        sale = self.env['sale.order'].browse(active_ids)
        if sale:
            sale.state = 'dir_approved'
            sale.notes = self.message
        
    def action_reject(self):
        active_ids = self._context.get('active_ids', [])
        sale = self.env['sale.order'].browse(active_ids)
        if sale:
            sale.state = 'cancel'
            sale.rejected_reason = self.message
