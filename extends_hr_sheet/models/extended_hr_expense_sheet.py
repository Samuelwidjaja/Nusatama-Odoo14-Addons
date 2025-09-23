from odoo import models, fields

class ExtendedHRExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    no_rekening = fields.Char(string='Ditransfer ke')
