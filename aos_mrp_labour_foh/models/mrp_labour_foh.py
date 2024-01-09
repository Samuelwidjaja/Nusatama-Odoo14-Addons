from odoo import models,fields, api,_
from odoo.exceptions import UserError
from datetime import datetime,timedelta,time
from odoo.tools.float_utils import float_round
from odoo.tools import float_compare
import math
from . import float_to_hour
from odoo.osv import expression
class MRPLabourFOH(models.Model):
    _name = "mrp.labour.foh"
    _inherit = ["mail.thread","mail.activity.mixin"]
    _description = "MRP Labour & FOH"
    _order = "id desc"
    
    @api.model
    def default_get(self,fields):
        result = super(MRPLabourFOH,self).default_get(fields)
        if 'account_labour_ids' not in result:
            labour_account = self.env['account.account'].search([('default_account_labour','=',True),('deprecated','=',False)])
            result['account_labour_ids'] = labour_account[:1].id
        if 'account_foh_ids' not in result:
            foh_account = self.env['account.account'].search([('default_account_foh','=',True),('deprecated','=',False)])
            result['account_foh_ids'] = foh_account[:1].id
        return result
    
    name = fields.Char(string="Name",default="New",readonly=True,copy=False,index=True)
    start_date = fields.Date(string="Start Date",required=True,tracking=1)
    end_date = fields.Date(string="End Date",required=True,tracking=2)
    state = fields.Selection([('draft','Draft'),('done','Posted'),('cancel','Cancel')],string="Status",default="draft",copy=False,tracking=True)
    total_duration = fields.Float(string="Total Duration",readonly=True,copy=False)
    company_id = fields.Many2one('res.company',string="Company",default=lambda self:self.env.company,tracking=True)
    line_ids = fields.One2many('mrp.labour.foh.line','mrp_labour_foh_id',string="Line",copy=False,tracking=True)
    
    # Accounting Fields
    currency_id = fields.Many2one('res.currency',string="Currencies",default=lambda self:self.env.company.currency_id)
    salary_journal_id = fields.Many2one('account.journal',string="Journal Salary",required=True,domain="[('company_id','=?',company_id),('type','=','general')]",tracking=True)
    foh_journal_id = fields.Many2one('account.journal',string="Journal FOH",required=True,domain="[('company_id','=?',company_id),('type','=','general')]",tracking=True)
    account_labour_ids = fields.Many2one('account.account',string="Accounts Labour",required=True)
    account_foh_ids = fields.Many2one('account.account',string="Accounts FOH",required=True,tracking=True)
    account_foh_id = fields.Many2one('account.account',string="Account FOH", help="Account FOH for journal purpose",required=True,tracking=True)
    account_wip_id = fields.Many2one('account.account',string="Account WIP",required=True,tracking=True)
    account_labour_id = fields.Many2one('account.account',string="Account Labour", help="Account Labour for journal purpose",required=True,tracking=True)
    # account_cogs_id = fields.Many2one('account.account',string="Account COGS",required=True)
    labour_cost = fields.Float(string="Labour Cost",digits="Product Price", readonly=True,store=True,copy=False)
    foh_cost = fields.Float(string="FOH Cost",digits="Product Price",readonly=True,store=True,copy=False)
    move_count = fields.Integer(compute="_compute_move_count")
    
    def action_update_price(self):
        #Total Debit Labour Cost
        domain = [('move_id.move_type','=','entry'),('date','>=',self.start_date),('date','<=',self.end_date)]
        labour_cost = self.env['account.move.line'].search(domain + [('account_id','in',self.account_labour_ids.ids)])
        self.labour_cost = sum(labour_cost.mapped('debit'))
        
        #Total Debit FOH Cost
        foh_cost = self.env['account.move.line'].search(domain + [('account_id','in',self.account_foh_ids.ids)])
        self.foh_cost = sum(foh_cost.mapped('debit'))
        
        # Compute Cost in line
        self.line_ids._compute_all()
        self.recompute_different_cost()
    
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
    
    def action_cancel(self):
        self.line_ids.move_line_ids.move_id.filtered(lambda move: move.state != 'posted').button_cancel()
        self.write({'state':'cancel'})
        
    def action_draft(self):
        self.write({'state':'draft'})
    
    def action_done(self):
        self.create_move()
        self.state = 'done'
        
    def action_view_moves(self):
        if self.line_ids.move_line_ids:
            return {
                'type':'ir.actions.act_window',
                'name':'Journal Entries',
                'res_model':'account.move',
                'view_mode':'tree,form',
                'domain':[('id','in',self.line_ids.move_line_ids.mapped('move_id').ids)],
            }
        return {'type':'ir.actions.act_window_close'}
    
    @api.depends('line_ids.move_line_ids')
    def _compute_move_count(self):
        for rec in self:
            rec.move_count = len(rec.line_ids.move_line_ids.mapped('move_id'))
    
    def recompute_different_cost(self):
        def _different_cost(amount, amount2, digits=2):
            """
                Check jika amount itu tidak sama dengan amount2 berdasarkan digits
                :return: bool, different_cost
                :rtype: bool, float
            """
            is_diff, diff_amount = False, 0
            if float_compare(amount, amount2, precision_digits=digits) > 0:
                is_diff = True
                diff_amount = amount - amount2
                
            return is_diff, diff_amount
        
        precision_digit = self.env['decimal.precision'].precision_get('Product Price')
        for rec in self.filtered(lambda r:r.line_ids):
            line_labour_cost = sum(rec.line_ids.mapped('labour_cost'))
            labour_cost = rec.labour_cost
            labour_diff, labour_cost_diff = _different_cost(labour_cost, line_labour_cost, precision_digit)
            if labour_diff:
                rec.line_ids[-1].labour_cost += labour_cost_diff
            
            # Amount Currency
            line_labour_cost = sum(rec.line_ids.mapped('amount_labour_cost'))
            labour_diff, labour_cost_diff = _different_cost(labour_cost, line_labour_cost, precision_digit)
            if labour_diff:
                rec.line_ids[-1].amount_labour_cost += labour_cost_diff
                
            line_foh_cost = sum(rec.line_ids.mapped('foh_cost'))
            foh_cost = rec.foh_cost
            foh_diff, foh_cost_diff = _different_cost(foh_cost, line_foh_cost, precision_digit)
            if foh_diff:
                rec.line_ids[-1].foh_cost += foh_cost_diff
            # Amount Currency
            line_foh_cost = sum(rec.line_ids.mapped('amount_foh_cost'))
            foh_diff, foh_cost_diff = _different_cost(foh_cost, line_foh_cost, precision_digit)
            if foh_diff:
                rec.line_ids[-1].amount_foh_cost += foh_cost_diff
                
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
        start_date = datetime.combine(self.start_date, time.min).strftime('%Y-%m-%d %H:%M:%S')
        end_date = datetime.combine(self.end_date, time.max).strftime('%Y-%m-%d %H:%M:%S')
        # Workorder Query
        query = """
            SELECT 
                SUM(wo.duration) as duration,
                wo.production_id
            FROM mrp_workorder as wo
            WHERE (wo.date_finished + INTERVAL '7 hours') BETWEEN %s AND %s
            GROUP BY wo.production_id
        """
        # use query for different timezone 
        self.env.cr.execute(query, [start_date, end_date])
        result = self.env.cr.dictfetchall() 
        if None in result:
            result = []
        # result = self.env['mrp.workorder'].read_group(['&',('date_finished','>=',self.start_date),('date_finished','<=',self.end_date)],['duration'],['production_id'],lazy=True)
        
        # Append Timesheet
        result += self.env['account.analytic.line'].read_group(['&',('date','>=',self.start_date),('date','<=',self.end_date),('mrp_production_id','!=',False)],['unit_amount'],['mrp_production_id'],lazy=True)
        lines = []
        for res in result:
            # use record timesheet & work order
            mo_id = ( res.get('mrp_production_id') or [ res.get('production_id', False) ] )[0] or False
            wo_duration = float_to_hour(res.get('duration', 0.0))
            timesheet_duration = res.get('unit_amount', 0.0)
            line_res = list( filter( lambda each: each[-1].get('mrp_production_id') == mo_id, lines or [(0,{})]) )
            if not line_res:
                if not mo_id: # mo false tapi ada ada wo duration dan timesheet duration
                    continue
                lines_vals = self._prepare_labour_foh_cost_line(
                                mrp_production_id=mo_id,
                                total_duration_wo= wo_duration,
                                total_timesheet=timesheet_duration,
                                mrp_labour_foh_id=self.id
                            )
                lines.append((0,0,lines_vals))
            else:
                line_res[0][-1]['total_duration_wo'] += wo_duration
                line_res[0][-1]['total_timesheet'] += timesheet_duration
            total_duration += (wo_duration + timesheet_duration)
        self.total_duration = total_duration
        self.line_ids = lines
        self.line_ids._compute_all()
        self.recompute_different_cost()
    
    def _prepare_move(self,):
        date = self._context.get('force_date', fields.Date.today())
        currency = self._context.get('force_currency',self.currency_id) or self.env.company.currency_id
        company = self._context.get('force_company') or self.company_id or self.env.company
        ref = self._get_description(is_salary=self._context.get('is_salary',False), is_foh=self._context.get('is_foh',False))
        journal_id = self._context.get('journal_id')
        if not journal_id:
            raise UserError("Account Journal Doesnt Exist")
        return {
            'ref':ref,
            'date':date,
            'currency_id':currency.id,
            'company_id':company.id,
            'journal_id':journal_id,
            'move_type':'entry',
            'line_ids':[],
        }
    
    def _prepare_move_line(self,line,account=False,amount=0.0):
        def get_cogs_account_id(line):
            account_cogs = line.product_id.categ_id.property_account_expense_categ_id.id or line.product_id.property_account_expense_id.id
            if not account_cogs:
                raise UserError(_("Account COGS from product %s not found" % line.product_id.display_name))
            
            return account_cogs
        
        credit_description = line._get_description_line(is_salary=self._context.get('is_salary',False), is_foh=self._context.get('is_foh',False))
        account = self._context.get('force_account') or account or self.account_labour_id
        # Line For COGS
        # Line for Labour Cost or FOH
        # Account COGS DIAMBIL DARI PRODUCT CATEGORY
        if line.state == 'progress':
            account_debit = self.account_wip_id.id
        else:
            account_debit = get_cogs_account_id(line)
        
        line_vals = [
            (0,0,{'account_id': account_debit,'name':line._get_description_line(is_cogs=True),'debit':abs(amount), 'credit':0.0,'labour_cost_foh_id':line.id}),
            (0,0,{'account_id':account.id,'name':credit_description, 'debit':0.0, 'credit':abs(amount),'labour_cost_foh_id':line.id})
        ]
        return line_vals
    
    def different_cost_currency(self, amount_cost, amount_to_check, digits=2):
        is_diff, diff_amount = False, 0
        if float_compare(amount_cost, amount_to_check, precision_digits=digits) > 0:
            is_diff = True
            diff_amount = amount_cost - amount_to_check
            
        return is_diff, diff_amount
    
    def create_move(self):
        try:
            #Try To access Accounting if current user doesnt have access to accounting
            self.env['account.move'].check_access_right('read')
            self.env['account.account'].check_access_right('read')
            AccMoves = self.env['account.move']
        except:
            AccMoves = self.env['account.move'].sudo()
            self = self.sudo()
        moves_vals_list = []
        salary_move_vals = self.with_context({},is_salary=True, journal_id=self.salary_journal_id.id)._prepare_move()
        foh_move_vals = self.with_context({},is_foh=True, journal_id=self.foh_journal_id.id)._prepare_move()
        for salary_line in self.line_ids:
            salary_move_vals['line_ids'] += self.with_context({}, is_salary=True)._prepare_move_line(salary_line,self.account_labour_id if salary_line.mrp_production_id.state == 'done' else self.account_wip_id,salary_line.amount_labour_cost)
        moves_vals_list.append(salary_move_vals)
        
        for foh_line in self.line_ids:
            foh_move_vals['line_ids'] += self.with_context({}, is_foh=True)._prepare_move_line(foh_line,self.account_foh_id if foh_line.mrp_production_id.state == 'done' else self.account_wip_id,foh_line.amount_foh_cost)
        moves_vals_list.append(foh_move_vals)
        # foh_moves = AccMoves.with_context(default_move="entry").create([foh_move_vals,])
        AccMoves += AccMoves.with_context(default_move_type="entry").create(moves_vals_list)
        # Rounding Currencies Issue 
        for move in AccMoves:
            if move.journal_id.id == self.salary_journal_id.id:
                amount = self.labour_cost
                amount2 = sum( move.line_ids.mapped('debit') )
            if float_compare(amount, amount2, precision_digits=2) > 0:
                diff_amount = amount - amount2 # different amount
                # add debit and credit 
                debit_line = move.line_ids.filtered(lambda x:x.debit)[:1]
                credit_line = move.line_ids.filtered(lambda x:x.credit)[:1]
                debit_line.update({'debit': debit_line.debit + diff_amount})
                credit_line.update({'credit': credit_line.credit + diff_amount})
                
    @api.model
    def create(self,vals):
        if vals.get('name','New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('mrp.labour.foh')
        return super().create(vals)
    
    
class MRPLabourFOHLine(models.Model):
    _name = "mrp.labour.foh.line"
    _description = "MRP Labour & FOH Line"
    
    name = fields.Char(string="Description")
    mrp_labour_foh_id = fields.Many2one('mrp.labour.foh',string="MRP Labour FOH",ondelete="cascade")
    currency_id = fields.Many2one('res.currency',string="Currencies",related="mrp_labour_foh_id.currency_id")
    mrp_production_id = fields.Many2one('mrp.production',string="MO Number",ondelete="cascade")
    product_id = fields.Many2one('product.product',string="Product", related='mrp_production_id.product_id',store=True)
    total_duration_wo = fields.Float(string="Total Duration Work Order",readonly=True)
    total_timesheet = fields.Float(string="Total Duration Timesheet",readonly=True)
    total_duration = fields.Float(string="Total",readonly=True,store=True)
    labour_cost = fields.Float(string="Labour Cost",digits="Product Price",store=True)
    foh_cost = fields.Float(string="FOH",digits="Product Price",store=True)
    amount_labour_cost = fields.Monetary(string="Amount Labour Cost",currency_field="currency_id",digits="Product Price", store=True)
    amount_foh_cost = fields.Monetary(string="Amount FOH Cost",currency_field="currency_id",digits="Product Price", store=True)
    state = fields.Selection(related="mrp_production_id.state",string="State")
    move_line_ids = fields.One2many('account.move.line','labour_cost_foh_id',string="Account Lines")
    
    # @api.depends('mrp_labour_foh_id.total_duration',
    #              'mrp_labour_foh_id.labour_cost',
    #              'mrp_labour_foh_id.foh_cost')
    def _compute_all(self):
        for rec in self:
            rec.total_duration = rec.total_duration_wo + rec.total_timesheet
            rec.labour_cost = (rec.total_duration / (rec.mrp_labour_foh_id.total_duration or 1.0)) * rec.mrp_labour_foh_id.labour_cost
            rec.foh_cost = (rec.total_duration / (rec.mrp_labour_foh_id.total_duration or 1.0)) * rec.mrp_labour_foh_id.foh_cost
            rec.amount_labour_cost = rec.labour_cost
            rec.amount_foh_cost = rec.foh_cost
    
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