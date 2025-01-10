odoo.define('bista_hr_dashboard.Dashboard', function (require) {
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

var HrDashboard =AbstractAction.extend({
    template: "HrDashboardMain",
    events: {
        'click .announcement_info': 'view_announcement',
    },

    init: function(parent, context) {
        this._super(parent, context);
        this.employee_birthday = [];
        this.upcoming_events = [];
        this.announcements = [];
        this.action_id = context.id;

    },

    start: function() {
        var self = this;
        for(var i in self.breadcrumbs){
            self.breadcrumbs[i].title = "Dashboard";
        }
        this._rpc({
            model: 'hr.employee',
            method: 'get_upcoming',
        })
        .then(function (res) {
            self.employee_birthday = res['birthday'];
            self.upcoming_events = res['event'];
            self.announcements = res['announcements'];
            $('.o_hr_dashboard').append(QWeb.render('EmployeeDashboard', {widget: self}));
        });
    },

    on_reverse_breadcrumb: function() {
//        this.update_control_panel({clear: true});
        web_client.do_push_state({action: this.action_id});
    },

    view_announcement: function(e) {
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        var $event = $(e.currentTarget);
        var announcement_id = parseInt($event.attr('data-id'), 10)
        this.do_action({
            name: _t("Announcements"),
            type: 'ir.actions.act_window',
            res_model: 'hr.announcement',
            view_type: 'form',
            view_mode: 'form',
            views: [[false, 'form']],
            res_id: announcement_id,
            target: 'current'
        }, options)
    },

});

core.action_registry.add('hr_dashboard', HrDashboard);

return HrDashboard;

});
