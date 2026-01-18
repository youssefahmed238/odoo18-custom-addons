# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Employee Loan Management Accounting Extend',
    'summary': """Employee Loan Management Accounting Extend""",
    'description': """Employee Loan Management Accounting Extend. 
                      Add Accounting Page inside hr.loan form view to manage the company employees loan payment proces""",
    'author': 'VarietyIT , Dev: Mohamed Nasr',
    'website': 'https://varietyit.com/',
    'category': 'Generic Modules/Human Resources',
    'version': '1.8',
    'license': 'OPL-1',
    'depends': ['hr_payroll', 'hr', 'hr_contract', 'saudi_hr_loan'],
    'data': [
        'views/hr_loan_view_inherit.xml',
        'views/hr_loan_operation_view_inherit.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
