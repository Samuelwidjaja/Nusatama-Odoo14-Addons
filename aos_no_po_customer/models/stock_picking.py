"""
- stock.picking
"""
from odoo import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    no_po = fields.Char(related='sale_id.no_po', string="No Pesanan", store=True)
