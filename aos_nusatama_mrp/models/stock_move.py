from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_round
import logging
_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'


    move_raw_origin_ids = fields.Many2many('stock.move', 'stock_move_raw_origin_rel', 'stock_move_id', 'raw_origin_id', string="Raw Source", copy=False)
    move_raw_dest_ids = fields.Many2many('stock.move', 'stock_move_raw_origin_rel', 'raw_origin_id', 'stock_move_id', string="Raw Dest", copy=False)



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

    def _action_done(self, cancel_backorder=False):
        res = super()._action_done(cancel_backorder=cancel_backorder)
        production_usage = any(self.move_dest_ids.mapped(lambda r:r.raw_material_production_id.id))
        if production_usage:
            for rec in self:
                rec._assign_to_destination_as_raw_origin()
        return res

    def _prepare_move_split_vals(self, qty):
        res = super()._prepare_move_split_vals(qty)
        # move_orig_ids = self.move_orig_ids.filtered(lambda r:r.state!='done') if self.move_orig_ids.filtered(lambda r:r.state!='done') else self.move_orig_ids
        res.update({
            'move_raw_dest_ids': []
        })
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

    def _get_price_unit(self):
        precision = self.env["decimal.precision"].precision_get("Product Price")
        res = super()._get_price_unit()
        moves_todo = self._context.get('moves_todo')
        if len(self) == 1 and self.production_id and self.product_id == self.production_id.product_id and self.location_id.usage=='production' and moves_todo:
            # valuation porduction is calculated from consumed unit price valuation
            # print(res)
            order_moves = moves_todo.get(self.production_id.id)
            totalvalues = abs(sum(order_moves.move_raw_origin_ids.filtered(lambda r:r.state=='done').stock_valuation_layer_ids.mapped('value')))
            res = float_round((totalvalues / self.quantity_done), precision_digits=precision) # price per unit
            # print(order_moves)


            
            
        return res