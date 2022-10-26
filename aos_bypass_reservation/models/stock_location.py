from odoo import models,fields,api


class StockLocation(models.Model):
    _inherit = "stock.location"


    bypass_reservation = fields.Boolean('Bypass Reservation', compute="_compute_bypass_reservation", store=True, inverse=lambda self:True)

    @api.depends('usage','scrap_location')
    def _compute_bypass_reservation(self):
        for rec in self:
            rec.bypass_reservation = rec.with_context(compute_origin_bypass_reservation=1).should_bypass_reservation()



    def should_bypass_reservation(self):
        fs = dict(self._fields)
        ctx_origin = self._context.get('compute_origin_bypass_reservation')
        if fs.get('bypass_reservation') and not ctx_origin:
            return self.bypass_reservation
        return super(StockLocation, self).should_bypass_reservation()
        