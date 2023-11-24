from odoo import models, fields
from . import float_to_hour

class MRPWorkder(models.Model):
    _inherit = "mrp.workorder"
    
    
    duration_hour = fields.Float(string="Duration Hour")
    
    def button_finish(self):
        res = super(MRPWorkder, self).button_finish()
        self.duration_hour = float_to_hour(self.duration)
        return res