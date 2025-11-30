from odoo import models, fields, api


class CommissionLine(models.Model):
    _name = 'commission.line'
    _description = 'Commission Line'

    medical_policy_id = fields.Many2one('medical.policy', string='Medical Policy')
    life_policy_id = fields.Many2one('life.policy', string='Life Policy')
    motor_policy_id = fields.Many2one('motor.policy', string='Motor Policy')
    fire_policy_id = fields.Many2one('fire.policy', string='Fire Policy')
    engineering_policy_id = fields.Many2one('engineering.policy', string='Engineering Policy')
    misc_policy_id = fields.Many2one('misc.policy', string='Misc Policy')
    marine_policy_id = fields.Many2one('marine.policy', string='Marine Policy')

    contract_line_id = fields.Many2one('insurance.contract.line', string='Contract', required=True)

    basic_p = fields.Float(string='Basic %', related='contract_line_id.basic')
    comp_p = fields.Float(string='Comp %', related='contract_line_id.comp')
    bonus_p = fields.Float(string='Bonus %', related='contract_line_id.bonus')
    commission_p = fields.Float(string='Commission %', related='contract_line_id.commission')

    layer_1_p = fields.Float(string='Layer 1 %', related='contract_line_id.layer_1')
    layer_2_p = fields.Float(string='Layer 2 %', related='contract_line_id.layer_2')
    layer_3_p = fields.Float(string='Layer 3 %', related='contract_line_id.layer_3')
    layer_4_p = fields.Float(string='Layer 4 %', related='contract_line_id.layer_4')

    basic = fields.Float(string='Basic', compute='_compute_values', store=True)
    comp = fields.Float(string='Comp', compute='_compute_values', store=True)
    bonus = fields.Float(string='Bonus', compute='_compute_values', store=True)
    commission = fields.Float(string='Commission', compute='_compute_values', store=True)

    net_premium_egp = fields.Float(string="Net Premium EGP", compute='_get_net_premium_egp', store=True)


    @api.depends('medical_policy_id.net_premium_egp', 'life_policy_id.net_premium_egp', 'motor_policy_id.net_premium_egp',
                 'fire_policy_id.net_premium_egp', 'engineering_policy_id.net_premium_egp',
                 'misc_policy_id.net_premium_egp', 'marine_policy_id.net_premium_egp')
    def _get_net_premium_egp(self):
        for record in self:
            if record.medical_policy_id:
                record.net_premium_egp = record.medical_policy_id.net_premium_egp
            elif record.life_policy_id:
                record.net_premium_egp = record.life_policy_id.net_premium_egp
            elif record.motor_policy_id:
                record.net_premium_egp = record.motor_policy_id.net_premium_egp
            elif record.fire_policy_id:
                record.net_premium_egp = record.fire_policy_id.net_premium_egp
            elif record.engineering_policy_id:
                record.net_premium_egp = record.engineering_policy_id.net_premium_egp
            elif record.misc_policy_id:
                record.net_premium_egp = record.misc_policy_id.net_premium_egp
            elif record.marine_policy_id:
                record.net_premium_egp = record.marine_policy_id.net_premium_egp
            else:
                record.net_premium_egp = 0

    @api.depends('net_premium_egp', 'contract_line_id.basic', 'contract_line_id.comp',
                 'contract_line_id.bonus', 'contract_line_id.commission')
    def _compute_values(self):
        for record in self:
            for field in ['basic', 'comp', 'bonus', 'commission']:
                percentage = getattr(record.contract_line_id, field)
                value = (record.net_premium_egp * percentage) / 100
                setattr(record, field, value)
