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

    net_premium = fields.Float(string="Net Premium", compute='_get_net_premium', store=True)

    @api.depends('medical_policy_id.net_premium', 'life_policy_id.net_premium', 'motor_policy_id.net_premium',
                 'fire_policy_id.net_premium', 'engineering_policy_id.net_premium',
                 'misc_policy_id.net_premium', 'marine_policy_id.net_premium')
    def _get_net_premium(self):
        for record in self:
            if record.medical_policy_id:
                record.net_premium = record.medical_policy_id.net_premium
            elif record.life_policy_id:
                record.net_premium = record.life_policy_id.net_premium
            elif record.motor_policy_id:
                record.net_premium = record.motor_policy_id.net_premium
            elif record.fire_policy_id:
                record.net_premium = record.fire_policy_id.net_premium
            elif record.engineering_policy_id:
                record.net_premium = record.engineering_policy_id.net_premium
            elif record.misc_policy_id:
                record.net_premium = record.misc_policy_id.net_premium
            elif record.marine_policy_id:
                record.net_premium = record.marine_policy_id.net_premium
            else:
                record.net_premium = 0

    @api.depends('net_premium', 'contract_line_id.basic', 'contract_line_id.comp',
                 'contract_line_id.bonus', 'contract_line_id.commission')
    def _compute_values(self):
        for record in self:
            for field in ['basic', 'comp', 'bonus', 'commission']:
                percentage = getattr(record.contract_line_id, field)
                value = (record.net_premium * percentage) / 100
                setattr(record, field, value)
