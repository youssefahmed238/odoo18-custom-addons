from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    medical_policy_id = fields.Many2one('medical.policy', related='commission_line_id.medical_policy_id',
                                        string='Policy', ondelete='cascade')
    life_policy_id = fields.Many2one('life.policy', related='commission_line_id.life_policy_id', string='Policy',
                                     ondelete='cascade')
    motor_policy_id = fields.Many2one('motor.policy', related='commission_line_id.motor_policy_id', string='Policy',
                                      ondelete='cascade')
    fire_policy_id = fields.Many2one('fire.policy', related='commission_line_id.fire_policy_id', string='Policy',
                                     ondelete='cascade')
    engineering_policy_id = fields.Many2one('engineering.policy', related='commission_line_id.engineering_policy_id',
                                            string='Policy', ondelete='cascade')
    misc_policy_id = fields.Many2one('misc.policy', related='commission_line_id.misc_policy_id', string='Policy',
                                     ondelete='cascade')
    marine_policy_id = fields.Many2one('marine.policy', related='commission_line_id.marine_policy_id', string='Policy',
                                       ondelete='cascade')

    commission_line_id = fields.Many2one('commission.line', string='Commission Line', ondelete='cascade')
