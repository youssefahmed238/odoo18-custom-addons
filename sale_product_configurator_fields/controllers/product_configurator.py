from odoo import http
from odoo.http import request
from datetime import datetime
from odoo.addons.sale.controllers.product_configurator import SaleProductConfiguratorController


class SaleProductConfiguratorFieldsController(SaleProductConfiguratorController):

    @http.route(route='/sale/product_configurator/get_costume_values', type='json', auth='user')
    def sale_product_configurator_get_values(
        self,
        product_template_id,
        quantity,
        currency_id,
        so_date,
        product_uom_id=None,
        company_id=None,
        pricelist_id=None,
        ptav_ids=None,
        only_main_product=False,
        **kwargs,
    ):
        """ Override to include accessory and alternative products in the response """

        if company_id:
            request.update_context(allowed_company_ids=[company_id])
        product_template = self._get_product_template(product_template_id)

        combination = request.env['product.template.attribute.value']
        if ptav_ids:
            combination = request.env['product.template.attribute.value'].browse(ptav_ids).filtered(
                lambda ptav: ptav.product_tmpl_id.id == product_template_id
            )
            # Set missing attributes (unsaved no_variant attributes, or new attribute on existing product)
            unconfigured_ptals = (
                    product_template.attribute_line_ids - combination.attribute_line_id).filtered(
                lambda ptal: ptal.attribute_id.display_type != 'multi')
            combination += unconfigured_ptals.mapped(
                lambda ptal: ptal.product_template_value_ids._only_active()[:1]
            )
        if not combination:
            combination = product_template._get_first_possible_combination()
        currency = request.env['res.currency'].browse(currency_id)
        pricelist = request.env['product.pricelist'].browse(pricelist_id)
        so_date = datetime.fromisoformat(so_date)

        return dict(
            products=[
                dict(
                    **self._get_product_information(
                        product_template,
                        combination,
                        currency,
                        pricelist,
                        so_date,
                        quantity=quantity,
                        product_uom_id=product_uom_id,
                        **kwargs,
                    ),
                )
            ],
            optional_products=[
                dict(
                    **self._get_product_information(
                        optional_product_template,
                        optional_product_template._get_first_possible_combination(
                            parent_combination=combination
                        ),
                        currency,
                        pricelist,
                        so_date,
                        # giving all the ptav of the parent product to get all the exclusions
                        parent_combination=product_template.attribute_line_ids. \
                            product_template_value_ids,
                        **kwargs,
                    ),
                    parent_product_tmpl_id=product_template.id,
                ) for optional_product_template in product_template.optional_product_ids if
                self._should_show_product(optional_product_template, combination)
            ] if not only_main_product else [],
            accessory_products=[
                dict(
                    **self._get_product_information(
                        accessory_product.product_tmpl_id,
                        accessory_product.product_tmpl_id._get_first_possible_combination(
                            parent_combination=combination
                        ),
                        currency,
                        pricelist,
                        so_date,
                        parent_combination=product_template.attribute_line_ids. \
                            product_template_value_ids,
                        **kwargs,
                    ),
                    parent_product_tmpl_id=product_template.id,
                    product_type='accessory'
                ) for accessory_product in product_template.accessory_product_ids if
                self._should_show_product(accessory_product.product_tmpl_id, combination)
            ] if not only_main_product else [],
            alternative_products=[
                dict(
                    **self._get_product_information(
                        alternative_product_template,
                        alternative_product_template._get_first_possible_combination(
                            parent_combination=combination
                        ),
                        currency,
                        pricelist,
                        so_date,
                        parent_combination=product_template.attribute_line_ids. \
                            product_template_value_ids,
                        **kwargs,
                    ),
                    parent_product_tmpl_id=product_template.id,
                    product_type='alternative'
                ) for alternative_product_template in product_template.alternative_product_ids if
                self._should_show_product(alternative_product_template, combination)
            ] if not only_main_product else [],
            currency_id=currency_id,
        )

    @http.route(route='/sale/product_configurator/get_costume_optional_products', type='json', auth='user')
    def sale_product_configurator_get_costume_optional_products(
        self,
        product_template_id,
        ptav_ids,
        parent_ptav_ids,
        currency_id,
        so_date,
        company_id=None,
        pricelist_id=None,
        **kwargs,
    ):
        """ Return all product types (optional, accessory, alternative) for the given product template """
        
        if company_id:
            request.update_context(allowed_company_ids=[company_id])
        
        product_template = self._get_product_template(product_template_id)
        parent_combination = request.env['product.template.attribute.value'].browse(
            parent_ptav_ids + ptav_ids
        )
        currency = request.env['res.currency'].browse(currency_id)
        pricelist = request.env['product.pricelist'].browse(pricelist_id)
        
        # Get optional products (original behavior)
        optional_products = [
            dict(
                **self._get_product_information(
                    optional_product_template,
                    optional_product_template._get_first_possible_combination(
                        parent_combination=parent_combination
                    ),
                    currency,
                    pricelist,
                    datetime.fromisoformat(so_date),
                    parent_combination=parent_combination,
                    **kwargs,
                ),
                parent_product_tmpl_id=product_template.id,
            ) for optional_product_template in product_template.optional_product_ids if
            self._should_show_product(optional_product_template, parent_combination)
        ]
        
        # Get accessory products
        accessory_products = [
            dict(
                **self._get_product_information(
                    accessory_product.product_tmpl_id,
                    accessory_product.product_tmpl_id._get_first_possible_combination(
                        parent_combination=parent_combination
                    ),
                    currency,
                    pricelist,
                    datetime.fromisoformat(so_date),
                    parent_combination=parent_combination,
                    **kwargs,
                ),
                parent_product_tmpl_id=product_template.id,
                product_type='accessory'
            ) for accessory_product in product_template.accessory_product_ids if
            self._should_show_product(accessory_product.product_tmpl_id, parent_combination)
        ]
        
        # Get alternative products
        alternative_products = [
            dict(
                **self._get_product_information(
                    alternative_product_template,
                    alternative_product_template._get_first_possible_combination(
                        parent_combination=parent_combination
                    ),
                    currency,
                    pricelist,
                    datetime.fromisoformat(so_date),
                    parent_combination=parent_combination,
                    **kwargs,
                ),
                parent_product_tmpl_id=product_template.id,
                product_type='alternative'
            ) for alternative_product_template in product_template.alternative_product_ids if
            self._should_show_product(alternative_product_template, parent_combination)
        ]
        
        return {
            'optional_products': optional_products,
            'accessory_products': accessory_products,
            'alternative_products': alternative_products,
        }

