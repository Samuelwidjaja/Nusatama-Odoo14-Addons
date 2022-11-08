from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
    _inherit = 'product.product'


    def _prepare_in_svl_vals(self, quantity, unit_cost):
        res = super()._prepare_in_svl_vals(quantity=quantity, unit_cost=unit_cost)
        return res