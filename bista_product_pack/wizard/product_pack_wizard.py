# -*- encoding: utf-8 -*-
#
#
# Bista Solutions Pvt. Ltd
# Copyright (C) 2012 (http://www.bistasolutions.com)
#
#
from odoo import models, fields, api, _
from odoo.exceptions import Warning


class ProductPackWizard(models.TransientModel):
    _name = 'product.pack.wizard'
    _description = 'Product Pack'

    product_id = fields.Many2one('product.template', 'Product pack')
    pack_ids = fields.One2many(
        'product.pack.line', related='product_id.pack_ids',
        string='Pack Products')

    @api.multi
    def add_product_pack(self):
        order_id = self.env['sale.order'].browse(
            self._context.get('active_id'))
        for pack in self:
            for prd in pack.product_id.pack_ids:
                prd_id = prd.product_id.id
                vals = {'order_id': order_id.id,
                        'product_id': prd_id,
                        }
                self.env['sale.order.line'].create(vals)
        return True

    @api.multi
    def add_product_pack_invoice(self):
        invoice_id = self.env['account.invoice'].browse(
            self._context.get('active_id'))
        for pack in self:
            for prd in pack.product_id.pack_ids:
                prd_id = prd.product_id.id
                if prd.product_id.property_account_income_id:
                    acc_id = prd.product_id.property_account_income_id.id
                elif prd.product_id.categ_id.property_account_income_categ_id:
                    acc_id = prd.product_id.categ_id.\
                        property_account_income_categ_id.id
                else:
                    raise Warning(_("Account is not set for product.First \
                                     configure account for product !"))
                    acc_id = prd.product_id.categ_id.\
                        property_account_income_categ_id.id
                vals = {'invoice_id': invoice_id.id,
                        'product_id': prd_id,
                        'name': prd.product_id.name,
                        'price_unit': prd.product_id.list_price,
                        'account_id': acc_id,
                        'quantity': 1
                        }
                self.env['account.invoice.line'].create(vals)
        return True
