{
    'name': 'Employee Self Service Portal',
    'version': '18.1',
    'summary': 'Employee Self Service Portal',
    'author': 'Ahmed Mohamed',
    'description': 'All Portal Modules',
    'license': 'LGPL-3',
    'depends': ['base', 'portal', 'hr_holidays','hr_attendance','hr_payroll','approvals'],
    'data': [
        'secuirty/ir.model.access.csv',
        'secuirty/record_rules.xml',
        'views/attendance_portal_templates.xml',
        'views/leaves_portal_templates.xml',
        'views/payslip_portal_templates.xml',
        'views/hr_employee_views.xml',
        'views/aproval_portal_templates.xml',
        'views/approval_category_views.xml',

        # 'views/portal.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'vit_employee_self_service_portal/static/src/js/*',
            'vit_employee_self_service_portal/static/src/scss/*',
        ]
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
