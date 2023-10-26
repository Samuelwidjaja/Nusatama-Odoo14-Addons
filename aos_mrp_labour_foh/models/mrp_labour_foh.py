from odoo import models,fields, api,_
from odoo.exceptions import UserError
from datetime import datetime

class MRPLabourFOH(models.Model):
    _name = "mrp.labour.foh"
    _description = "MRP Labour & FOH"
    _order = "id desc"
    
    name = fields.Char(string="Name",default="New",readonly=True,copy="False")
    start_date = fields.Date(string="Start Date",required=True)
    end_date = fields.Date(string="End Date",required=True)
    state = fields.Selection([('draft','Draft'),('confirm','Confirm'),('done','Done'),('cancel','Cancel')],string="Status",default="draft")
    total_duration = fields.Float(string="Total Duration")
    company_id = fields.Many2one('res.company',string="Company",default=lambda self:self.env.company)
    line_ids = fields.One2many('mrp.labour.foh.line','mrp_labour_foh_id',string="Line")
    
    # Accounting Fields
    currency_id = fields.Many2one('res.currency',string="Currencies",default=lambda self:self.env.company.currency_id)
    salary_journal_id = fields.Many2one('account.journal',string="Journal Salary",required=True)
    foh_journal_id = fields.Many2one('account.journal',string="Journal FOH",required=True)
    account_labour_ids = fields.Many2many('account.account','mrp_labour_cost_account_account',string="Accounts Labour",required=True)
    account_foh_ids = fields.Many2many('account.account','mrp_foh_account_account',string="Accounts FOH",required=True)
    account_foh_id = fields.Many2one('account.account',string="Account FOH", help="Account FOH for journal purpose",required=True)
    account_wip_id = fields.Many2one('account.account',string="Account WIP",required=True)
    account_labour_id = fields.Many2one('account.account',string="Account Labour", help="Account Labour for journal purpose",required=True)
    account_cogs_id = fields.Many2one('account.account',string="Account COGS",required=True)
    labour_cost = fields.Monetary(string="Labour Cost",currency_field="currency_id",digits="Product Price")
    foh_cost = fields.Monetary(string="FOH Cost",currency_field="currency_id",digits="Product Price")
    
    
class MRPLabourFOHLine(models.Model):
    _name = "mrp.labour.foh.line"
    _description = "MRP Labour & FOH Line"
    
    name = fields.Char(string="Description")
    mrp_labour_foh_id = fields.Many2one('mrp.labour.foh',string="MRP Labour FOH",ondelete="set null")
    currency_id = fields.Many2one('res.currency',string="Currencies",related="mrp_labour_foh_id.currency_id")
    mrp_production_id = fields.Many2one('mrp.production',string="MO Number",ondelete="cascade")
    total_duration_wo = fields.Float(string="Total Duration Work Order")
    total_timesheet = fields.Float(string="Total Duration Timesheet")
    total_duration = fields.Float(string="Total")
    labour_cost = fields.Monetary(string="Labour Cost",currency_field="currency_id",digits="Product Price")
    foh_cost = fields.Monetary(string="FOH Cost",currency_field="currency_id",digits="Product Price")
    state = fields.Selection(related="mrp_production_id.state",string="State")