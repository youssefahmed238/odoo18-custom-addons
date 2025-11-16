from odoo import models, fields, api
from odoo.exceptions import ValidationError


class InsuranceContract(models.Model):
    _name = 'insurance.contract'
    _description = 'Insurance Contract'

    name = fields.Char(default='New', readonly=True, store=True)
    vendor_id = fields.Many2one('res.partner', string='Vendor', required=True)
    date = fields.Date(required=True, default=fields.Date.context_today)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('cancel', 'Cancel'),
    ], string='Status', default='draft', required=True)

    line_ids = fields.One2many('insurance.contract.line', 'contract_id', string='Contract Lines')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('insurance.contract') or 'New'
        return super(InsuranceContract, self).create(vals)

    def action_draft(self):
        self.state = 'draft'

    def action_confirm(self):
        self.state = 'confirm'

    def action_cancel(self):
        self.state = 'cancel'


class InsuranceContractLine(models.Model):
    _name = 'insurance.contract.line'
    _description = 'Insurance Contract Line'

    contract_id = fields.Many2one('insurance.contract', string='Contract', required=True)

    start_date = fields.Date(string='From', required=True)
    end_date = fields.Date(string='To', required=True)

    basic = fields.Float(string='Basic', required=True)
    commission = fields.Float(string='Commission', required=True)
    bonus = fields.Float(string='Bonus', required=True)

    layer_1 = fields.Float(string='Layer 1', required=True)
    layer_2 = fields.Float(string='Layer 2', required=True)
    layer_3 = fields.Float(string='Layer 3', required=True)
    layer_4 = fields.Float(string='Layer 4', required=True)

    @api.constrains('end_date', 'start_date')
    def _check_dates(self):
        for record in self:
            if record.end_date < record.start_date:
                raise ValidationError("End date must be after start date.")

    @api.constrains('basic', 'commission', 'bonus', 'layer_1', 'layer_2', 'layer_3', 'layer_4')
    def _check_percentage_values(self):
        for record in self:
            fields_to_check = {
                'Basic': record.basic,
                'Commission': record.commission,
                'Bonus': record.bonus,
                'Layer 1': record.layer_1,
                'Layer 2': record.layer_2,
                'Layer 3': record.layer_3,
                'Layer 4': record.layer_4,
            }
            for field_name, value in fields_to_check.items():
                if not (0 <= value <= 100):
                    raise ValidationError(f"Field {field_name} must be between 0 and 100.")
