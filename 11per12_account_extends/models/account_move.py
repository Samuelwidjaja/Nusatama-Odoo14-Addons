from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    eleven_twelve_untaxed_amount = fields.Monetary(
        string="11/12 Untaxed Amount",
        compute="_compute_eleven_twelve_untaxed_amount",
        store=True,
        currency_field='currency_id',
        help="This field shows 11/12 of the untaxed amount with the associated currency."
    )

    @api.depends('amount_untaxed')
    def _compute_eleven_twelve_untaxed_amount(self):
        for move in self:
            move.eleven_twelve_untaxed_amount = move.amount_untaxed * (11 / 12)
