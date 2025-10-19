{
    'name': 'Website Helpdesk New Fields',
    'author': 'Youssef',
    'category': 'Website',
    'version': '18.0.0.2.0',
    'depends': ['website_helpdesk', 'vit_facility_management_config','base','web'],
    'data': [
        'views/website_helpdesk_template_inherit.xml',
        'views/helpdesk_ticket_view.xml',
        'report/asset_qrcode.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            '/website_helpdesk_new_fields/static/lib/jsqr.min.js',  # must come first
            'website_helpdesk_new_fields/static/src/scss/qr_scan.scss',
            'website_helpdesk_new_fields/static/src/js/handel_website_helpdesk_new_fields.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': True,
}
