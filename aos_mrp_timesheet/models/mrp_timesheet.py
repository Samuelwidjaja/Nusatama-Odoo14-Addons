from odoo import models, fields,api,_
from odoo.osv import expression
from odoo.exceptions import UserError

class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    @api.model
    def default_get(self,field_list):
        res = super(AccountAnalyticLine, self).default_get(field_list)
        if not res.get('employee_id'):
            res['employee_id'] = self.env.user.employee_id.id
        if self.env.context.get('default_mrp_production_id'):
            res['mrp_production_id'] = self.env.context.get('default_mrp_production_id')
        return res

    # user_id = fields.Many2one(compute='_compute_user_id', store=True, readonly=False)
    # employee_id = fields.Many2one('hr.employee', "Employee", domain=_domain_employee_id, context={'active_test': False})
    mrp_production_id = fields.Many2one('mrp.production',string="Manufacturing Order",compute="_compute_mrp_production",domain="[('use_timesheet','=',True)]",store=True,readonly=False)
    mrp_workorder_id = fields.Many2one('mrp.workorder',string="MO Work Order", domain="[('production_id','=',mrp_production_id)]",compute="_compute_mrp_workorder",store=True,readonly=False)
    is_mrp_timesheet = fields.Boolean(compute="_compute_is_mrp_timesheet",readonly=False)

    @api.depends_context('timesheet_mrp')
    # @api.depends('project_id')
    def _compute_is_mrp_timesheet(self):
        for line in self:
            line.is_mrp_timesheet = line._context.get('timesheet_mrp',False)
            
    @api.depends('mrp_workorder_id', 'mrp_workorder_id.production_id')
    def _compute_mrp_production(self):
        for line in self.filtered(lambda line: not line.mrp_production_id):
            line.mrp_production_id = line.mrp_workorder_id.production_id

    @api.depends('mrp_production_id')
    def _compute_mrp_workorder(self):
        for line in self.filtered(lambda line: not line.mrp_production_id):
            line.mrp_workorder_id = False

    @api.onchange('mrp_production_id')
    def _onchange_mrp_production(self):
        # TODO KBA in master - check to do it "properly", currently:
        # This onchange is used to reset the task_id when the project changes.
        # Doing it in the compute will remove the task_id when the project of a task changes.
        if self.mrp_production_id != self.mrp_workorder_id.production_id:
            self.mrp_workorder_id = False

    def _mrp_timesheet_preprocess(self, vals):
        if vals.get('mrp_production_id') and not vals.get('account_id'):
            production = self.env['mrp.production'].browse(vals.get('mrp_production_id'))
            if not production.analytic_account_id:
                production._prepare_mo_analytic_account()
            vals['account_id'] = production.analytic_account_id.id
            vals['company_id'] = production.analytic_account_id.company_id.id or production.company_id.id
        # employee implies user
        if vals.get('employee_id') and not vals.get('user_id'):
            employee = self.env['hr.employee'].browse(vals['employee_id'])
            vals['user_id'] = employee.user_id.id
        return vals
            
    def _check_account_mrp(self):        
        for line in self.sudo():
            if line.account_id != line.mrp_production_id.analytic_account_id:
                line.account_id = line.mrp_production_id.analytic_account_id.id
            
    @api.model_create_multi
    def create(self,vals_list):
        for vals in vals_list:
            # if vals._context.get('timesheet_mrp'):
            if vals.get('mrp_production_id'):
                vals.update(self._mrp_timesheet_preprocess(vals))
        res = super(AccountAnalyticLine,self).create(vals_list)
        # Check for account make sure analytic account use from mrp analytic account not from the others
        if res.mrp_production_id:
            res.filtered(lambda x:x.mrp_production_id)._check_account_mrp()
        return res
    
    def write(self,vals):
        if self.mrp_production_id or self._context.get('timesheet_mrp'):
            vals.update(self._mrp_timesheet_preprocess(vals))
        res = super(AccountAnalyticLine,self).write(vals)
        if self.mrp_production_id or self._context.get('timesheet_mrp'):
            self.filtered(lambda x:x.mrp_production_id)._check_account_mrp()
        return res
        
        