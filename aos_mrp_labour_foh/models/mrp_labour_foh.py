from odoo import models,fields, api,_
from odoo.exceptions import UserError
from datetime import datetime

class MRPLabourFOH(models.Model):
    _name = "mrp.labour.foh"
    _description = "MRP Labour & FOH"
    _order = "id desc"
    
    @api.model
    def default_get(self,fields):
        result = super(MRPLabourFOH,self).default_get(fields)
        if 'account_labour_ids' not in result:
            labour_account = self.env['account.account'].search([('default_account_labour','=',True),('deprecated','=',False)])
            result['account_labour_ids'] = [(6,0,labour_account.ids)]
        if 'account_foh_ids' not in result:
            foh_account = self.env['account.account'].search([('default_account_foh','=',True),('deprecated','=',False)])
            result['account_foh_ids'] = [(6,0,foh_account.ids)]
        return result
    
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
    labour_cost = fields.Monetary(string="Labour Cost",currency_field="currency_id",digits="Product Price", readonly=True,store=True)
    foh_cost = fields.Monetary(string="FOH Cost",currency_field="currency_id",digits="Product Price",readonly=True,store=True)
    
    def action_update_price(self):
        #Total Debit Labour Cost
        domain = [('move_id.move_type','=','entry'),('date','>=',self.start_date),('date','<=',self.end_date)]
        labour_cost = self.env['account.move.line'].search(domain + [('account_id','in',self.account_labour_ids.ids)])
        self.labour_cost = sum(labour_cost.mapped('debit'))
        
        #Total Debit FOH Cost
        foh_cost = self.env['account.move.line'].search(domain + [('account_id','in',self.account_foh_ids.ids)])
        self.foh_cost = sum(foh_cost.mapped('debit'))
        
    def fetch_summary(self):
        total_duration = 0.0
        self.line_ids = [(5,0)]
        # Fetch All MO Summary
    #     query = self.env.cr.execute(""" 
    #     WITH timesheet_mrp AS (   
    #         SELECT 
    #             mrp_production_id timesheet_mo_id,
    #             SUM(unit_amount) total_duration
    #         FROM account_analytic_line
    #         WHERE date BETWEEN %s AND %s 
    #         GROUP BY mrp_production_id
    #     )                        
    #     SELECT 
    #         wo.production_id mo_id,
    #         SUM(wo.duration) total_duration_wo,
    #         (SELECT total_duration FROM timesheet_mrp WHERE timesheet_mo_id = wo.production_id) total_duration_timesheet,
    #         SUM(wo.duration) + (SELECT total_duration FROM timesheet_mrp WHERE timesheet_mo_id = wo.production_id) as total
    #     FROM mrp_workorder wo
    #     WHERE DATE(wo.date_finished) BETWEEN %s AND %s
    #     GROUP BY wo.production_id
    # """,[self.start_date,self.end_date,self.start_date,self.end_date])
    #     result = self.env.cr.dictfetchall()
        result = self.env['mrp.workorder'].read_group(['&',('date_finished','>=',self.start_date),('date_finished','<=',self.end_date)],['duration'],['production_id'],lazy=True)
        lines = []
        for res in result:
            mo_id = res.get('production_id')[0]
            timesheet_mrp = self.env['account.analytic.line'].read_group(['&',('date','>=',self.start_date),('date','<=',self.end_date),('mrp_production_id','=',mo_id)],['unit_amount'],['mrp_production_id'],lazy=True) 
            total_duration += (res.get('duration') + timesheet_mrp[0].get('unit_amount') if timesheet_mrp else 0.0)
            lines.append((0,0,{'mrp_production_id':mo_id,
                               'mrp_labour_foh_id':self.id,
                               'total_duration_wo':res.get('duration'),
                               'total_timesheet':timesheet_mrp[0].get('unit_amount') if timesheet_mrp else 0.0,
                               'total_duration':(res.get('duration') + timesheet_mrp[0].get('unit_amount') if timesheet_mrp else 0.0),
                            }))
        self.line_ids = lines
        self.total_duration = total_duration
        
class MRPLabourFOHLine(models.Model):
    _name = "mrp.labour.foh.line"
    _description = "MRP Labour & FOH Line"
    
    name = fields.Char(string="Description")
    mrp_labour_foh_id = fields.Many2one('mrp.labour.foh',string="MRP Labour FOH",ondelete="cascade")
    currency_id = fields.Many2one('res.currency',string="Currencies",related="mrp_labour_foh_id.currency_id")
    mrp_production_id = fields.Many2one('mrp.production',string="MO Number",ondelete="cascade")
    total_duration_wo = fields.Float(string="Total Duration Work Order",readonly=True)
    total_timesheet = fields.Float(string="Total Duration Timesheet",readonly=True)
    total_duration = fields.Float(string="Total",readonly=True)
    labour_cost = fields.Monetary(string="Labour Cost",currency_field="currency_id",digits="Product Price",compute="_compute_labour_and_foh_cost",store=True)
    foh_cost = fields.Monetary(string="FOH Cost",currency_field="currency_id",digits="Product Price",compute="_compute_labour_and_foh_cost",store=True)
    state = fields.Selection(related="mrp_production_id.state",string="State")
    
    @api.depends('mrp_labour_foh_id.total_duration',
                 'mrp_labour_foh_id.labour_cost',
                 'mrp_labour_foh_id.foh_cost')
    def _compute_labour_and_foh_cost(self):
        for rec in self:
            rec.labour_cost = (rec.total_duration / (rec.mrp_labour_foh_id.total_duration or 1.0)) * rec.mrp_labour_foh_id.labour_cost
            rec.foh_cost = (rec.total_duration / (rec.mrp_labour_foh_id.total_duration or 1.0)) * rec.mrp_labour_foh_id.foh_cost