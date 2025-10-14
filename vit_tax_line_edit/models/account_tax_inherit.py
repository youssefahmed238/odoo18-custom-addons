from odoo import api, models, Command, _
from odoo.tools import frozendict
import uuid
from collections import defaultdict
from contextlib import contextmanager


class AccountTax(models.Model):
    _inherit = 'account.tax'

    @api.model
    def _prepare_base_line_tax_repartition_grouping_key(self, base_line, base_line_grouping_key, tax_data,
                                                        tax_rep_data):
        tax = tax_data['tax']
        tax_rep = tax_rep_data['tax_rep']

        unique_key = f"{base_line.get('id', 'no_line')}_{tax.id}_{tax_rep.id}_{uuid.uuid4()}"
        print(" DEBUG: _prepare_base_line_tax_repartition_grouping_key called")
        print("  Base Line ID:", base_line.get('id'))
        print("  Tax ID:", tax.id)
        print("   Tax Rep ID:", tax_rep.id)
        print("  Unique Key:", unique_key)

        base_line_grouping_key = {
            **base_line_grouping_key,
        }

        return {
            **base_line_grouping_key,
            'tax_repartition_line_id': tax_rep.id,
            'partner_id': base_line['partner_id'].id if base_line.get('partner_id') else None,
            'currency_id': base_line['currency_id'].id if base_line.get('currency_id') else None,
            'group_tax_id': tax_data['group'].id if tax_data.get('group') else None,
            'analytic_distribution': (
                base_line_grouping_key.get('analytic_distribution')
                if tax.analytic or not tax_rep.use_in_tax_closing
                else False
            ),
            'account_id': tax_rep_data['account'].id or base_line_grouping_key.get('account_id'),
            'tax_ids': [Command.set(tax_rep_data['taxes'].ids)],
            'tax_tag_ids': [Command.set(tax_rep_data['tax_tags'].ids)],
            '__force_unique': unique_key,  # 👈 مؤقت فقط، Python-side
        }

    @api.model
    def _prepare_tax_line_repartition_grouping_key(self, tax_line):
        tax_id = tax_line['tax_ids'].ids[0] if tax_line.get('tax_ids') else 'no_tax'
        tax_rep_id = tax_line['tax_repartition_line_id'].id if tax_line.get('tax_repartition_line_id') else 'no_rep'
        base_line_id = tax_line.get('id', 'no_line')

        unique_key = f"{base_line_id}_{tax_id}_{tax_rep_id}_{uuid.uuid4()}"
        print(" DEBUG: _prepare_tax_line_repartition_grouping_key called")
        print(f"  Base Line ID: {base_line_id}")
        print(f"   Tax ID: {tax_id}")
        print(f"  Tax Rep ID: {tax_rep_id}")
        print(f"   Unique Key: {unique_key}")

        return {
            'tax_repartition_line_id': tax_line['tax_repartition_line_id'].id,
            'partner_id': tax_line['partner_id'].id if tax_line.get('partner_id') else None,
            'currency_id': tax_line['currency_id'].id if tax_line.get('currency_id') else None,
            'group_tax_id': tax_line['group_tax_id'].id if tax_line.get('group_tax_id') else None,
            'analytic_distribution': tax_line.get('analytic_distribution'),
            'account_id': tax_line['account_id'].id if tax_line.get('account_id') else None,
            'tax_ids': [Command.set(tax_line['tax_ids'].ids)] if tax_line.get('tax_ids') else [],
            'tax_tag_ids': [Command.set(tax_line['tax_tag_ids'].ids)] if tax_line.get('tax_tag_ids') else [],
            '__force_unique': unique_key,
        }
    @api.model
    def _aggregate_base_line_tax_details(self, base_line, grouping_function):
        """ Modified: Prevent merging of taxes — each tax line remains unique. """


        print(" DEBUG: Entered _aggregate_base_line_tax_details for base_line:", base_line.get('id'))

        values_per_grouping_key = defaultdict(lambda: {
            'base_amount_currency': 0.0,
            'base_amount': 0.0,
            'raw_base_amount_currency': 0.0,
            'raw_base_amount': 0.0,
            'tax_amount_currency': 0.0,
            'tax_amount': 0.0,
            'raw_tax_amount_currency': 0.0,
            'raw_tax_amount': 0.0,
            'total_excluded_currency': 0.0,
            'total_excluded': 0.0,
            'taxes_data': [],
        })

        tax_details = base_line['tax_details']
        taxes_data = tax_details['taxes_data']

        for tax_data in (taxes_data or [None]):
            grouping_key = grouping_function(base_line, tax_data)

            #  نضيف UUID فريد لكل مفتاح لتجنب الدمج نهائيًا
            if isinstance(grouping_key, dict):
                grouping_key = dict(grouping_key)
            grouping_key['__force_unique'] = str(uuid.uuid4())  # دايمًا مفتاح مختلف
            grouping_key = frozendict(grouping_key)

            already_accounted = grouping_key in values_per_grouping_key
            values = values_per_grouping_key[grouping_key]
            values['grouping_key'] = grouping_key

            if not already_accounted:
                values['total_excluded_currency'] += tax_details['total_excluded_currency'] + tax_details[
                    'delta_total_excluded_currency']
                values['total_excluded'] += tax_details['total_excluded'] + tax_details['delta_total_excluded']

                if tax_data:
                    values['base_amount_currency'] += tax_data['base_amount_currency']
                    values['base_amount'] += tax_data['base_amount']
                    values['raw_base_amount_currency'] += tax_data['raw_base_amount_currency']
                    values['raw_base_amount'] += tax_data['raw_base_amount']
                else:
                    values['base_amount_currency'] += tax_details['total_excluded_currency'] + tax_details[
                        'delta_total_excluded_currency']
                    values['base_amount'] += tax_details['total_excluded'] + tax_details['delta_total_excluded']
                    values['raw_base_amount_currency'] += tax_details['raw_total_excluded_currency']
                    values['raw_base_amount'] += tax_details['raw_total_excluded']

            if tax_data:
                values['tax_amount_currency'] += tax_data['tax_amount_currency']
                values['tax_amount'] += tax_data['tax_amount']
                values['raw_tax_amount_currency'] += tax_data['raw_tax_amount_currency']
                values['raw_tax_amount'] += tax_data['raw_tax_amount']
                values['taxes_data'].append(tax_data)

        print(" DEBUG: Finished — unique tax lines count:", len(values_per_grouping_key))
        return values_per_grouping_key
    @api.model
    def _prepare_tax_lines(self, base_lines, company, tax_lines=None):
        print("ENTERED: _prepare_tax_lines()")
        print(f"Total base lines: {len(base_lines)}")

        tax_lines_mapping = defaultdict(lambda: {
            'tax_base_amount': 0.0,
            'amount_currency': 0.0,
            'balance': 0.0,
            'name': '',
        })

        base_lines_to_update = []

        for base_line in base_lines:
            sign = base_line['sign']
            tax_tag_invert = base_line['tax_tag_invert']
            tax_details = base_line['tax_details']

            print(f"\n Base Line ID: {base_line.get('id')} | Sign: {sign}")

            base_lines_to_update.append((
                base_line,
                {
                    'tax_tag_ids': [Command.set(base_line['tax_tag_ids'].ids)],
                    'amount_currency': sign * (
                                tax_details['total_excluded_currency'] + tax_details['delta_total_excluded_currency']),
                    'balance': sign * (tax_details['total_excluded'] + tax_details['delta_total_excluded']),
                },
            ))

            for tax_data in tax_details['taxes_data']:
                for tax_rep_data in tax_data['tax_reps_data']:
                    grouping_key = self._prepare_base_line_tax_repartition_grouping_key(
                        base_line, {}, tax_data, tax_rep_data
                    )
                    tax_line = tax_lines_mapping[frozendict(grouping_key)]
                    tax_line['name'] = base_line.get('manual_tax_line_name', tax_data['tax'].name)
                    tax_line['tax_base_amount'] += sign * tax_data['base_amount'] * (-1 if tax_tag_invert else 1)
                    tax_line['amount_currency'] += sign * tax_rep_data['tax_amount_currency']
                    tax_line['balance'] += sign * tax_rep_data['tax_amount']

                    print(f"  Tax: {tax_data['tax'].name} | RepLine ID: {tax_rep_data['tax_rep'].id}")
                    print(f"    grouping_key = {grouping_key}")
                    print(f"      tax_base_amount now = {tax_line['tax_base_amount']}")
                    print(f"      amount_currency now = {tax_line['amount_currency']}")
                    print(f"      balance now = {tax_line['balance']}")

        tax_lines_mapping = {
            frozendict(key): v
            for key, v in tax_lines_mapping.items()
        }

        tax_lines_to_update = []
        tax_lines_to_delete = []
        for tax_line in tax_lines or []:
            grouping_key = frozendict(self._prepare_tax_line_repartition_grouping_key(tax_line))
            if grouping_key in tax_lines_mapping:
                amounts = tax_lines_mapping.pop(grouping_key)
                tax_lines_to_update.append((tax_line, grouping_key, amounts))
            else:
                tax_lines_to_delete.append(tax_line)

        tax_lines_to_add = [
            {**{k: v for k, v in key.items() if k != '__force_unique'}, **values}
            for key, values in tax_lines_mapping.items()
        ]
        print("\n Summary:")
        print(f"   tax_lines_to_add: {len(tax_lines_to_add)}")
        print(f"   tax_lines_to_update: {len(tax_lines_to_update)}")
        print(f"   tax_lines_to_delete: {len(tax_lines_to_delete)}")

        return {
            'tax_lines_to_add': tax_lines_to_add,
            'tax_lines_to_delete': tax_lines_to_delete,
            'tax_lines_to_update': tax_lines_to_update,
            'base_lines_to_update': base_lines_to_update,
        }




