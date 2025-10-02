from werkzeug.exceptions import NotFound
from werkzeug.utils import redirect

from odoo import http
from odoo.http import request
from odoo.osv import expression

from odoo.addons.website_helpdesk.controllers.main import WebsiteHelpdesk


class PortalWebsiteHelpdesk(WebsiteHelpdesk):
    """
    Override the WebsiteHelpdesk controller to allow portal users to access
    helpdesk url even page unpublish.
    """

    @http.route(['/helpdesk', '/helpdesk/<model("helpdesk.team"):team>'], type='http', auth="public", website=True,
                sitemap=True)
    def website_helpdesk_teams(self, team=None, **kwargs):
        search = kwargs.get('search')

        teams_domain = [('use_website_helpdesk_form', '=', True), ('website_id', '=', request.website.id)]

        # ============= Allow portal users to access unpublished teams =============
        user = request.env.user
        if not (user.has_group('helpdesk.group_helpdesk_manager') or user.has_group('base.group_portal')):
            if team and not team.is_published:
                raise NotFound()
            teams_domain = expression.AND([teams_domain, [('website_published', '=', True)]])

        teams = request.env['helpdesk.team'].search(teams_domain, order="id asc")
        if not teams:
            raise NotFound()

        if not team:
            if len(teams) != 1:
                return request.render("website_helpdesk.helpdesk_all_team", {'teams': teams})
            redirect_url = teams.website_url
            if teams.show_knowledge_base and not kwargs.get('contact_form'):
                redirect_url += '/knowledgebase'
            elif kwargs.get('contact_form'):
                redirect_url += '/?contact_form=1'
            return redirect(redirect_url)

        if team.show_knowledge_base and not kwargs.get('contact_form'):
            return redirect(team.website_url + '/knowledgebase')

        result = self.get_helpdesk_team_data(team or teams[0], search=search)
        result['multiple_teams'] = len(teams) > 1
        return request.render("website_helpdesk.team", result)


