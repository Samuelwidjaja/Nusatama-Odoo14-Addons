from odoo import models,fields,api,_
import re
from odoo.exceptions import UserError
class ConfigFilter(models.Model):
    _name = "config.filter"
    _description = "Configuration Filter"

    name = fields.Char(string="Name",required=True)
    type = fields.Selection([('monthly','Monthly'),('yearly','Yearly'),('quarter','Quarter')],string="Type Filter",default="monthly",required=True)
    month_int = fields.Integer(string="Month In Integer")
    months = fields.One2many('config.filter.line','config_filter_id',string="Lines")
    quarter_sequence = fields.Integer(string="Quarter Sequence",help="How to describe Quarter Sequence")
    year_int = fields.Integer(string="Year In Integer")
    @api.onchange("type")
    def onchange_type(self):
        vals = []
        self.months = [(5,0)]
        if self.type == 'yearly':
            for line in self.search([('type','=','monthly')]):
                vals.append((0,0,{'month':line.id}))
        self.months = vals

    @api.constrains('type','name')
    def constrain_name(self):
        pattern = r"[1-3][0-9]{3}"
        if self.type == 'yearly':
            if not re.match(pattern,self.name):
                raise UserError("Year %s cannot contain Alphabet if type = %s" % (self.name,self.type))
    
    @api.model
    def create(self,vals):
        if vals.get('type') == 'yearly':
            vals.update({'year_int': int(vals.get('name'))})
        return super(ConfigFilter,self).create(vals)
class ConfigFilterLine(models.Model):
    _name = "config.filter.line"

    
    config_filter_id = fields.Many2one('config.filter',string="Parent",readonly=True)
    month = fields.Many2one('config.filter',string="Month",domain=[('type','=','monthly')])
    month_int = fields.Integer(related="month.month_int",string="Month In Integer")
    type = fields.Selection(related="month.type",string="Type Filter")