class AccountMove(models.Model):
    _inherit = 'account.move'


    def _get_automatic_balancing_account(self):
        """ Small helper for special cases where we want to auto balance a move with a specific account. """
        self.ensure_one()
        print("\n===== DEBUG: ENTERED _get_automatic_balancing_account =====")
        print(
            f"Journal: {self.journal_id.display_name}, Default Account: {self.journal_id.default_account_id.display_name if self.journal_id.default_account_id else 'None'}")
        print(
            f"Company Suspense Account: {self.company_id.account_journal_suspense_account_id.display_name if self.company_id.account_journal_suspense_account_id else 'None'}")

        if self.journal_id.default_account_id:
            print(f"Returning Journal Default Account: {self.journal_id.default_account_id.display_name}")
            return self.journal_id.default_account_id.id

        print(f"Returning Company Suspense Account: {self.company_id.account_journal_suspense_account_id.display_name}")
        return self.company_id.account_journal_suspense_account_id.id


    @contextmanager
    def _sync_unbalanced_lines(self, container):
        def has_tax(move):
            return bool(move.line_ids.tax_ids)

        print("\n===== DEBUG: ENTERED _sync_unbalanced_lines =====")
        print(f"Container contains {len(container['records'])} moves")

        move_had_tax = {move: has_tax(move) for move in container['records']}
        for mv in container['records']:
            print(f" -> Move ID {mv.id}, Name: {mv.name}, State: {mv.state}, Has Tax: {has_tax(mv)}")

        yield  # Execute main logic first

        for move in (x for x in container['records'] if x.state != 'posted'):
            print(f"\n[DEBUG] Processing Move: {move.name} (ID: {move.id})")

            if not has_tax(move) and not move_had_tax.get(move):
                print("  ⏭ Skipping — no tax found.")
                continue

            if move_had_tax.get(move) and not has_tax(move):
                print("  Taxes removed — cleaning tax lines.")
                move.line_ids.filtered('tax_line_id').unlink()
                move.line_ids.tax_tag_ids = [Command.set([])]

            balance_name = _('Automatic Balancing Line')

            unbalanced_moves = self._get_unbalanced_moves({'records': move})
            print(f"  -> Unbalanced Moves result: {unbalanced_moves}")

            if isinstance(unbalanced_moves, list) and len(unbalanced_moves) == 1:
                dummy, debit, credit = unbalanced_moves[0]
                print(f"  Debit: {debit}, Credit: {credit}, Difference: {credit - debit}")

                vals = {
                    'name': balance_name,
                    'move_id': move.id,
                    'account_id': move._get_automatic_balancing_account(),
                    'currency_id': move.currency_id.id,
                    'tax_ids': False,
                    'balance': credit - debit,
                }

                print("  Creating new automatic balancing line...")
                new_line = self.env['account.move.line'].create(vals)
                print(f"  Created new balancing line: ID={new_line.id}, Account={new_line.account_id.display_name}")

        print("===== DEBUG: EXITED _sync_unbalanced_lines =====\n")

