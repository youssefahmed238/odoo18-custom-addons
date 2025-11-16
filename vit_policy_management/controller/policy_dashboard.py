from odoo import http
from odoo.http import request

class PolicyDashboardController(http.Controller):

    @http.route('/policy/dashboard', type='json', auth='user')
    def get_policy_dashboard_data(self):
        policies = request.env['policy.management'].sudo().search([])
        total = len(policies)
        running = sum(1 for p in policies if p.current)
        expired = total - running

        return {
            'total_policies': total,
            'running_policies': running,
            'expired_policies': expired,
        }
