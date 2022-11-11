from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_round
import logging
_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'


    move_raw_origin_ids = fields.Many2many('stock.move', 'stock_move_raw_origin_rel', 'stock_move_id', 'raw_origin_id', string="Raw Source", copy=False)
    move_raw_dest_ids = fields.Many2many('stock.move', 'stock_move_raw_origin_rel', 'raw_origin_id', 'stock_move_id', string="Raw Dest", copy=False)
    consumed_raw_qty = fields.Float(compute="_compute_consumed_raw_qty")
    to_consume_raw_qty = fields.Float(compute="_compute_consumed_raw_qty")

    @api.depends('move_raw_dest_ids.quantity_done')
    def _compute_consumed_raw_qty(self):
        """Internal Transfer move -> Production move
            calculated on destination move how many qty already done in production -> move_raw_ids
        """
        for rec in self:
            consumed = 0
            to_consume = 0
            if rec.move_raw_dest_ids:
                consumed = sum(rec.move_raw_dest_ids.filtered(lambda r:r.state=='done').mapped('quantity_done'))
                to_consume = sum(rec.mapped('quantity_done')) - consumed

            rec.update({
                'consumed_raw_qty':consumed,
                'to_consume_raw_qty':to_consume,
            })


    # get origin
    # def _calc_move_raw_origin_ids(self):
    #     for rec in self:
    #         origs = rec.move_orig_ids.filtered(lambda r:not r.move_raw_dest_ids)
    #         rec.write({'move_raw_origin_ids':[(6,0,origs.filtered(lambda r:r.state=='done').ids)]})

    def _assign_to_destination_as_raw_origin(self):
        self.ensure_one()
        # self = internal
        # self.move_dest_ids => production
        
        self.move_dest_ids.filtered(lambda r:r.state not in ('done','cancel')).write({'move_raw_origin_ids':[(4,self.id)]})

    def _assign_move_raw_origin_to_consume(self):
        production_raw = self.filtered(lambda r:r.raw_material_production_id)
        if production_raw:
            if self.raw_material_production_id.qty_produced<self.raw_material_production_id.product_qty:
                # if backorder
                next_backorder_moves = self.move_raw_origin_ids.move_dest_ids.filtered(lambda r:r.state not in ('done','cancel'))
                # next_backorder_production = next_backorder_moves.raw_material_production_id
                for rec in self.filtered(lambda r:sum(r.move_orig_ids.mapped('to_consume_raw_qty'))>0.0):
                    target_move = next_backorder_moves.filtered(lambda r:r.move_orig_ids in self[0].move_orig_ids)
                    orig_to_assign = rec.move_orig_ids.filtered(lambda r:r.to_consume_raw_qty>0.0)
                    for m in orig_to_assign:
                        target_move.write({'move_raw_origin_ids':[(4,m.id)]})

    def _action_done(self, cancel_backorder=False):
        res = super()._action_done(cancel_backorder=cancel_backorder)
        production_usage = any(self.move_dest_ids.mapped(lambda r:r.raw_material_production_id.id))
        if production_usage:
            for rec in self:
                rec._assign_to_destination_as_raw_origin()
        self._assign_move_raw_origin_to_consume()

        return res

    def _prepare_move_split_vals(self, qty):
        res = super()._prepare_move_split_vals(qty)
        # move_orig_ids = self.move_orig_ids.filtered(lambda r:r.state!='done') if self.move_orig_ids.filtered(lambda r:r.state!='done') else self.move_orig_ids
        res.update({
            'move_raw_dest_ids': []
        })
        return res

    def _get_price_unit(self):
        precision = self.env["decimal.precision"].precision_get("Product Price")
        res = super()._get_price_unit()
        moves_todo = self._context.get('moves_todo')
        if len(self) == 1 and self.production_id and self.product_id == self.production_id.product_id and self.location_id.usage=='production' and moves_todo:
            # valuation porduction is calculated from consumed unit price valuation
            # print(res)
            order_moves = moves_todo.get(self.production_id.id)
            res = 0
            for move in order_moves:
                totalvalues = 0
                for valuation in move.move_raw_origin_ids.filtered(lambda r:r.state=='done'):
                    totalvalues = abs(valuation.stock_valuation_layer_ids.unit_cost * move.quantity_done)

                res += float_round((totalvalues), precision_digits=precision) # price per unit
            # print(order_moves)
        return res

    def _create_in_svl_mo(self, forced_quantity=None):
        """Create a `stock.valuation.layer` from `self`.

        :param forced_quantity: under some circunstances, the quantity to value is different than
            the initial demand of the move (Default value = None)
        """
        svl_vals_list = []
        for move in self:
            move = move.with_company(move.company_id)
            valued_move_lines = move._get_in_move_lines()
            valued_quantity = 0
            for valued_move_line in valued_move_lines:
                valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done, move.product_id.uom_id)
            unit_cost = abs(move._get_price_unit())  # May be negative (i.e. decrease an out move).
            svl_vals = move.product_id._prepare_in_svl_vals(forced_quantity or valued_quantity, unit_cost)
            svl_vals.update(move._prepare_common_svl_vals())
            if forced_quantity:
                svl_vals['description'] = 'Correction of %s (modification of past move)' % move.picking_id.name or move.name
            svl_vals_list.append(svl_vals)
        return self.env['stock.valuation.layer'].sudo().create(svl_vals_list)

    def _create_in_svl(self, forced_quantity=None):
        production = all(self.mapped(lambda r:r.production_id.id))
        if production:
            return self._create_in_svl_mo()
        else:
            return super()._create_in_svl(forced_quantity=forced_quantity)