# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import xml.etree as etr
import xml.etree.ElementTree as ET
from ast import literal_eval
import logging
_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit = ["purchase.order", "approval.matrix.mixin"]
    
    approver = fields.Text()
    approved_by_ids = fields.Many2many('res.users',compute="_compute_approver")
    minimum_approved = fields.Integer(compute="_compute_approver")
    approver_seq = fields.Integer()

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('rejected', 'Rejected'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    
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
            

    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            
            # check approval matrix
            order.sudo().checking_approval_matrix(require_approver=False)
            
            # if here not raises anything on approval matrix than it true / rules was passed
            # if any rules then it will registered on rule_ids
            # if not any rules,then probably it not required approvers
            if not order.approval_ids:
                order.button_approve()  
                # original: add supplier into product
                order._add_supplier_to_product()
                return True
            # if has any rules then write state into "to approve"
            order._add_supplier_to_product()
            order.write({'state': 'to approve'})
    
    def btn_approve(self):
        if not self._context.get('force_request'):    
            self.approving_matrix()
        if self.approved:     
            self.with_context(allowed_company_ids=self.company_id.ids,cids=self.company_id.id).button_approve()

    def button_reject(self):
        self.state = 'rejected'
        self.order_line.reject()
        self.rejecting_matrix()
        # self.button_cancel()
        
    def open_reject_message_wizard(self):
        self.ensure_one()
        
        form = self.env.ref('approval_matrix.message_post_wizard_form_view')
        context = dict(self.env.context or {})
        context.update({'default_prefix_message':"<h4>Rejecting Purchase Order</h4>","default_suffix_action": "button_reject"}) #uncomment if need append context
        context.update({'active_id':self.id,'active_ids':self.ids,'active_model':'purchase.order'})
        res = {
            'name': "%s - %s" % (_('Rejecting Purchase'), self.name),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'message.post.wizard',
            'view_id': form.id,
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new'
        }
        return res

#     def __authorized_form(self, root):
#           
#         def append_readonly_non_draft(elm):
#             # _logger.info(('---- loop', elm.tag))
#             if elm.tag!='field':
#                 return elm
#             
#             # _logger.info(('-------------->', elm.get('name')))
#             attrs = elm.get('attrs')
#             
#             if attrs:
#                 # IF HAS EXISTING "attrs" ATTRIBUTE
#                 attrs_dict = literal_eval(attrs)
#                 attrs_readonly = attrs_dict.get('readonly')
#                 # if had existing readonly rules on attrs will append it with or operator
#                 
#                 if attrs_readonly:
#                     if type(attrs_readonly) == list:
#                         # readonly if limit_approval_state not in draft,approved
#                         # incase:
#                         # when so.state locked (if limit automatically approved the limit_approval_state will still in draft) so will use original functions
#                         # when so.state == draft and limit approval strate in (need_approval_request,  need_approval, reject) will lock the field form to readonly
#                         
#                         # print(attrs_readonly)
#                         # forced domain
#                         attrs_readonly = [('state', 'not in',['draft'])]
#                     attrs_dict.update({'readonly':attrs_readonly})
#                 else:
#                     # if not exsit append new readonly key on attrs
#                     attrs_dict.update({'readonly':[('state','not in',['draft'])]})
#             else:
#                 
#                 attrs_dict = {'readonly':[('state','not in',['draft'])]}
#             try:
#                 new_attrs_str = str(attrs_dict)
#                 elm.set('attrs',new_attrs_str)
#             except Exception as e:
#                 pass
# 
#             return elm
# 
# 
#         def set_readonly_on_fields(elms):
#             for elm in elms:
# 
#                 if elm.tag=='field':
#                     elm = append_readonly_non_draft(elm)
#                 else:
#                     if len(elm)>0:
#                         _logger.info((len(elm)))
#                         if elm.tag in ['tree','kanban','form','calendar']:
#                             continue # skip if *2many field child element
#                         elm = set_readonly_on_fields(elm)
#                     else:
#                         if elm.tag=='field':
#                             elm = append_readonly_non_draft(elm)
#             return elms
#         paths = []
#         for child in root:
#             if child.tag=='sheet':
#                 # child = append_readonly_non_draft(child)
#                 child = set_readonly_on_fields(child)
#         return root
# 
#     @api.model
#     def _fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
# 
#         sup = super()._fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
#         # get generated xml view
#         
#         # if form
#         if view_type=='form':
#             root_elm = ET.fromstring("%s" % (sup['arch']))
#             # AUTHORIZED ALL "<field>" element
#             new_view = self.__authorized_form(root_elm)
#             sup.update({'arch':ET.tostring(new_view)})
# 
#         return sup

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('rejected', 'Rejected'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True,compute="_compute_state",store=True)

    @api.depends('order_id')
    def _compute_state(self):
        for rec in self:
            rec.state = rec.order_id.state

    def reject(self):
        for rec in self:
            rec.state = 'rejected'