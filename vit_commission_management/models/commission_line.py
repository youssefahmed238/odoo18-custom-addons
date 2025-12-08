from odoo import models, fields, api


class CommissionLine(models.Model):
    _name = 'commission.line'
    _description = 'Commission Line'
    _rec_name = 'contract_id'

    medical_policy_id = fields.Many2one('medical.policy', string='Policy')
    life_policy_id = fields.Many2one('life.policy', string='Policy')
    motor_policy_id = fields.Many2one('motor.policy', string='Policy')
    fire_policy_id = fields.Many2one('fire.policy', string='Policy')
    engineering_policy_id = fields.Many2one('engineering.policy', string='Policy')
    misc_policy_id = fields.Many2one('misc.policy', string='Policy')
    marine_policy_id = fields.Many2one('marine.policy', string='Policy')

    policy_name = fields.Char(string='Policy', compute='_get_policy_values', store=True)

    contract_line_id = fields.Many2one('insurance.contract.line', string='Contract', required=True, ondelete='cascade')
    insurance_line = fields.Many2one('policy.category', string='Insurance Line', required=True)
    insurance_product = fields.Many2one('policy.product', string='Insurance Product', required=True)

    contract_id = fields.Many2one('insurance.contract', string='Contract', related='contract_line_id.contract_id')
    contract_insurer = fields.Many2one(string='Insurer', related='contract_id.partner_id')
    contract_start_date = fields.Date(string='From', related='contract_id.start_date')
    contract_end_date = fields.Date(string='To', related='contract_id.end_date')

    basic_p = fields.Float(string='Basic %', related='contract_line_id.basic', readonly=False)
    comp_p = fields.Float(string='Comp %', related='contract_line_id.comp', readonly=False)
    transportation_comm_p = fields.Float(string='Transportation %', related='contract_line_id.transportation_comm',
                                         readonly=False)
    bonus_p = fields.Float(string='Bonus %', related='contract_line_id.bonus', readonly=False)
    commission_p = fields.Float(string='Commission %', related='contract_line_id.commission', readonly=False)

    layer_1_p = fields.Float(string='Layer 1 %', related='contract_line_id.layer_1', readonly=False)
    layer_2_p = fields.Float(string='Layer 2 %', related='contract_line_id.layer_2', readonly=False)
    layer_3_p = fields.Float(string='Layer 3 %', related='contract_line_id.layer_3', readonly=False)
    layer_4_p = fields.Float(string='Layer 4 %', related='contract_line_id.layer_4', readonly=False)

    basic = fields.Float(string='Basic', compute='_compute_values', store=True)
    comp = fields.Float(string='Comp', compute='_compute_values', store=True)
    transportation_comm = fields.Float(string='Transportation', compute='_compute_values', store=True)
    bonus = fields.Float(string='Bonus', compute='_compute_values', store=True)
    commission = fields.Float(string='Commission', compute='_compute_values', store=True)

    total_amount = fields.Float(string='Total Amount', compute='_compute_values', store=True)

    apply_commission = fields.Boolean(string='Apply Commission', compute='_get_policy_values', store=True)
    net_premium_egp = fields.Float(string="Net Premium EGP", compute='_get_policy_values', store=True)

    @api.depends('medical_policy_id.name',
                 'life_policy_id.name',
                 'motor_policy_id.name',
                 'fire_policy_id.name',
                 'engineering_policy_id.name',
                 'misc_policy_id.name',
                 'marine_policy_id.name',

                 'medical_policy_id.net_premium_egp',
                 'life_policy_id.net_premium_egp',
                 'motor_policy_id.net_premium_egp',
                 'fire_policy_id.net_premium_egp',
                 'engineering_policy_id.net_premium_egp',
                 'misc_policy_id.net_premium_egp',
                 'marine_policy_id.net_premium_egp',

                 'medical_policy_id.apply_commission',
                 'life_policy_id.apply_commission',
                 'motor_policy_id.apply_commission',
                 'fire_policy_id.apply_commission',
                 'engineering_policy_id.apply_commission',
                 'misc_policy_id.apply_commission',
                 'marine_policy_id.apply_commission',
                 )
    def _get_policy_values(self):
        for record in self:
            if record.medical_policy_id:
                record.policy_name = record.medical_policy_id.name
                record.apply_commission = record.medical_policy_id.apply_commission
                record.net_premium_egp = record.medical_policy_id.net_premium_egp
            elif record.life_policy_id:
                record.policy_name = record.life_policy_id.name
                record.apply_commission = record.life_policy_id.apply_commission
                record.net_premium_egp = record.life_policy_id.net_premium_egp
            elif record.motor_policy_id:
                record.policy_name = record.motor_policy_id.name
                record.apply_commission = record.motor_policy_id.apply_commission
                record.net_premium_egp = record.motor_policy_id.net_premium_egp
            elif record.fire_policy_id:
                record.policy_name = record.fire_policy_id.name
                record.apply_commission = record.fire_policy_id.apply_commission
                record.net_premium_egp = record.fire_policy_id.net_premium_egp
            elif record.engineering_policy_id:
                record.policy_name = record.engineering_policy_id.name
                record.apply_commission = record.engineering_policy_id.apply_commission
                record.net_premium_egp = record.engineering_policy_id.net_premium_egp
            elif record.misc_policy_id:
                record.policy_name = record.misc_policy_id.name
                record.apply_commission = record.misc_policy_id.apply_commission
                record.net_premium_egp = record.misc_policy_id.net_premium_egp
            elif record.marine_policy_id:
                record.policy_name = record.marine_policy_id.name
                record.apply_commission = record.marine_policy_id.apply_commission
                record.net_premium_egp = record.marine_policy_id.net_premium_egp
            else:
                record.net_premium_egp = 0

    @api.depends('net_premium_egp', 'basic_p', 'comp_p',
                 'transportation_comm_p', 'bonus_p', 'commission_p',)
    def _compute_values(self):
        for record in self:
            total = 0
            for field in ['basic', 'comp', 'transportation_comm', 'bonus', 'commission']:
                percentage = getattr(record.contract_line_id, field)
                value = (record.net_premium_egp * percentage) / 100
                total += value
                setattr(record, field, value)

            record.total_amount = total
