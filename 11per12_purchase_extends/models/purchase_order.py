from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # Make sure 'currency_id' exists and is linked to the correct currency.
    eleven_twelve_untaxed_amount = fields.Monetary(
        string="11/12 Untaxed Amount",
        compute="_compute_eleven_twelve_untaxed_amount",
        store=True,
        currency_field='currency_id'  # Make sure the 'currency_id' exists
    )

    @api.depends('amount_untaxed')
    def _compute_eleven_twelve_untaxed_amount(self):
        for order in self:
            order.eleven_twelve_untaxed_amount = (11 / 12) * order.amount_untaxed

