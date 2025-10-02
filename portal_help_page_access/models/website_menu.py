from odoo import models


class WebsiteMenu(models.Model):
    _inherit = 'website.menu'

    def _compute_visible(self):
        """ Override to allow portal users to see helpdesk menu item even if it's not published. """
        super(WebsiteMenu, self)._compute_visible()

        user = self.env.user
        if user.has_group('base.group_portal'):
            for menu in self:
                if menu.url and '/helpdesk' in menu.url:
                    menu.is_visible = True
