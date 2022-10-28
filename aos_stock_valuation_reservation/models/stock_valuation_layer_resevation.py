import re
from odoo import fields, models


class StockValuationLayerReservation(models.Model):
    _name = 'stock.valuation.layer.reservation'
    _description = 'Stock Valuation Layer Reservation'


    stock_move_id = fields.Many2one('stock.move', required=True)
    stock_move_line_id = fields.Many2one('stock.move.line')
    valuation_layer_id = fields.Many2one('stock.valuation.layer', required=True)
    qty = fields.Float()
    