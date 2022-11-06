from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class MrpProductionPostHistory(models.Model):
    _name = 'mrp.production.post.history'

    _description = 'Mrp Production Post History'
    
    production_id = fields.Many2one('mrp.production', ondelete="cascade")
    done_qty = fields.Float()
    lot_id = fields.Many2one('stock.production.lot', ondelete="set null")

