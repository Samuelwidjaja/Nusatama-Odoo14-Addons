import re
from calendar import monthrange
from datetime import datetime,date
from odoo import api, models, fields
from odoo.exceptions import UserError

class ConfigFilter(models.Model):
    _name = "config.filter"
    _description = "Configuration Filter"
    
    name = fields.Char(string="Name",required=True)
    type = fields.Selection([('monthly','Monthly'),('yearly','Yearly'),('quarter','Quarter')],string="Type Filter",default="monthly",required=True)
    month_int = fields.Integer(string="Month In Integer",readonly=True)
    months = fields.One2many('config.filter.line','config_filter_id',string="Lines")
    quarter_sequence = fields.Integer(string="Quarter Sequence",help="How to describe Quarter Sequence")
    year_int = fields.Integer(string="Year In Integer",readonly=True)
    @api.onchange("type")
    def onchange_type(self):
        vals = []
        self.months = [(5,0)]
        if self.type == 'yearly':
            for line in self.search([('type','=','monthly')]):
                if line.month_int in [1,12]:
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


    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        ctx = self._context
        if ctx.get('filter_selection','') == 'yearly':
            order = 'year_int asc'
        elif ctx.get('filter_selection','') == 'quarter':
            order = 'quarter_sequence asc'
        elif ctx.get('filter_selection','') == 'monthly':
            order = 'month_int asc'
        res = super(ConfigFilter, self)._search(
            args, offset=offset, limit=limit, order=order, count=count,access_rights_uid=access_rights_uid)
        return res

    def set_filter_data(self,data,filter=False,year=False):
        result = {}
        today = fields.Datetime.today()
        year_from = year.year_int if year else today.year
        if data.get('filter_selection') == 'quarter':
            # if self.to_id:
            #     filter.update({'to_month_int':self.to_id.months.mapped('month_int').sort(),'year_to':year_to})

            # if self.to_id.quarter_sequence < self.from_id.quarter_sequence and year_to == year_from:
            #     raise UserError(f"Doesnt Match Quarter {self.from_id.name} to {self.to_id.name} in the same year")

            month_int = filter.months.mapped('month_int')
            from_date = date(year_from,min(month_int),1)
            end_from_date = monthrange(year_from,max(month_int))[1]
            to_date = date(year_from,max(month_int),end_from_date)

            result.update({'from_month':from_date,'to_month':to_date})
        elif data.get('filter_selection') == 'monthly':
            from_date = date(year_from,filter.month_int,1)
            end_from_date = monthrange(year_from,from_date.month)[1]
            result.update({'from_month':from_date,'to_month':from_date.replace(day=end_from_date)})
        
        elif data.get('filter_selection') == 'yearly':
            year = filter.year_int
            month_int = filter.months.mapped('month_int')
            from_date = date(year,min(month_int),1)
            end_from_date = monthrange(year_from,max(month_int))[1]
            to_date = date(year,max(month_int),end_from_date)
            result.update({'from_month':from_date,'to_month':to_date})
        return result

    def range_comparison(self,data,from_year,to_year,filter_from=False,filter_to=False):
        today = date.today()
        default_from_year = from_year if from_year else self.env['config.filter'].search([('name','=',str(today.year))],limit=1)
        default_to_year = to_year if to_year else self.env['config.filter'].search([('name','=',str(today.year))],limit=1)
        result = {}
        list_result = []
        get_all_filter_by_selection = self.env['config.filter'].search([('type','=',data.get('filter_selection'))])
        if data.get('filter_selection') == 'quarter':
            if default_to_year.year_int < default_from_year.year_int:
                get_filter_from = self.env['config.filter'].search([('type','=','quarter'),('quarter_sequence','<',filter_from.quarter_sequence)])
                get_filter_to = self.env['config.filter'].search([('type','=','quarter'),('quarter_sequence','>=',filter_to.quarter_sequence)])
                get_filter_year = self.env['config.filter'].search([('year_int','>',default_to_year.year_int),('year_int','<',default_from_year.year_int)])
                # raise UserError(f'Invalid Comparison {self.from_id.name} {self.year_from.name} to {self.to_id.name} {self.year_to.name}')
                
                for line in get_filter_from:
                    list_result.append({line.name +" "+ default_from_year.name:self.set_filter_data(data,line,default_from_year)})

                for line in get_filter_year:
                    for l in get_all_filter_by_selection:
                        list_result.append({l.name + " " + line.name:self.set_filter_data(data,l,line)})

                for line in get_filter_to:
                    list_result.append({line.name +" "+ default_to_year.name:self.set_filter_data(data,line,default_to_year)})
                # from_date = self.set_filter_data(data,filter_to,to_year)
                # raise UserError(f'Invalid Comparison {self.from_id.name} {self.year_from.name} to {self.to_id.name} {self.year_to.name}')

            elif default_to_year.year_int > default_from_year.year_int:
                get_filter_from = self.env['config.filter'].search([('type','=','quarter'),('quarter_sequence','>',filter_from.quarter_sequence)])
                get_filter_to = self.env['config.filter'].search([('type','=','quarter'),('quarter_sequence','<=',filter_to.quarter_sequence)])
                get_filter_year = self.env['config.filter'].search([('year_int','<',default_to_year.year_int),('year_int','>',default_from_year.year_int)])
                # raise UserError(f'Invalid Comparison {self.from_id.name} {self.year_from.name} to {self.to_id.name} {self.year_to.name}')
                
                for line in get_filter_from:
                    list_result.append({line.name +" "+ default_from_year.name:self.set_filter_data(data,line,default_from_year)})

                for line in get_filter_year:
                    for l in get_all_filter_by_selection:
                        list_result.append({l.name + " " + line.name:self.set_filter_data(data,l,line)})

                for line in get_filter_to:
                    list_result.append({line.name +" "+ default_to_year.name:self.set_filter_data(data,line,default_to_year)})

            elif default_to_year.year_int == default_from_year.year_int:
                if filter_from.quarter_sequence < filter_to.quarter_sequence:
                    get_filter = self.env['config.filter'].search([('type','=','quarter'),('quarter_sequence','>',filter_from.quarter_sequence),('quarter_sequence','<=',filter_to.quarter_sequence)])
                else:
                    get_filter = self.env['config.filter'].search([('type','=','quarter'),('quarter_sequence','<',filter_from.quarter_sequence),('quarter_sequence','>=',filter_to.quarter_sequence)])
                
                for line in get_filter:
                    list_result.append({line.name +" "+ default_from_year.name:self.set_filter_data(data,line,default_from_year)})

        elif data.get('filter_selection') == 'monthly':
            if default_to_year.year_int < default_from_year.year_int:
                get_filter_from = self.env['config.filter'].search([('type','=','monthly'),('month_int','<',filter_from.month_int)])
                get_filter_to = self.env['config.filter'].search([('type','=','monthly'),('month_int','>=',filter_to.month_int)])
                get_filter_year = self.env['config.filter'].search([('year_int','>',default_to_year.year_int),('year_int','<',default_from_year.year_int)])

                for line in get_filter_from:
                    list_result.append({line.name +" "+ default_from_year.name:self.set_filter_data(data,line,default_from_year)})

                for line in get_filter_year:
                    for l in get_all_filter_by_selection:
                        list_result.append({l.name +" "+ line.name:self.set_filter_data(data,l,line)})

                for line in get_filter_to:
                    list_result.append({line.name +" "+ default_to_year.name:self.set_filter_data(data,line,default_to_year)})
                # # from_date = self.set_filter_data(data,filter_to,to_year)
                # raise UserError(f'Invalid Comparison {self.from_id.name} {self.year_from.name} to {self.to_id.name} {self.year_to.name}')

            elif default_to_year.year_int > default_from_year.year_int:
                get_filter_from = self.env['config.filter'].search([('type','=','monthly'),('month_int','>',filter_from.month_int)])
                get_filter_to = self.env['config.filter'].search([('type','=','monthly'),('month_int','<=',filter_to.month_int)])
                get_filter_year = self.env['config.filter'].search([('year_int','<',default_to_year.year_int),('year_int','>',default_from_year.year_int)])
                # raise UserError(f'Invalid Comparison {self.from_id.name} {self.year_from.name} to {self.to_id.name} {self.year_to.name}')
                for line in get_filter_from:
                    list_result.append({line.name +" "+ default_from_year.name:self.set_filter_data(data,line,default_from_year)})
                
                for line in get_filter_year:
                    for l in get_all_filter_by_selection:
                        list_result.append({l.name +" "+ line.name:self.set_filter_data(data,l,line)})

                for line in get_filter_to:
                    list_result.append({line.name +" "+ default_to_year.name:self.set_filter_data(data,line,default_to_year)})

            elif default_to_year.year_int == default_from_year.year_int:
                if filter_from.month_int < filter_to.month_int:
                    get_filter = self.env['config.filter'].search([('type','=','monthly'),('month_int','>',filter_from.month_int),('month_int','<=',filter_to.month_int)])
                else:
                    get_filter = self.env['config.filter'].search([('type','=','monthly'),('month_int','<',filter_from.month_int),('month_int','>=',filter_to.month_int)])
                
                for line in get_filter:
                    list_result.append({line.name +" "+ default_from_year.name:self.set_filter_data(data,line,default_from_year)})
                    
        elif data.get('filter_selection') == 'yearly':
            if filter_from.year_int > filter_to.year_int:
                res = get_all_filter_by_selection.filtered(lambda x:x.year_int < filter_from.year_int and x.year_int >= filter_to.year_int)
                # raise UserError(f'Invalid Comparison {self.from_id.name} to {self.to_id.name}')
            else:
                res = get_all_filter_by_selection.filtered(lambda x:x.year_int > filter_from.year_int and x.year_int <= filter_to.year_int)
            for line in res:
                list_result.append({line.name:self.set_filter_data(data,line)})

        for l in list_result:
            result.update(l)
        return list(result.items())

class ConfigFilterLine(models.Model):
    _name = "config.filter.line"

    
    config_filter_id = fields.Many2one('config.filter',string="Parent",readonly=True)
    month = fields.Many2one('config.filter',string="Month",domain=[('type','=','monthly')])
    month_int = fields.Integer(related="month.month_int",string="Month In Integer")
    type = fields.Selection(related="month.type",string="Type Filter")