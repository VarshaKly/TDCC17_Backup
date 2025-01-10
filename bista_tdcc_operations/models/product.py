# -*- encoding: utf-8 -*-
##############################################################################
#
# Bista Solutions Pvt. Ltd
# Copyright (C) 2012 (http://www.bistasolutions.com)
#
##############################################################################

from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    tdcc_product_id = fields.Integer(string="Product TDCC ID")
