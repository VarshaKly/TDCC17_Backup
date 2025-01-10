odoo.define('bista_tdcc_operations.DailyNotesDashboard', function (require) {
"use strict";
var ajax = require('web.ajax');
var ControlPanelMixin = require('web.ControlPanelMixin');
var AbstractAction = require('web.AbstractAction');
var core = require('web.core');
var Dialog = require('web.Dialog');
var session = require('web.session');
var rpc = require('web.rpc');
var utils = require('web.utils');
var web_client = require('web.web_client');
var Widget = require('web.Widget');
var _t = core._t;
var QWeb = core.qweb;
var time = require('web.time');

var DailyNotesDashboard =AbstractAction.extend({
    template: "DailyNotesDashboardMain",
    events: {
        'click .dailynotes_info': 'view_dailynotes',
        'click .dna_appointments': 'view_dna_appointments',
        'click .inv_cancel_request': 'inv_cancel_request_actions',
    },

    init: function(parent, context) {
        this._super(parent, context);
        this.dailynotes_count = 0;
        this.dna_appointment_count = 0;
        this.inv_cancel_request_count = 0;
        this.action_id = context.id;
    },

    start: function() {
        var self = this;
        for(var i in self.breadcrumbs){
            self.breadcrumbs[i].title = "Daily Notes Dashboard";
        }
        this._rpc({
            model: 'daily.notes',
            method: 'get_dailynotes',
        })
        .then(function (res) {
            self.dailynotes_count = res['dailynotes_count']
            self.dna_appointment_count = res['dna_appointment_count']
            self.inv_cancel_request_count = res['inv_cancel_request_count']
            $('.o_dailynotes_dashboard').append(QWeb.render('DailyNotesDashboard', {widget: self}));
        });
    },

    on_reverse_breadcrumb: function() {
        web_client.do_push_state({action: this.action_id});
    },

    view_dailynotes: function(e) {
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Daily Notes"),
            type: 'ir.actions.act_window',
            res_model: 'daily.notes',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [["state","=","draft"]],
            target: 'current'
        }, options)
    },

    view_dna_appointments: function(e) {
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        var current_date = time.date_to_str(new Date());
        this.do_action({
            name: _t("DNA Appointments"),
            type: 'ir.actions.act_window',
            res_model: 'appointment.appointment',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [["state","=","dna"],['start_date', '>=', current_date + ' 00:00:00'],
                    ['start_date', '<=', current_date + ' 23:59:59']],
            target: 'current'
        }, options)
    },

    inv_cancel_request_actions: function (ev) {
        ev.preventDefault();
        var $action = $(ev.currentTarget);
        this.do_action($action.attr('name'), {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb
        });
    },

});

core.action_registry.add('dn_dashboard', DailyNotesDashboard);

return DailyNotesDashboard;

});
