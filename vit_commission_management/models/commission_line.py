from odoo import models, fields, api


class CommissionLine(models.Model):
    _name = 'commission.line'
    _description = 'Commission Line'
    _rec_name = 'policy_name'

    medical_policy_id = fields.Many2one('medical.policy', string='Policy', ondelete='cascade')
    life_policy_id = fields.Many2one('life.policy', string='Policy', ondelete='cascade')
    motor_policy_id = fields.Many2one('motor.policy', string='Policy', ondelete='cascade')
    fire_policy_id = fields.Many2one('fire.policy', string='Policy', ondelete='cascade')
    engineering_policy_id = fields.Many2one('engineering.policy', string='Policy', ondelete='cascade')
    misc_policy_id = fields.Many2one('misc.policy', string='Policy', ondelete='cascade')
    marine_policy_id = fields.Many2one('marine.policy', string='Policy', ondelete='cascade')

    policy_name = fields.Char(string='Policy', compute='_get_policy_values', store=True)
    insurer = fields.Many2one('res.partner', string='Insurer', compute='_get_policy_values', store=True)

    apply_commission = fields.Boolean(string='Apply Commission', compute='_get_policy_values', store=True)
    policy_total_amount = fields.Float(string='Policy Total Amount', compute='_get_policy_values', store=True)

    net_premium_egp = fields.Float(string="Net Premium EGP", compute='_get_policy_values', store=True)

    invoice_id = fields.Many2one('account.move', string='Invoice')

    contract_line_id = fields.Many2one('insurance.contract.line', string='Contract', ondelete='cascade')

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

    def _get_policy(self):
        return (
                self.medical_policy_id or self.life_policy_id or self.motor_policy_id or
                self.fire_policy_id or self.engineering_policy_id or
                self.misc_policy_id or self.marine_policy_id
        )

    @api.depends(*(f"{rel}.{field}" for rel in [
        'medical_policy_id', 'life_policy_id', 'motor_policy_id',
        'fire_policy_id', 'engineering_policy_id', 'misc_policy_id', 'marine_policy_id'
    ] for field in ['insurer', 'net_premium_egp', 'apply_commission', 'total_amount']))
    def _get_policy_values(self):
        for record in self:
            policy = record._get_policy()

            if policy:
                record.policy_name = policy.name
                record.insurer = policy.insurer
                record.apply_commission = policy.apply_commission
                record.policy_total_amount = policy.total_amount
                record.net_premium_egp = policy.net_premium_egp
            else:
                record.net_premium_egp = 0

    @api.depends(
        'net_premium_egp', 'apply_commission',
        'basic_p', 'comp_p', 'transportation_comm_p',
        'bonus_p', 'commission_p'
    )
    def _compute_values(self):
        for record in self:
            if record.apply_commission and record.contract_line_id:
                record.basic = (record.net_premium_egp * record.basic_p) / 100
                record.comp = (record.net_premium_egp * record.comp_p) / 100
                record.transportation_comm = (record.net_premium_egp * record.transportation_comm_p) / 100
                record.bonus = (record.net_premium_egp * record.bonus_p) / 100
                record.commission = (record.net_premium_egp * record.commission_p) / 100

                record.total_amount = (
                        record.basic + record.comp +
                        record.transportation_comm + record.bonus +
                        record.commission
                )
            else:
                record.total_amount = record.policy_total_amount

            for line in record.invoice_id.invoice_line_ids:
                if line.product_id == self.env.ref('vit_commission_management.product_commission_product'):
                    line.price_unit = record.total_amount

    @api.model
    def create(self, vals):
        """ Override create to create invoice when commission line is created """
        commission_line = super(CommissionLine, self).create(vals)

        commission_line.invoice_id = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'commission_line_id': commission_line.id,
            'medical_policy_id': commission_line.medical_policy_id.id,
            'life_policy_id': commission_line.life_policy_id.id,
            'motor_policy_id': commission_line.motor_policy_id.id,
            'fire_policy_id': commission_line.fire_policy_id.id,
            'engineering_policy_id': commission_line.engineering_policy_id.id,
            'misc_policy_id': commission_line.misc_policy_id.id,
            'marine_policy_id': commission_line.marine_policy_id.id,
            'partner_id': commission_line.insurer.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.env.ref('vit_commission_management.product_commission_product').id,
                'quantity': 1,
                'price_unit': commission_line.total_amount,
            })],
        })

        return commission_line
