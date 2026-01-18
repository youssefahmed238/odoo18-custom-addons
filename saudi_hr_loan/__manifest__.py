# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Employee Loan Management',
    'summary': """Employee Loan Management""",
    'description': """Employee Loan Management also manage the installment of loan.""",
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'http://www.synconics.com',
    'category': 'Generic Modules/Human Resources',
    'version': '2.2',
    'license': 'OPL-1',
    'depends': ['hr_payroll', 'hr', 'hr_contract', ],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'data/hr_payroll_data.xml',
        'data/loan_data.xml',
        'data/cron.xml',
        'wizard/employee_loan_freeze_view.xml',
        'views/hr_loan_view.xml',
        'views/hr_skip_installment_view.xml',
        'views/hr_loan_operation_view.xml',
        'views/res_config_settings_view.xml',
        'views/emp_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': ['demo/demo.xml'],
    'images': [
        'static/description/main_screen.jpg'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
