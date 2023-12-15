from odoo import models

#from init report import default_column
DEFAULT_COLUMN = {'default_header_row':6,'default_header_col':0,'default_row':7,'default_col':0}
DEFAULT_COLUMN_ALPHABET = [
    'A','B','C','D','E','F','G','H','I','J','K','L',
    'M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',

    'AA','AB','AC','AD','AE','AF','AG','AH','AI','AJ','AK','AL',
    'AM','AN','AO','AP','AQ','AR','AS','AT','AU','AV','AW','AX','AY','AZ',

    'BA','BB','BC','BD','BE','BF','BG','BH','BI','BJ','BK','BL',
    'BM','BN','BO','BP','BQ','BR','BS','BT','BU','BV','BW','BX','BY','BZ',

    'CA','CB','CC','CD','CE','CF','CG','CH','CI','CJ','CK','CL',
    'CM','CN','CO','CP','CQ','CR','CS','CT','CU','CV','CW','CX','CY','CZ',

    'DA','DB','DC','DD','DE','DF','DG','DH','DI','DJ','DK','DL',
    'DM','DN','DO','DP','DQ','DR','DS','DT','DU','DV','DW','DX','DY','DZ',

    'EA','EB','EC','ED','EE','EF','EG','EH','EI','EJ','EK','EL',
    'EM','EN','EO','EP','EQ','ER','ES','ET','EU','EV','EW','EX','EY','EZ',
]
import json
class PartnerXlsx(models.AbstractModel):
    _name = 'report.base_accounting_kit.report_trial_balance_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data,object):
        company = self.env.company.name
        sheet = workbook.add_worksheet("Test")
        data = json.loads(object.datas) 
        default_column = DEFAULT_COLUMN
        alp = DEFAULT_COLUMN_ALPHABET
        sheet.set_column("A:BZ",20)
        sheet.set_column("B:B",34)
        formats = workbook.add_format
        sheet.merge_range("A1:C1",company,formats({'bold':True,'align':'center','valign':'vcenter','font_size':16}))
        sheet.merge_range("A2:C2",'Trial Balance',formats({'bold':True,'valign':'vcenter','align':'center','font_size':14}))
        if not object.enable_filter:
            title = f"{data['form'][0]['date_from'] if data['form'][0]['date_from'] else ''} {'- ' + data['form'][0]['date_to'] if data['form'][0]['date_to'] else ''}"
            sheet.merge_range("A3:C3",title,formats({'align':'center','valign':'vcenter'}))

        sheet.write("A5","Target Moves",formats({'align':'center'})) 

        if object.display_account == 'all':
            sheet.write("B5",'All Accounts',formats({'valign':'vcenter','align':'center'}))
        elif object.display_account == 'movement':
            sheet.write("B5",'With Movements',formats({'valign':'vcenter','align':'center'}))
        else:
            sheet.write("B5",'With balance not equal to zero',formats({'valign':'vcenter','align':'center'}))

    #     # sheet.merge_range("F7:G8","DATE",formats({'valign':'vcenter'}))

    #     # set variabel untuk header column dan row dimulai setelah column balance yaitu 0
        header_row = default_column['default_header_row']
        header_col = default_column['default_header_col']
        sheet.merge_range(header_row,header_col,header_row,header_col + 1 ,"Account",formats({'align':'center'}))
        header_col += 2
        sheet.merge_range(header_row - 1,header_col + 1,header_row -1 ,header_col + 2,f"{object.from_id.name} {object.from_year.name if object.from_year else ''}",formats({'align':'center'}))
        sheet.write(header_row,header_col,"Initial Balance")
        header_col += 1
        sheet.write(header_row,header_col,"Debit")
        header_col += 1
        sheet.write(header_row,header_col,"Credit")
        header_col += 1
        if data.get('filters'):
            filter_object = data['filters'][::-1]
            for index in range(0,len(filter_object)):
                sheet.merge_range(header_row - 1,header_col,header_row - 1,header_col + 1 ,filter_object[index][0],formats({'align':'center'}))
                sheet.write(header_row,header_col,'Debit')
                header_col += 1
                sheet.write(header_row,header_col,'Credit')
                header_col += 1
        sheet.write(header_row,header_col,"Ending Balance")
        header_col += 1
    #     if object.enable_filter:
    #         sheet.write(header_row,header_col,object.from_id.name + " " +(object.year_from.name if object.year_from else '') )
    #     else:
    #         sheet.write(header_row,header_col,"Balance")

        line_row = default_column['default_row']
        line_col = default_column['default_col']
        last_line_col = 0
        format_amount = formats({'align':'right','num_format':'[$Rp-421] #,##0;[$Rp-421] -#,##0'})
        font_weight = formats({'bold':True})
        for name in json.loads(object.account_name_json):
            sheet.merge_range(line_row,line_col,line_row,line_col + 1,name)
            line_col += 2

            initial_balance_filter = next(filter(lambda x: x if x.get('name') == name else {}, data['initial_balance'][0][1]), {})
            sheet.write(line_row,line_col,initial_balance_filter.get('balance') if initial_balance_filter.get('balance') is not None else 0,format_amount)
            line_col += 1

            first_filter = next(filter(lambda x: x if x.get('name') == name else {}, data['accounts'][0][1]), {})
            sheet.write(line_row,line_col,first_filter.get('debit') if first_filter.get('debit') is not None else 0,format_amount)
            line_col += 1
            sheet.write(line_row,line_col,first_filter.get('credit') if first_filter.get('credit') is not None else 0,format_amount)
            line_col += 1
        #     last_line_col = line_col
        #     line_col = 0
        # # name dan balance adalah column static yang selalu ada
            if data.get('filters'):
                for index in range(0,len(filter_object)):
                    second_filter = next(filter(lambda x: x if x.get('name') == name else {}, filter_object[index][1]), {})
                    sheet.write(line_row,line_col,second_filter.get('debit') if second_filter.get('debit') is not None else 0,format_amount)
                    line_col += 1
                    sheet.write(line_row,line_col,second_filter.get('credit') if second_filter.get('credit') is not None else 0,format_amount)
                    line_col += 1
            # Ending Balance set Row From initial balance end this line
            start_column = alp[2]
            end_column = alp[line_col - 1] # kurang 1 untuk mendapatkan nilai sebelumnya
            # Formula terdiri dari =start_colum + defaulf row (C8) : end_column + line_col yang sekarang (F8)
            formula = f"=SUM({start_column}{line_row + 1}:{end_column}{line_row + 1})"
            sheet.write_formula(line_row,line_col,formula,format_amount)
                    
            last_line_col = line_col
            line_row += 1
            line_col = 0
        #TOTAL ALL ROW
        if object._mapping_name:
            line_col += 1
            total_format = formats({'align':'right','num_format':'[$Rp-421] #,##0;[$Rp-421] -#,##0','top':1})
            sheet.write(line_row,line_col,"Total",total_format)
            for num in range(2,last_line_col + 1):
                start_column = end_column = alp[num]
                line_col += 1
                formula = f"=SUM({start_column}{default_column['default_row'] + 1}:{end_column}{line_row})"
                sheet.write_formula(line_row,line_col,formula,total_format)