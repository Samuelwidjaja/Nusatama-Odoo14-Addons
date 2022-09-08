"""
- account.move
"""
from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    sale_id = fields.Many2one('sale.order', compute='_compute_sale_order')
    no_po = fields.Char(string="No Pesanan", related='sale_id.no_po', store=True)

    @api.depends('move_type', 'invoice_origin')
    def _compute_sale_order(self):
        """ Compute sale_id based from type == 'out_invoice' and invoice_origin """
        for move in self:
            move.sale_id = False
            if move.move_type == 'out_invoice' and move.invoice_origin:
                move.sale_id = self.env['sale.order'].search([('name', '=', move.invoice_origin)], limit=1)
