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
    salary_journal_id = fields.Many2one('account.journal',string="Journal Salary",required=True,domain="[('company_id','=?',company_id),('type','=','general')]")
    foh_journal_id = fields.Many2one('account.journal',string="Journal FOH",required=True,domain="[('company_id','=?',company_id),('type','=','general')]")
    account_labour_ids = fields.Many2many('account.account','mrp_labour_cost_account_account',string="Accounts Labour",required=True)
    account_foh_ids = fields.Many2many('account.account','mrp_foh_account_account',string="Accounts FOH",required=True)
    account_foh_id = fields.Many2one('account.account',string="Account FOH", help="Account FOH for journal purpose",required=True)
    account_wip_id = fields.Many2one('account.account',string="Account WIP",required=True)
    account_labour_id = fields.Many2one('account.account',string="Account Labour", help="Account Labour for journal purpose",required=True)
    account_cogs_id = fields.Many2one('account.account',string="Account COGS",required=True)
    labour_cost = fields.Monetary(string="Labour Cost",currency_field="currency_id",digits="Product Price", readonly=True,store=True)
    foh_cost = fields.Monetary(string="FOH Cost",currency_field="currency_id",digits="Product Price",readonly=True,store=True)
    moves_ids = fields.Many2many('account.move',string="Moves",relation="foh_labour_cost_moves_rel")
    
    def action_update_price(self):
        #Total Debit Labour Cost
        domain = [('move_id.move_type','=','entry'),('date','>=',self.start_date),('date','<=',self.end_date)]
        labour_cost = self.env['account.move.line'].search(domain + [('account_id','in',self.account_labour_ids.ids)])
        self.labour_cost = sum(labour_cost.mapped('debit'))
        
        #Total Debit FOH Cost
        foh_cost = self.env['account.move.line'].search(domain + [('account_id','in',self.account_foh_ids.ids)])
        self.foh_cost = sum(foh_cost.mapped('debit'))
    
    def _get_description(self,is_salary=False,is_cogs=False,is_foh=False,prefix_date=True):
        name =  self.name
        if is_salary:
            name = "Salary " + name
        if is_cogs:
            name = "COGS " + name
        if is_foh:
            name = "FOH " + name
        if prefix_date:
            name = name + " - " + str(self.start_date) + "/" + str(self.end_date) 
        return name
    
    def action_done(self):
        self.create_move()
        self.state = 'done'
        
    def action_view_moves(self):
        if self.moves_ids:
            return {
                'type':'ir.actions.act_window',
                'name':'Journal Entries',
                'res_model':'account.move',
                'view_mode':'tree,form',
                'domain':[('id','in',self.moves_ids.ids)],
            }
        return {'type':'ir.actions.act_window_close'}
    ##################
    # CRUD METHOD
    ##################
    def _prepare_labour_foh_cost_line(self,mrp_production_id=False,total_duration_wo=0.0,total_timesheet=0.0,total_duration=0.0,**kwargs):
        vals =  {
            'mrp_production_id':mrp_production_id,
            'total_duration_wo':total_duration_wo,
            'total_timesheet':total_timesheet,
            'total_duration':total_duration
        }
        if kwargs:
            vals.update(kwargs)
        return vals
    
    def fetch_summary(self):
        total_duration = 0.0
        self.line_ids = [(5,0)]
        result = self.env['mrp.workorder'].read_group(['&',('date_finished','>=',self.start_date),('date_finished','<=',self.end_date)],['duration'],['production_id'],lazy=True)
        timesheet = not result
        if timesheet:
            result = self.env['account.analytic.line'].read_group(['&',('date','>=',self.start_date),('date','<=',self.end_date),('mrp_production_id','!=',False)],['unit_amount'],['mrp_production_id'],lazy=True)
        lines = []
        for res in result:
            if not timesheet:
                #Use Record Work Order
                mo_id = res.get('production_id')[0]
                timesheet_mrp = self.env['account.analytic.line'].read_group(['&',('date','>=',self.start_date),('date','<=',self.end_date),('mrp_production_id','=',mo_id)],['unit_amount'],['mrp_production_id'],lazy=True) 
                total_duration += (res.get('duration') + timesheet_mrp[0].get('unit_amount') if timesheet_mrp else 0.0)
                lines_vals = self._prepare_labour_foh_cost_line(
                                mrp_production_id=mo_id,
                                total_duration_wo=res.get('duration'),
                                total_timesheet=timesheet_mrp[0].get('unit_amount') if timesheet_mrp else 0.0,
                                total_duration=(res.get('duration') + timesheet_mrp[0].get('unit_amount') if timesheet_mrp else 0.0),
                                mrp_labour_foh_id=self.id
                            )
            else:
                #Use Record Timesheet
                mo_id = res.get('mrp_production_id')[0]
                total_duration += res.get('unit_amount')
                lines_vals = self._prepare_labour_foh_cost_line(
                                mrp_production_id=mo_id,
                                total_timesheet=res.get('unit_amount'),
                                total_duration=res.get('unit_amount'),
                                mrp_labour_foh_id=self.id
                            )
            lines.append((0,0,lines_vals))
        self.line_ids = lines
        self.total_duration = total_duration
    
    def _prepare_move(self,):
        date = self._context.get('force_date', fields.Date.today())
        currency = self._context.get('force_currency',self.currency_id) or self.env.company.currency_id
        company = self._context.get('force_company') or self.company_id or self.env.company
        ref = self._get_description(is_salary=self._context.get('is_salary',False), is_foh=self._context.get('is_foh',False))
        return {
            'ref':ref,
            'date':date,
            'currency_id':currency.id,
            'company_id':company.id,
            'move_type':'entry',
            'line_ids':[],
        }
    
    def _prepare_move_line(self,line,account=False,amount=0.0):
        credit_description = line._get_description_line(is_salary=self._context.get('is_salary',False), is_foh=self._context.get('is_foh',False))
        account_cogs = self._context.get('force_account_cogs', self.account_cogs_id)
        account = self._context.get('force_account') or account or self.account_labour_id
        line_vals = [
            (0,0,{'account_id':account_cogs.id,'name':line._get_description_line(is_cogs=True),'debit':abs(amount), 'credit':0.0,'labour_cost_foh_id':line.id}),
            (0,0,{'account_id':account.id,'name':credit_description, 'debit':0.0, 'credit':abs(amount),'labour_cost_foh_id':line.id})
        ]
        return line_vals
    
    def create_move(self):
        try:
            self.env['account.move'].check_access_right('read')
            self.env['account.account'].check_access_right('read')
            AccMoves = self.env['account.move']
        except:
            AccMoves = self.env['account.move'].sudo()
            self = self.sudo()
        moves_vals_list = []
        salary_move_vals = self.with_context({},is_salary=True)._prepare_move()
        foh_move_vals = self.with_context({},is_foh=True)._prepare_move()
        for salary_line in self.line_ids:
            salary_move_vals['line_ids'] += self.with_context({}, is_salary=True)._prepare_move_line(salary_line,self.account_labour_id,salary_line.labour_cost)
        moves_vals_list.append(salary_move_vals)
        # salary_moves = AccMoves.with_context(default_move_type="entry").create([salary_move_vals,])
        
        for foh_line in self.line_ids:
            foh_move_vals['line_ids'] += self.with_context({}, is_foh=True)._prepare_move_line(foh_line,self.account_foh_id,salary_line.foh_cost)
        moves_vals_list.append(foh_move_vals)
        # foh_moves = AccMoves.with_context(default_move="entry").create([foh_move_vals,])
        self.moves_ids = AccMoves.with_context(default_move_type="entry").create(moves_vals_list)
        
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
    foh_cost = fields.Monetary(string="FOH",currency_field="currency_id",digits="Product Price",compute="_compute_labour_and_foh_cost",store=True)
    state = fields.Selection(related="mrp_production_id.state",string="State")
    
    @api.depends('mrp_labour_foh_id.total_duration',
                 'mrp_labour_foh_id.labour_cost',
                 'mrp_labour_foh_id.foh_cost')
    def _compute_labour_and_foh_cost(self):
        for rec in self:
            rec.labour_cost = (rec.total_duration / (rec.mrp_labour_foh_id.total_duration or 1.0)) * rec.mrp_labour_foh_id.labour_cost
            rec.foh_cost = (rec.total_duration / (rec.mrp_labour_foh_id.total_duration or 1.0)) * rec.mrp_labour_foh_id.foh_cost
    
    @api.onchange('mrp_production_id','mrp_labour_foh_id')
    def _onchange_name(self):
        for rec in self:
            rec.name = rec.mrp_production_id.name

    def _get_description_line(self,is_salary=False,is_cogs=False,is_foh=False):
        name = self.name
        if is_salary:
            name = name + " LC"
        if is_cogs:
            name = name + " COGS"
        if is_foh:
            name = name + " FOH"
        return name
    
    @api.model_create_multi
    def create(self,vals_list):
        res = super().create(vals_list)
        res._onchange_name()
        return res