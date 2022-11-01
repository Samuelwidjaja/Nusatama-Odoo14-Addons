from odoo.tests.common import SavepointCase, SingleTransactionCase, Form
from odoo.tests import tagged

from odoo.exceptions import Warning

@tagged('standard', 'at_install')
class TestSplitMo(SavepointCase):


    @classmethod
    def load_bom(cls):
        cls.bom = cls.env['mrp.bom'].browse(2)
        

    @classmethod
    def setUpClass(cls):
        super(TestSplitMo, cls).setUpClass()
        cls.load_bom()


    def test_no_of_split_01(self):
        # mo_qty = 2
        # n = 1

        # expected = [1,1]

        Wiz = self.env['wizard.split.mo']

        res = Wiz.no_of_split(mo_qty=2, n=1, split_qty_lst=[])
        self.assertEqual(len(res),1)
        self.assertEqual(res, [2])


        res = Wiz.no_of_split(mo_qty=3, n=2, split_qty_lst=[])
        # expected = [1,2]
        self.assertEqual(len(res),2)
        self.assertEqual(res, [1,2])



        res = Wiz.no_of_split(mo_qty=12, n=12, split_qty_lst=[])
        # expected = [1,2]
        self.assertEqual(len(res),12)
        self.assertTrue(all(list(map(lambda r:r==1, res))))

    def test_mrp_prod_split_by_number_of_split(self):
        
        Mrp = self.env['mrp.production']
        rec_form = Form(Mrp)
        rec_form.bom_id = self.bom
        rec_form.product_qty = 3
        rec = rec_form.save()


        action = rec.split_manufacturing_orders()

        #move_Raw_ids Testing
        Wiz = Form(self.env['wizard.split.mo'].with_context(action.get('context')))
        Wiz.split_mo_by = 'no_of_split'
        Wiz.no_of_qty = 2
        WizData = Wiz.save()
        res = WizData.btn_split_mo()
        self.assertEqual(len(res),2)
        a = 1
        for rec in res :
            self.assertEqual(rec.name,rec.origin+'-'+str(a))
            a += 1
            if rec.product_qty == 1:
                prod_1 = 1
                prod_2 = 4
                prod_3 = 4
                prod_4 = 10
                self.assertEqual(prod_1,rec.move_raw_ids[0].product_qty)
                self.assertEqual(prod_2,rec.move_raw_ids[1].product_qty)
                self.assertEqual(prod_3,rec.move_raw_ids[2].product_qty)
                self.assertEqual(prod_4,rec.move_raw_ids[3].product_qty)
            elif rec.product_qty == 2:
                prod_1 = 2
                prod_2 = 8
                prod_3 = 8
                prod_4 = 20
                self.assertEqual(prod_1,rec.move_raw_ids[0].product_qty)
                self.assertEqual(prod_2,rec.move_raw_ids[1].product_qty)
                self.assertEqual(prod_3,rec.move_raw_ids[2].product_qty)
                self.assertEqual(prod_4,rec.move_raw_ids[3].product_qty)
            elif rec.product_qty == 3:
                prod_1 = 3
                prod_2 = 12
                prod_3 = 12
                prod_4 = 30
                self.assertEqual(prod_1,rec.move_raw_ids[0].product_qty)
                self.assertEqual(prod_2,rec.move_raw_ids[1].product_qty)
                self.assertEqual(prod_3,rec.move_raw_ids[2].product_qty)
                self.assertEqual(prod_4,rec.move_raw_ids[3].product_qty)

        #cancle testing
        Wiz = Form(self.env['wizard.split.mo'].with_context(action.get('context')))
        Wiz.split_mo_by = 'no_of_split'
        Wiz.no_of_qty = 1
        WizData = Wiz.save()
        if Wiz.no_of_qty > rec_form.product_qty or Wiz.no_of_qty <= 1 :
            with self.assertRaises(Warning):
                WizData.btn_split_mo()  #gagal,, muncul error?? gak bisa split cuma 1
        return


    def test_mrp_prod_split_by_number_quantity(self):
        Mrp = self.env['mrp.production']
        rec_form = Form(Mrp)
        rec_form.bom_id = self.bom
        rec_form.product_qty = 7
        rec = rec_form.save()

        action = rec.split_manufacturing_orders()

        #move_Raw_ids Testing
        Wiz = Form(self.env['wizard.split.mo'].with_context(action.get('context')))
        Wiz.split_mo_by = 'no_qty'
        Wiz.no_of_qty = 3
        WizData = Wiz.save()
        res = WizData.btn_split_mo()
        self.assertEqual(len(res),3)
        a = 1
        for rec in res :
            self.assertEqual(rec.name,rec.origin+'-'+str(a))
            a += 1
            if rec.product_qty == 1:
                prod_1 = 1
                prod_2 = 4
                prod_3 = 4
                prod_4 = 10
                self.assertEqual(prod_1,rec.move_raw_ids[0].product_qty)
                self.assertEqual(prod_2,rec.move_raw_ids[1].product_qty)
                self.assertEqual(prod_3,rec.move_raw_ids[2].product_qty)
                self.assertEqual(prod_4,rec.move_raw_ids[3].product_qty)
            elif rec.product_qty == 2:
                prod_1 = 2
                prod_2 = 8
                prod_3 = 8
                prod_4 = 20
                self.assertEqual(prod_1,rec.move_raw_ids[0].product_qty)
                self.assertEqual(prod_2,rec.move_raw_ids[1].product_qty)
                self.assertEqual(prod_3,rec.move_raw_ids[2].product_qty)
                self.assertEqual(prod_4,rec.move_raw_ids[3].product_qty)
            elif rec.product_qty == 3:
                prod_1 = 3
                prod_2 = 12
                prod_3 = 12
                prod_4 = 30
                self.assertEqual(prod_1,rec.move_raw_ids[0].product_qty)
                self.assertEqual(prod_2,rec.move_raw_ids[1].product_qty)
                self.assertEqual(prod_3,rec.move_raw_ids[2].product_qty)
                self.assertEqual(prod_4,rec.move_raw_ids[3].product_qty)
                
        #cancle testing
        Wiz = Form(self.env['wizard.split.mo'].with_context(action.get('context')))
        Wiz.split_mo_by = 'no_of_split'
        Wiz.no_of_qty = 1
        WizData = Wiz.save()
        if Wiz.no_of_qty > rec_form.product_qty or Wiz.no_of_qty <= 1 :
            with self.assertRaises(Warning):
                WizData.btn_split_mo()  #gagal,, muncul error?? gak bisa split cuma 1
        return

    
    def test_mrp_prod_split_by_custom(self):
        Mrp = self.env['mrp.production']
        rec_form = Form(Mrp)
        rec_form.bom_id = self.bom
        rec_form.product_qty = 7
        rec = rec_form.save()

        action = rec.split_manufacturing_orders()

        #move_Raw_ids Testing
        Wiz = Form(self.env['wizard.split.mo'].with_context(action.get('context')))
        Wiz.split_mo_by = 'custom'
        WizData = Wiz.save()
        WizData.split_mo_line_ids = [(0,0,{'qty': 2}),(0,0,{'qty': 2}),(0,0,{'qty': 3})]
        res = WizData.btn_split_mo()
        self.assertEqual(len(res),3)
        a = 1
        for rec in res :
            self.assertEqual(rec.name,rec.origin+'-'+str(a))
            a += 1
            if rec.product_qty == 1:
                prod_1 = 1
                prod_2 = 4
                prod_3 = 4
                prod_4 = 10
                self.assertEqual(prod_1,rec.move_raw_ids[0].product_qty)
                self.assertEqual(prod_2,rec.move_raw_ids[1].product_qty)
                self.assertEqual(prod_3,rec.move_raw_ids[2].product_qty)
                self.assertEqual(prod_4,rec.move_raw_ids[3].product_qty)
            elif rec.product_qty == 2:
                prod_1 = 2
                prod_2 = 8
                prod_3 = 8
                prod_4 = 20
                self.assertEqual(prod_1,rec.move_raw_ids[0].product_qty)
                self.assertEqual(prod_2,rec.move_raw_ids[1].product_qty)
                self.assertEqual(prod_3,rec.move_raw_ids[2].product_qty)
                self.assertEqual(prod_4,rec.move_raw_ids[3].product_qty)
            elif rec.product_qty == 3:
                prod_1 = 3
                prod_2 = 12
                prod_3 = 12
                prod_4 = 30
                self.assertEqual(prod_1,rec.move_raw_ids[0].product_qty)
                self.assertEqual(prod_2,rec.move_raw_ids[1].product_qty)
                self.assertEqual(prod_3,rec.move_raw_ids[2].product_qty)
                self.assertEqual(prod_4,rec.move_raw_ids[3].product_qty)
                
        #Error testing
        Wiz = Form(self.env['wizard.split.mo'].with_context(action.get('context')))
        Wiz.split_mo_by = 'custom'
        WizData = Wiz.save()
        WizData.split_mo_line_ids = [(0,0,{'qty': 1}),(0,0,{'qty': 2}),(0,0,{'qty': 3})]
        #res = WizData.btn_split_mo()
        #qty = 0
        #for rec in res :
        #    qty += rec.product_qty
        #if qty != rec_form.product_qty :
        with self.assertRaises(Warning):
            WizData.btn_split_mo()  #gagal, karena jumlah product_qty != total qty split
        return