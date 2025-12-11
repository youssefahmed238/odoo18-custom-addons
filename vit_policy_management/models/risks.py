from odoo import models, fields, api


class PolicyRisks(models.Model):
    _name = "policy.risks"
    _description = "Policy Risks"

    name = fields.Char(string="Name", required=True)

    category = fields.Many2one('policy.category', string="Category", required=True, default=1)

    medical_policy_number = fields.Many2one('medical.policy', string="Policy Number")
    life_policy_number = fields.Many2one('life.policy', string="Policy Number")
    motor_policy_number = fields.Many2one('motor.policy', string="Policy Number")
    fire_policy_number = fields.Many2one('fire.policy', string="Policy Number")
    eng_policy_number = fields.Many2one('engineering.policy', string="Policy Number")
    misc_policy_number = fields.Many2one('misc.policy', string="Policy Number")
    marine_policy_number = fields.Many2one('marine.policy', string="Policy Number")

    category_code = fields.Char(related="category.name", store=False)

    #  --------------------  fields Motor  --------------------

    possession = fields.Char("Possession")
    plate_number = fields.Char("Plate Number")
    maker = fields.Char("Maker")
    model = fields.Char("Model")
    color = fields.Char("Color")
    number_of_seats = fields.Integer("Number of Seats")
    year = fields.Integer("Year")
    body_type = fields.Char("Body Type")
    usage = fields.Char("Usage")
    cc = fields.Char("CC")
    chassis_number = fields.Char("Chassis Number")
    engine_number = fields.Char("Engine Number")
    fuel_type = fields.Char("Fuel Type")
    radio = fields.Boolean("Radio")
    air_conditioner = fields.Boolean("Air Conditioner")
    road_side = fields.Boolean("Road Side")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('cancel', 'Cancel'),
    ],
        default='draft',
        copy=False,
    )

    @api.onchange('category')
    def _onchange_category(self):
        if self.category:
            return {
                'domain': {
                    'policy_number': [
                        ('category', '=', self.category.id)
                    ]
                }
            }
        else:
            return {
                'domain': {
                    'policy_number': []
                }
            }

    def set_to_draft(self):
        self.state = 'draft'

    def set_to_cancel(self):
        self.state = 'cancel'

    def set_to_approved(self):
        self.state = 'approved'
