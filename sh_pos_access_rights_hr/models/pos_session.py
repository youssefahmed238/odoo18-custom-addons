from odoo import models,fields

class PosSessionInherit(models.Model):
    _inherit = "pos.session"

    def _loader_params_hr_employee(self):
        result = super(PosSessionInherit,self)._loader_params_hr_employee()
        result['search_params']['fields'].extend(["id", "disable_payment_id", "group_select_customer", "group_disable_discount", "group_disable_qty", "group_disable_price", "group_disable_plus_minus", "group_disable_numpad", "hr_group_disable_hide_orders", "hr_group_disable_remove", 'hr_group_remove_delete_button'])
        return result
    
        