from odoo.tests.common import SavepointCase, SingleTransactionCase, Form
from odoo.tests import tagged

from odoo.exceptions import Warning

@tagged('standard', 'at_install')
class TestSplitMo(SavepointCase):


    @classmethod
    def load_bom(cls):
        cls.bom = cls.env['mrp.bom'].search([], limit=1)
        

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

        Wiz = Form(self.env['wizard.split.mo'].with_context(action.get('context')))
        Wiz.split_mo_by = 'no_of_split'
        Wiz.no_of_qty = 1
        WizData = Wiz.save()
        with self.assertRaises(Warning):
            WizData.btn_split_mo() #gagal,, muncul error?? gak bisa split cuma 1
        return




    def test_mrp_prod_split_by_number_quantity(self):
        # self.assertEqual()
        return

    
    def test_mrp_prod_split_by_custom(self):
        # self.assertEqual()
        return