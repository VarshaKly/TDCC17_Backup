.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===================================
Report Qweb Element Page Visibility
===================================

This module allows you to use 4 classes in QWEB reports:

- not-first-page: shows element in every page but first
- not-last-page: shows element in every page but last
- first-page: shows element only on first page
- last-page: shows element only on last page

Usage
=====

To use this module, you need to:

In the QWEB ``ir.ui.views`` used by your report,
you can add an element with css class with any of the classes described above.
For example if you need to improve invoice report header with
invoice's number in every page but first, and sale order report header 
with order's name in every page but last, add this code to external_layout_header::

    <t t-if="o._table=='account_invoice'">
        <div class="not-first-page">
            <span t-esc="o.number"/>
        </div>
    </t>
    <t t-if="o._table=='sale_order'">
        <div class="not-last-page">
            <span t-esc="o.name"/>
        </div>
    </t>

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/143/11.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/
reporting-engine/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback `here <https://github.com/OCA/reporting-engine/issues/new?body=module:%20
report_qweb_element_page_visibility%0Aversion:%20
11.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Nicola Malcontenti <nicola.malcontenti@agilebg.com>
* Lorenzo Battistini <lorenzo.battistini@agilebg.com>
* Alessio Gerace <alessio.gerace@agilebg.com>
* Alex Comba <alex.comba@agilebg.com>
* Susana Vázquez <svazquez@netquest.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
