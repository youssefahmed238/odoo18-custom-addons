from odoo import models, fields, api
from odoo.exceptions import ValidationError


class InsuranceContract(models.Model):
    _name = 'insurance.contract'
    _description = 'Insurance Contract'

    name = fields.Char(default='New', readonly=True, store=True)
    partner_id = fields.Many2one('res.partner', string='Insurer', required=True,
                                 domain=[('insurance_contract_id', '=', False)])
    date = fields.Date(required=True, default=fields.Date.context_today)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'In Progress'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', required=True)

    line_ids = fields.One2many('insurance.contract.line', 'contract_id', string='Contract Lines')

    @api.constrains('line_ids')
    def _check_overlapping_lines(self):
        for contract in self:
            lines = contract.line_ids
            for i, line1 in enumerate(lines):
                for line2 in lines[i + 1:]:
                    if (line1.start_date <= line2.start_date <= line1.end_date) or \
                            (line1.start_date <= line2.end_date <= line1.end_date):
                        if line1.insurance_line == line2.insurance_line and \
                                set(line1.insurance_products.ids).intersection(set(line2.insurance_products.ids)):
                            raise ValidationError(
                                "Overlapping contract lines with the same insurance line and products in same date range are not allowed.")

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

    def action_cancel(self):
        if self.partner_id.insurance_contract_id == self:
            self.partner_id.insurance_contract_id = False

        self.state = 'cancel'


class InsuranceContractLine(models.Model):
    _name = 'insurance.contract.line'
    _description = 'Insurance Contract Line'

    contract_id = fields.Many2one('insurance.contract', string='Contract', required=True)

    start_date = fields.Date(string='From', required=True)
    end_date = fields.Date(string='To', required=True)

    insurance_line = fields.Many2one('policy.category', string='Insurance Line', required=True)
    insurance_products = fields.Many2many('policy.product', string='Insurance Products', required=True,
                                          domain="[('category_id', '=', insurance_line)]")

    basic = fields.Float(string='Basic %', required=True)
    comp = fields.Float(string='Comp %', required=True)
    bonus = fields.Float(string='Bonus %', required=True)
    commission = fields.Float(string='Commission %', required=True)

    layer_1 = fields.Float(string='Layer 1 %', required=True)
    layer_2 = fields.Float(string='Layer 2 %', required=True)
    layer_3 = fields.Float(string='Layer 3 %', required=True)
    layer_4 = fields.Float(string='Layer 4 %', required=True)

    @api.constrains('end_date', 'start_date')
    def _check_dates(self):
        for record in self:
            if record.end_date < record.start_date:
                raise ValidationError("End date must be after start date.")

    FIELDS_TO_CHECK = [
        'basic', 'comp', 'bonus', 'commission',
        'layer_1', 'layer_2', 'layer_3', 'layer_4',
    ]

    @api.constrains(*FIELDS_TO_CHECK)
    def _check_percentage_values(self):
        for record in self:
            fields_to_check = {
                'Basic %': record.basic,
                'Comp %': record.comp,
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
