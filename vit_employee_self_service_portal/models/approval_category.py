from odoo import models, fields, api

class ApprovalCategory(models.Model):
    _inherit = "approval.category"

    # Portal control fields (stored, editable)
    show_trip_portal = fields.Boolean("Show Trip in Portal")
    show_borrow_portal = fields.Boolean("Show Borrow in Portal")
    show_general_portal = fields.Boolean("Show General in Portal")
    show_contract_portal = fields.Boolean("Show Contract in Portal")
    show_payment_portal = fields.Boolean("Show Payment in Portal")
    show_car_rental_portal = fields.Boolean("Show Car Rental in Portal")
    show_job_referral_portal = fields.Boolean("Show Job Referral in Portal")
    show_procurement_portal = fields.Boolean("Show Procurement in Portal")

    # Visibility helpers (computed only, no store)
    show_trip_visible = fields.Boolean(compute="_compute_visibility", store=False)
    show_borrow_visible = fields.Boolean(compute="_compute_visibility", store=False)
    show_general_visible = fields.Boolean(compute="_compute_visibility", store=False)
    show_contract_visible = fields.Boolean(compute="_compute_visibility", store=False)
    show_payment_visible = fields.Boolean(compute="_compute_visibility", store=False)
    show_car_rental_visible = fields.Boolean(compute="_compute_visibility", store=False)
    show_job_referral_visible = fields.Boolean(compute="_compute_visibility", store=False)
    show_procurement_visible = fields.Boolean(compute="_compute_visibility", store=False)

    @api.depends("name")
    def _compute_visibility(self):
        """Control which portal fields should appear depending on the category name."""
        for rec in self:
            rec.show_trip_visible = rec.name == "Business Trip"
            rec.show_borrow_visible = rec.name == "Borrow Items"
            rec.show_general_visible = rec.name == "General Approval"
            rec.show_contract_visible = rec.name == "Contract Approval"
            rec.show_payment_visible = rec.name == "Payment Application"
            rec.show_car_rental_visible = rec.name == "Car Rental Application"
            rec.show_job_referral_visible = rec.name == "Job Referral Award"
            rec.show_procurement_visible = rec.name == "Procurement"
