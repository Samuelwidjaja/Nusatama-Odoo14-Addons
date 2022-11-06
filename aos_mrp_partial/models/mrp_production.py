from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    post_history_ids = fields.One2many('mrp.production.post.history', 'production_id')


    show_post_inventory_button = fields.Boolean(compute="_compute_show_post_inventory_button")

    @api.depends('state','lot_producing_id','qty_producing')
    def _compute_show_post_inventory_button(self):
        for rec in self:
            # FIXME: TODO
            rec.show_post_inventory_button = True

    def _post_inventory(self, cancel_backorder=False):
        return super()._post_inventory()

    def _register_post_history(self):
        self.ensure_one()
        done_qty = self.qty_producing - self.qty_produced
        if not done_qty:
            raise UserError("Try to post 0 inventory!")
        self.write({
            'post_history_ids': [(0,0,{
                'lot_id': self.lot_producing_id.id,
                'done_qty': done_qty, #FIXME
            })]
        })

    def _cleanup_after_post_history(self):
        self.lot_producing_id = False

    def post_inventory(self):
        self._register_post_history()
        res = self._post_inventory()
        self._cleanup_after_post_history()

        