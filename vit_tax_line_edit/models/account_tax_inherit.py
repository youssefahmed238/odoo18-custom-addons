from odoo import api, models, fields, Command, _
from odoo.tools import frozendict
from odoo.exceptions import UserError
import uuid
from collections import defaultdict
from contextlib import contextmanager


class AccountTax(models.Model):
    _inherit = 'account.tax'

    @api.model
    def _get_move_from_line_dict(self, base_line):
        """Return account.move record or False. Handles int id, record proxy or dict/value forms."""
        move_val = base_line.get('record') and base_line['record'].move_id
        if not move_val:
            return False
        try:
            if hasattr(move_val, 'id'):
                return move_val
        except Exception:
            pass
        try:
            move_id = int(move_val)
            return self.env['account.move'].browse(move_id)
        except Exception:
            return self.env['account.move'].browse(move_val)

    @api.model
    def _prepare_base_line_tax_repartition_grouping_key(self, base_line, base_line_grouping_key, tax_data,
                                                        tax_rep_data):
        move = self._get_move_from_line_dict(base_line)
        if move and not move.journal_id.per_line_calc:
            return super(AccountTax, self)._prepare_base_line_tax_repartition_grouping_key(
                base_line, base_line_grouping_key, tax_data, tax_rep_data
            )

        tax = tax_data['tax']
        tax_rep = tax_rep_data['tax_rep']

        unique_key = f"{base_line.get('id', 'no_line')}_{tax.id}_{tax_rep.id}_{uuid.uuid4()}"

        base_line_grouping_key = {**base_line_grouping_key}

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
            '__force_unique': unique_key,
            'base_line_id': base_line.get('id'),
        }

    @api.model
    def _prepare_tax_line_repartition_grouping_key(self, tax_line):
        move = self._get_move_from_line_dict(tax_line)
        if move and not move.journal_id.per_line_calc:
            return super(AccountTax, self)._prepare_tax_line_repartition_grouping_key(tax_line)

        tax_id = tax_line['tax_ids'].ids[0] if tax_line.get('tax_ids') else 'no_tax'
        tax_rep_id = tax_line['tax_repartition_line_id'].id if tax_line.get('tax_repartition_line_id') else 'no_rep'
        base_line_id = tax_line.get('id', 'no_line')

        unique_key = f"{base_line_id}_{tax_id}_{tax_rep_id}_{uuid.uuid4()}"

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
            'base_line_id': tax_line.get('base_line_id') or False,
        }

    @api.model
    def _aggregate_base_line_tax_details(self, base_line, grouping_function):
        """ Modified: Prevent merging of taxes — each tax line remains unique. """
        move = self._get_move_from_line_dict(base_line)
        if move and not move.journal_id.per_line_calc:
            return super(AccountTax, self)._aggregate_base_line_tax_details(base_line, grouping_function)

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
            if 'currency' not in base_line or not base_line['currency']:
                base_line['currency'] = self.env.company.currency_id

            if tax_data:
                if 'currency' not in tax_data or not tax_data['currency']:
                    tax_data['currency'] = base_line['currency']
                if 'delta_currency' not in tax_data or not tax_data['delta_currency']:
                    tax_data['delta_currency'] = base_line['currency']

            defaults = {
                'price_include': False,
                'tax_ids': [],
                'currency': base_line.get('currency'),
                '__force_unique': str(uuid.uuid4()),
            }

            grouping_key = grouping_function(base_line, tax_data) or {}
            for k, v in defaults.items():
                grouping_key.setdefault(k, v)

            if isinstance(grouping_key, dict):
                grouping_key = dict(grouping_key)
            grouping_key['__force_unique'] = str(uuid.uuid4())
            grouping_key = frozendict(grouping_key)

            already_accounted = grouping_key in values_per_grouping_key
            values = values_per_grouping_key[grouping_key]

            for key in ['target_base_amount', 'target_base_amount_currency',
                        'target_tax_amount', 'target_tax_amount_currency', 'raw_total_excluded',
                        'target_total_excluded', 'target_total_excluded_currency', 'raw_total_excluded_currency']:
                values.setdefault(key, 0.0)

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

        return values_per_grouping_key

    @api.model
    def _prepare_tax_lines(self, base_lines, company, tax_lines=None):
        tax_lines_mapping = defaultdict(lambda: {
            'tax_base_amount': 0.0,
            'amount_currency': 0.0,
            'balance': 0.0,
            'name': '',
            'base_line_id': False,
        })

        base_lines_to_update = []

        for base_line in base_lines:
            move = self._get_move_from_line_dict(base_line)
            if move and not move.journal_id.per_line_calc:
                return super(AccountTax, self)._prepare_tax_lines(base_lines, company, tax_lines)

            sign = base_line['sign']
            tax_tag_invert = base_line['tax_tag_invert']
            tax_details = base_line['tax_details']

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
                    tax_line['base_line_id'] = base_line.get('id')

        tax_lines_mapping = {frozendict(key): v for key, v in tax_lines_mapping.items()}

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

        return {
            'tax_lines_to_add': tax_lines_to_add,
            'tax_lines_to_delete': tax_lines_to_delete,
            'tax_lines_to_update': tax_lines_to_update,
            'base_lines_to_update': base_lines_to_update,
        }


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_automatic_balancing_account(self):
        self.ensure_one()
        if not self.journal_id.per_line_calc:
            return super(AccountMove, self)._get_automatic_balancing_account()
        return (
                self.journal_id.default_account_id.id
                or self.company_id.account_journal_suspense_account_id.id
        )

    @contextmanager
    def _sync_unbalanced_lines(self, container):
        def has_tax(move):
            return bool(move.line_ids.tax_ids)

        move_had_tax = {move: has_tax(move) for move in container['records']}
        yield  # Execute main logic first

        for move in (x for x in container['records'] if x.state != 'posted'):

            if not has_tax(move) and not move_had_tax.get(move):
                continue

            if move_had_tax.get(move) and not has_tax(move):
                move.line_ids.filtered('tax_line_id').unlink()
                move.line_ids.tax_tag_ids = [Command.set([])]

            balance_name = _('Automatic Balancing Line')

            if not move.journal_id.per_line_calc:
                existing_balancing_line = move.line_ids.filtered(lambda line: line.name == balance_name)
                if existing_balancing_line:
                    existing_balancing_line.balance = existing_balancing_line.amount_currency = 0.0

                # Create an automatic balancing line to make sure the entry can be saved/posted.
                # If such a line already exists, we simply update its amounts.
                unbalanced_moves = self._get_unbalanced_moves({'records': move})
                if isinstance(unbalanced_moves, list) and len(unbalanced_moves) == 1:
                    dummy, debit, credit = unbalanced_moves[0]

                    vals = {'balance': credit - debit}
                    if existing_balancing_line:
                        existing_balancing_line.write(vals)
                    else:
                        vals.update({
                            'name': balance_name,
                            'move_id': move.id,
                            'account_id': move._get_automatic_balancing_account(),
                            'currency_id': move.currency_id.id,
                            # A balancing line should never have default taxes applied to it, it doesn't work well and wouldn't make much sense.
                            'tax_ids': False,
                        })
                        self.env['account.move.line'].create(vals)
            else:

                base_lines = move.line_ids.filtered(lambda l: not l.tax_line_id and l.name != balance_name)

                sequence = 1
                for base_line in base_lines:
                    unbalanced_moves = self._get_unbalanced_moves({'records': move})

                    if isinstance(unbalanced_moves, list) and len(unbalanced_moves) == 1:
                        self._create_balancing_line(move, base_line, balance_name)

                    base_line.sequence = sequence
                    sequence += 1

                    if base_line.balance_line_id:
                        base_line.balance_line_id.sequence = sequence
                        sequence += 1

                    for tax_line in move.line_ids.filtered(lambda l: l.tax_line_id and l.base_line_id == base_line):
                        tax_line.sequence = sequence
                        sequence += 1

    def _create_balancing_line(self, move, base_line, balance_name):
        related_lines = move.line_ids.filtered(lambda l: l == base_line or l.base_line_id == base_line)

        debit = sum(l.balance for l in related_lines if l.balance > 0)
        credit = -sum(l.balance for l in related_lines if l.balance < 0)
        diff = round(debit - credit, 2)

        if base_line.balance_line_id:
            if abs(diff) < 0.0001 or abs(base_line.balance_line_id.balance) == abs(diff):
                return
            old_line = base_line.balance_line_id
            base_line.balance_line_id = False
            old_line.unlink()

        vals = {
            'name': balance_name,
            'move_id': move.id,
            'account_id': move._get_automatic_balancing_account(),
            'currency_id': move.currency_id.id,
            'tax_ids': False,
            'balance': credit - debit,
        }

        new_line = self.env['account.move.line'].create(vals)
        base_line.balance_line_id = new_line


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    base_line_id = fields.Many2one('account.move.line', string='Base Line', ondelete='cascade')
    balance_line_id = fields.Many2one('account.move.line', string='Balance Line', ondelete='cascade')
