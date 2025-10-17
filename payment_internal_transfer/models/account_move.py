from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        """ When posting a journal linked to a payment, also post the linked payment. """
        if self.env.context.get('skip_payment_post'):
            return super(AccountMove, self).action_post()
        else:
            for move in self:
                if move.origin_payment_id and move.origin_payment_id.state != 'paid':
                    move.origin_payment_id.with_context(skip_payment_post=True).action_post()
            return None

    def button_draft(self):
        """ When resetting to draft, also reset the linked payment to draft. """
        super(AccountMove, self).button_draft()

        for move in self:
            if move.origin_payment_id:
                move.origin_payment_id.state = 'draft'
