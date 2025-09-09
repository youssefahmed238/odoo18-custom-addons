from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.form import WebsiteForm


class WebsiteHelpdeskFormController(WebsiteForm):

    def extract_data(self, model, values):
        asset_id = values.pop('asset_id', None)
        location_id = values.pop('location_id', None)

        data = super(WebsiteHelpdeskFormController, self).extract_data(model, values)

        if model.model == 'helpdesk.ticket':
            if asset_id:
                try:
                    data['record']['asset_id'] = int(asset_id)
                except (ValueError, TypeError):
                    pass

            if location_id:
                try:
                    data['record']['location_id'] = int(location_id)
                except (ValueError, TypeError):
                    pass

        return data
