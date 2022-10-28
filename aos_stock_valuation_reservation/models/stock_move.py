from odoo import fields, models, api


class StockMove(models.Model):
    _inherit = 'stock.move'


    reserved_valuation_ids = fields.One2many('stock.valuation.layer.reservation', 'stock_move_id')
    reserved_valuation_qty = fields.Float(compute='_compute_reserved_valuation_qty')
    
    @api.depends('reserved_valuation_ids.qty')
    def _compute_reserved_valuation_qty(self):
        for rec in self:
            rec.reserved_valuation_qty = rec.reserved_valuation_ids.mapped('qty')
    
    def reserve_valuation(self):
        pass