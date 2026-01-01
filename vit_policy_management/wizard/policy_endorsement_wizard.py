from odoo import api, fields, models
from odoo.exceptions import UserError


class PolicyEndorsementWizard(models.TransientModel):
    _name = "policy.endorsement.wizard"
    _description = "Universal Policy Endorsement Wizard"

    # Reference to ANY policy model
    policy_ref = fields.Reference(
        selection=lambda self: self._get_policy_models(),
        string="Policy",
        required=True
    )

    name = fields.Char(string="Policy Name", readonly=True)
    transaction_type = fields.Selection([
        ('non_technical', 'Technical Add'),
        ('technical_refund', 'Technical Refund'),
        ('technical_borndead', 'Technical Born Dead'),
        ('cancel', 'Technical Cancel With Refund'),
        ('period_extension', 'Technical Period Extension'),
        ('cancel_add_end', 'Technical Cancel Add End'),
        ('cancel_refund_end', 'Technical Cancel Refund End'),
    ], required=True)

    effective_date_from = fields.Date(required=True)
    endorsement_reason = fields.Char()
    text_reason = fields.Char()

    # ----------------------------------------------------
    # POLICY MODEL DETECTION
    # ----------------------------------------------------
    def _get_policy_models(self):
        return [
            ('medical.policy', 'Medical Policy'),
            ('engineering.policy', 'Engineering Policy'),
            ('fire.policy', 'Fire Policy'),
            ('life.policy', 'Life Policy'),
            ('marine.policy', 'Marine Policy'),
            ('misc.policy', 'Misc Policy'),
            ('motor.policy', 'Motor Policy'),
        ]

    # ----------------------------------------------------
    # CONFIRM ENDORSEMENT
    # ----------------------------------------------------
    def action_confirm(self):
        self.ensure_one()

        policy = self.policy_ref
        if not policy:
            raise UserError("No policy selected.")

        # Store the original values for net_premium_egp and gross_premium_egp
        net_premium_egp = policy.net_premium_egp
        gross_premium_egp = policy.gross_premium_egp

        # Create values for new endorsement
        new_vals = {
            "name": f"{policy.name} - Endorsement",
            "parent_id": policy.id,
            "transaction_type": self.transaction_type,
            "effective_date_from": self.effective_date_from,
            "endorsement_reason": self.endorsement_reason,
            "text_reason": self.text_reason,
            "state": "draft",

            "insurer": policy.insurer.id,
            "product": policy.product.id,
            "customer": policy.customer.id,
            "business_source_id": policy.business_source_id.id,
            "insured": policy.insured.id,

            # Set the new fields with zero values
            "net_premium_egp": 0,
            "gross_premium_egp": 0,

            # Store the original values in the new fields
            "net_before_parent_amount": net_premium_egp,
            "gross_before_parent_amount": gross_premium_egp,
        }

        # Copy original policy → new endorsement
        new_policy = policy.copy(new_vals)

        # Open the new policy
        return {
            "type": "ir.actions.act_window",
            "res_model": policy._name,
            "view_mode": "form",
            "res_id": new_policy.id,
            "target": "current",
        }
