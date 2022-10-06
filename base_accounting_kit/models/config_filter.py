from odoo import models,fields,api,_


class ConfigFilter(models.Model):
    _name = "config.filter"
    _description = "Configuration Filter"

    name = fields.Char(string="Name",required=True)
    type = fields.Selection([('monthly','Monthly'),('yearly','Yearly'),('quarter','Quarter')],string="Type Filter",default="monthly",required=True)
    month_int = fields.Integer(string="Month In Integer")
    months = fields.One2many('config.filter.line','config_filter_id',string="Lines")

class ConfigFilterLine(models.Model):
    _name = "config.filter.line"

    
    config_filter_id = fields.Many2one('config.filter',string="Parent",readonly=True)
    month = fields.Many2one('config.filter',string="Month",domain=[('type','=','monthly')])
    month_int = fields.Integer(related="month.month_int",string="Month In Integer")
    type = fields.Selection(related="month.type",string="Type Filter")