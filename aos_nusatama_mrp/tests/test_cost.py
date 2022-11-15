from odoo.tests import SavepointCase, tagged
from odoo.tests.common import Form

class TestCost(SavepointCase):


    @classmethod
    def setupProduct(cls):
        prodcat = cls.env.ref('product.product_category_5')
        # comp1 = Form(cls.env['product.template'],'product.product_template_only_form_view')
        # comp1.name = 'component 1'
        # comp1.type = 'product'
        # comp1.sale_ok = True
        # comp1.purchase_ok = True
        # comp1.categ_id = prodcat
        # comp1 = comp1.save()

        cls.comp1 = cls.env['product.template'].create({
            'name': 'component 1',
            'sale_ok':True,
            'categ_id':prodcat.id,
            'type':'product',
            'sale_line_warn':'no-message'
        })

        cls.comp2 = cls.env['product.template'].create({
            'name': 'component 2',
            'sale_ok':True,
            'type':'product',
            'categ_id':prodcat.id,
            'sale_line_warn':'no-message'
        })
        
        cls.fg = cls.env['product.template'].create({
            'name': 'FG1',
            'sale_ok':True,
            'type':'product',
            'categ_id':prodcat.id,
            'sale_line_warn':'no-message'
        })


        cls.bom = cls.env['mrp.bom'].create({
            'product_tmpl_id':cls.fg.id,
            'product_id':cls.fg.product_variant_id.id,
            'bom_line_ids':[(0,0,{
                'product_id':cls.comp1.product_variant_id.id,
                'product_qty':1
            }),(0,0,{
                'product_id':cls.comp2.product_variant_id.id,
                'product_qty':2
            })]
        })

        print(cls.bom)
        

    @classmethod
    def setUpClass(cls):
        super(TestCost, cls).setUpClass()
        cls.setupProduct()
        
    def test_01(self):
        Mrp = self.env['mrp.production']
        NewMrp = Form(Mrp)
        NewMrp.bom_id = self.bom
        NewMrp.product_qty = 5
        prod = NewMrp.save()
        prod.action_confirm()
        self.assertEqual(prod.state,'confirmed')


        # PURCHASE
        po = Form(self.env['purchase.order'])
        vendor = self.env.ref('base.res_partner_12')
        po.partner_id = vendor
        po = po.save()
        pu1 = 2100
        pqty1 = 2
        pu2 = 1100
        pqty2 = 5
        with Form(po) as p:
            with p.order_line.new() as l:
                l.product_id = self.comp1.product_variant_id
                l.product_qty = pqty1
                l.price_unit = pu1

            with p.order_line.new() as l:
                l.product_id = self.comp2.product_variant_id
                l.product_qty = pqty2
                l.price_unit = pu2
        
        po.button_approve()
        self.assertEqual(po.picking_ids.picking_type_id.warehouse_id.reception_steps,'one_step')
        validate = po.picking_ids.button_validate()
        Wiz = Form(self.env[validate.get('res_model')].with_context(validate.get('context')), validate.get('view_id'))

        back =Wiz.save()
        back.process()
        # END PURCHASE

        # here product already done in stock

        # check move transfer for mrp.production
        # prod.picking_ids[0]
        inttransfer = prod.picking_ids[0]
        inttransfer.action_assign()
        validate = inttransfer.button_validate()
        Wiz = Form(self.env[validate.get('res_model')].with_context(validate.get('context')), validate.get('view_id'))

        back = Wiz.save()
        done = back.process()
        if not done==True and type(done)==dict:
            Wiz2 = Form(self.env[done.get('res_model')].with_context(done.get('context')), done.get('view_id'))
            backorder = Wiz2.save()
            backorder.process()


        # validate journal entry
        aml = self.env['account.move.line'].search([('ref','=like',inttransfer.name+'%')])
        self.assertEqual(sum(aml.mapped('debit')), sum(aml.mapped('credit')))
        self.assertEqual(sum(aml.mapped('debit')), ((pu1*pqty1) + (pu2*pqty2)) )
        
        prod.action_assign()
        self.assertTrue(all(prod.move_raw_ids.mapped(lambda r:r.state in ['partially_available'])))
        prod.action_generate_serial()
        prod.write({'qty_producing':2})

        prod.move_raw_ids.move_line_ids[0].write({'qty_done':pqty1})
        prod.move_raw_ids.move_line_ids[1].write({'qty_done':pqty2-1})
        done = prod.button_mark_done()
        newmo = False
        if done is not True:
            Wiz = Form(self.env[done.get('res_model')].with_context(done.get('context')))
            backorder = Wiz.save()
            res = backorder.with_context(testing=1).action_backorder()
            newmo = self.env[res.get('res_model')].browse(res.get('res_id'))

        # check valuation incoming

        aml = self.env['account.move.line'].search([('ref','=like',prod.name+'%')])
        self.assertEqual(sum(aml.mapped('debit')), sum(aml.mapped('credit')))
        self.assertEqual(sum(aml.mapped('debit')), ((pu1*pqty1) + (pu2*(pqty2-1))))

        # DONE 1ST MO


        # 2ND PURCHASE
        po = Form(self.env['purchase.order'])
        vendor = self.env.ref('base.res_partner_12')
        po.partner_id = vendor
        po = po.save()
        pu1 = 1900
        pqty1 = 4
        pu2 = 1400
        pqty2 = 12
        with Form(po) as p:
            with p.order_line.new() as l:
                l.product_id = self.comp1.product_variant_id
                l.product_qty = pqty1
                l.price_unit = pu1

            with p.order_line.new() as l:
                l.product_id = self.comp2.product_variant_id
                l.product_qty = pqty2
                l.price_unit = pu2
        
        po.button_approve()
        self.assertEqual(po.picking_ids.picking_type_id.warehouse_id.reception_steps,'one_step')
        validate = po.picking_ids.button_validate()
        Wiz = Form(self.env[validate.get('res_model')].with_context(validate.get('context')), validate.get('view_id'))

        back =Wiz.save()
        back.process()
        # END 2ND PURCHASE

        inttransfer = prod.picking_ids.filtered(lambda r:r.state not in ('done'))
        inttransfer.action_assign()
        validate = inttransfer.button_validate()
        Wiz = Form(self.env[validate.get('res_model')].with_context(validate.get('context')), validate.get('view_id'))

        back = Wiz.save()
        done = back.process()
        if not done==True and type(done)==dict:
            Wiz2 = Form(self.env[done.get('res_model')].with_context(done.get('context')), done.get('view_id'))
            backorder = Wiz2.save()
            backorder.process()


        # validate journal entry
        aml = self.env['account.move.line'].search([('ref','=like',inttransfer.name+'%')])
        self.assertEqual(sum(aml.mapped('debit')), sum(aml.mapped('credit')))
        self.assertEqual(sum(aml.mapped('debit')), ((inttransfer.move_lines[0].quantity_done*pu1) + (inttransfer.move_lines[1].quantity_done*pu2)))
        prod = newmo
        prod.action_assign()
        self.assertTrue(all(prod.move_raw_ids.mapped(lambda r:r.state in ['assigned'])))
        prod.action_generate_serial()
        prod.write({'qty_producing':3})

        prod.move_raw_ids.move_line_ids[0].write({'qty_done':inttransfer.move_lines[0].quantity_done})
        prod.move_raw_ids.move_line_ids[1].write({'qty_done':inttransfer.move_lines[1].quantity_done+1}) # 1 because 1 qty already reserved from 1st mo internal transfer
        done = prod.with_context(testing=1).button_mark_done()
        

        # check valuation incoming

        aml = self.env['account.move.line'].search([('ref','=like',prod.name+'%')])
        self.assertEqual(sum(aml.mapped('debit')), sum(aml.mapped('credit')))
        self.assertEqual(sum(aml.mapped('debit')),13800)
        