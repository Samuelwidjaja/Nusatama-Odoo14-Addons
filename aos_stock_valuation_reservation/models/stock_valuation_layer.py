from odoo import fields, models, api


class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'
    

    reserved_qty = fields.Float(compute='_compute_reserved_qty', store=True, inverse=lambda self:True)
    reservation_line_ids = fields.One2many('stock.valuation.layer.reservation', 'valuation_layer_id')

    @api.depends('reservation_line_ids.qty')
    def _compute_reserved_qty(self):
        for rec in self:
            rec.reserved_qty = rec.reservation_line_ids.mapped('qty')