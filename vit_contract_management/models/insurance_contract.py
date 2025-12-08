from odoo import models, fields, api
from odoo.exceptions import ValidationError


class InsuranceContract(models.Model):
    _name = 'insurance.contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Insurance Contract'

    name = fields.Char(default='New', readonly=True, store=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Insurer', required=True, tracking=True,
                                 domain=[('insurance_contract_id', '=', False)])
    date = fields.Date(required=True, default=fields.Date.context_today, tracking=True)

    start_date = fields.Date(string='From', required=True, default=fields.Date.context_today, tracking=True)
    end_date = fields.Date(string='To', required=True, tracking=True,
                           default=lambda self: fields.Date.add(fields.Date.context_today(self), months=12))

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'In Progress'),
        ('expired', 'Expired'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', required=True, tracking=True)

    line_ids = fields.One2many('insurance.contract.line', 'contract_id', string='Contract Lines')

    @api.constrains('end_date', 'start_date')
    def _check_dates(self):
        for record in self:
            if record.end_date <= record.start_date:
                raise ValidationError("End date must be after start date.")
            if record.end_date <= fields.Date.context_today(self):
                raise ValidationError("End date must be after today's date.")

    @api.constrains('line_ids')
    def _check_overlapping_lines(self):
        """ Ensure no overlapping insurance lines and products in contract lines. """
        for contract in self:
            seen = set()
            for line in contract.line_ids:
                for product in line.insurance_products:
                    key = (line.insurance_line.id, product.id)
                    if key in seen:
                        raise ValidationError(f"Overlapping insurance line '{line.insurance_line.name}' "
                                              f"with product '{product.name}' in contract lines.")
                    seen.add(key)

    @api.model
    def check_expired_contracts(self):
        today = fields.Date.context_today(self)

        for contract in self:
            if contract.state == 'confirm' and contract.end_date < today:
                contract.action_expired()

            # if 75% of the contract duration has passed, send notification
            duration = (contract.end_date - contract.start_date).days
            elapsed = (today - contract.start_date).days
            if self.state == 'confirm' and (elapsed / duration) >= 0.75:

                self.env['mail.activity'].create({
                    'activity_type_id': self.env.ref('mail.mail_activity_data_email').id,
                    'note': f'Contract {contract.name} is nearing expiry on {contract.end_date}',
                    'user_id': contract.create_uid.id,
                    'res_id': contract.id,
                    'res_model_id': self.env['ir.model']._get('insurance.contract').id,
                })

                self.message_post(
                    subject='Contract Nearing Expiry',
                    body=f'The insurance contract {contract.name} is nearing its expiry date of {contract.end_date}.',
                    message_type='email',
                )


    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('insurance.contract') or 'New'
        return super(InsuranceContract, self).create(vals)

    def unlink(self):
        for rec in self:
            # Ensure partner does not keep old contract reference
            if rec.partner_id.insurance_contract_id == rec:
                rec.partner_id.insurance_contract_id = False
        return super(InsuranceContract, self).unlink()

    def action_draft(self):
        if self.partner_id.insurance_contract_id == self:
            self.partner_id.insurance_contract_id = False

        self.state = 'draft'

    def action_confirm(self):
        if self.partner_id.insurance_contract_id:
            raise ValidationError("The selected insurer already has an active insurance contract.")

        self.partner_id.insurance_contract_id = self.id
        self.state = 'confirm'

        self._check_dates()
        self.check_expired_contracts()

    def action_expired(self):
        if self.partner_id.insurance_contract_id == self:
            self.partner_id.insurance_contract_id = False

        self.state = 'expired'

    def action_cancel(self):
        if self.partner_id.insurance_contract_id == self:
            self.partner_id.insurance_contract_id = False

        self.state = 'cancel'


class InsuranceContractLine(models.Model):
    _name = 'insurance.contract.line'
    _description = 'Insurance Contract Line'

    contract_id = fields.Many2one('insurance.contract', string='Contract', required=True)

    insurance_line = fields.Many2one('policy.category', string='Insurance Line', required=True)
    insurance_products = fields.Many2many('policy.product', string='Insurance Products', required=True,
                                          domain="[('category_id', '=', insurance_line)]")

    basic = fields.Float(string='Basic %', required=True)
    comp = fields.Float(string='Comp %', required=True)
    transportation_comm = fields.Float(string='Transportation %', required=True)
    bonus = fields.Float(string='Bonus %', required=True)
    commission = fields.Float(string='Commission %', required=True)

    layer_1 = fields.Float(string='Layer 1 %', required=True)
    layer_2 = fields.Float(string='Layer 2 %', required=True)
    layer_3 = fields.Float(string='Layer 3 %', required=True)
    layer_4 = fields.Float(string='Layer 4 %', required=True)

    FIELDS_TO_CHECK = [
        'basic', 'comp', 'transportation_comm', 'bonus', 'commission',
        'layer_1', 'layer_2', 'layer_3', 'layer_4',
    ]

    @api.constrains(*FIELDS_TO_CHECK)
    def _check_percentage_values(self):
        for record in self:
            fields_to_check = {
                'Basic %': record.basic,
                'Comp %': record.comp,
                'Transportation %': record.transportation_comm,
                'Bonus %': record.bonus,
                'Commission %': record.commission,
                'Layer 1 %': record.layer_1,
                'Layer 2 %': record.layer_2,
                'Layer 3 %': record.layer_3,
                'Layer 4 %': record.layer_4,
            }
            for field_name, value in fields_to_check.items():
                if not (0 <= value <= 100):
                    raise ValidationError(f"Field {field_name} must be between 0 and 100.")
