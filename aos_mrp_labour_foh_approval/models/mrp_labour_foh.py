from odoo import models,fields,api,_

class MRPLabourFOH(models.Model):
    _name = "mrp.labour.foh"
    _inherit = ["mrp.labour.foh", "approval.matrix.mixin"]
    
    approver = fields.Text()
    approved_by_ids = fields.Many2many('res.users',compute="_compute_approver")
    minimum_approved = fields.Integer(compute="_compute_approver")
    approver_seq = fields.Integer()
    
    state = fields.Selection(selection_add=[('waiting_approval','Waiting Approval'), ('approved','Approved'),('done',),('reject','Rejected')])
    
    @api.depends('approval_ids.approved_by_ids.name','approval_ids.approver_ids.name')
    def _compute_approver(self):
        for rec in self:
            approvers =""
            approved =""
            approved_by_ids = rec.approval_ids.mapped('approved_by_ids')
            for line in rec.approval_ids:
                approver = line.approver_ids.mapped('name')
                minimum_approved = line.minimum_approved
                approved = ''.join(line.approved_by_ids.mapped('name'))
                approver_seq = line.approver_seq
                if approver_seq <= 1 :
                    if minimum_approved <=1 :
                        approvers = '/'.join(approver)
                    else:
                        approvers = ','.join(approver)
                    if approved != "" :
                        if approver_seq <= 1 :
                            if minimum_approved <= 1 :
                                if len(approver) == 1 :
                                    approvers = approvers.replace(approved, '')
                                else :
                                    approvers = approvers.split('/')
                                    approvers = approvers.clear()
                            else :
                                approvers = approvers.split(',')
                                approvers = ''.join(approvers)
                                approvers = approvers.replace(approved, '')
                else :
                    if minimum_approved <= 1 :
                        approver_seq -= 1
                        if approver_seq and  len(approvers) == 0 :
                            approvers += '/'.join(approver)
                        else :
                            approvers += " And "+'/'.join(approver)
                    else :
                        approver_seq -= 1
                        if approver_seq and  len(approvers) == 0 :
                            approvers += ','.join(approver)
                        else :
                            approvers += " And "+','.join(approver) 
                    if approved != ""  :
                        approver_seq += 1
                        if approver_seq > 1 :
                            if minimum_approved <= 1 :
                                if len(approver) == 1 :
                                    approvers = approvers.replace(approved, '') 
                                else :
                                    approvers = approvers.split('/')
                                    approvers = approvers.clear()
                            else :
                                approvers = approvers.split(',')
                                approvers = ''.join(approvers)
                                approvers = approvers.replace(approved, '')
            
            rec.update({
                "approver" : approvers,
                "approved_by_ids" : approved_by_ids
            })
            
    def action_approval(self):
        self.sudo().checking_approval_matrix(require_approver=False)
        if not self.approval_ids:
            return self.action_approved()

        self.write({'state':'waiting_approval'})
        
    def action_approve(self):
        if not self._context.get('force_request'):    
            self.approving_matrix()
        if self.approved:     
            self.with_context(allowed_company_ids=self.company_id.ids,cids=self.company_id.id).action_approved()
        
        
    def action_approved(self):
        self.write({'state':'approved'})
        
    
    def action_reject(self):
        self.write({'state':'reject'})
        self.rejecting_matrix()
        
        
    def open_reject_message_wizard(self):
        self.ensure_one()
        
        form = self.env.ref('approval_matrix.message_post_wizard_form_view')
        context = dict(self.env.context or {})
        context.update({'default_prefix_message':"<h4>Rejecting Labour Cost & FOH</h4>","default_suffix_action": "action_reject"}) #uncomment if need append context
        context.update({'active_id':self.id,'active_ids':self.ids,'active_model':self._name})
        res = {
            'name': "%s - %s" % (_('Rejecting Labour Cost & FOH'), self.name),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'message.post.wizard',
            'view_id': form.id,
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new'
        }
        return res