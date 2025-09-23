from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # New field for 11/12 calculation with currency
    eleven_twelve_untaxed_amount_sales = fields.Monetary(
        string="11/12 Untaxed Amount",
        compute="_compute_eleven_twelve_untaxed_amount",
        store=True,
        currency_field='currency_id',
        help="This field shows 11/12 of the untaxed amount with the associated currency."
    )

    @api.depends('amount_untaxed')
    def _compute_eleven_twelve_untaxed_amount(self):
        for order in self:
            order.eleven_twelve_untaxed_amount_sales = order.amount_untaxed * (11 / 12)
