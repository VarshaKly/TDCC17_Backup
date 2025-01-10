# -*- encoding: utf-8 -*-
#
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2012 (http://www.bistasolutions.com)
#
##############################################################

from odoo import models, api


class Employee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def get_upcoming(self):
#         Birthday
        self._cr.execute("""
            SELECT *,
                    (to_char(dob, 'ddd')::int-to_char(
                    now(), 'ddd')::int+total_days)%total_days AS dif
            FROM
                (SELECT he.id,he.name,
                        to_char(he.birthday, 'Month dd') AS birthday,
                        hj.name AS job_id,
                        he.birthday AS dob,
                       (to_char((to_char(now(), 'yyyy')||'-12-31')::date,
                       'ddd')::int) AS total_days
                              FROM hr_employee he
                              JOIN hr_job hj ON hj.id = he.job_id ) birth
                        WHERE (to_char(dob, 'ddd')::int-to_char(now(), 'DDD')
                                     ::int+total_days)%
                                     total_days BETWEEN 0 AND 15
                        ORDER BY dif
            """)
        birthday = self._cr.dictfetchall()

#         Events
        self._cr.execute("""
                       SELECT e.name,
                               e.date_begin
                               AT TIME ZONE '%s' as date_begin,
                               e.date_end
                               AT TIME ZONE '%s' as date_end,
                              rc.name AS LOCATION,
                               e.is_online
                        FROM event_event e
                            LEFT JOIN res_partner rp ON e.address_id = rp.id
                            LEFT JOIN res_country rc ON rc.id = rp.country_id
                            WHERE state ='confirm'
                              AND (e.date_begin >= now()
                                   AND e.date_begin <= now() +
                                   interval '15 day')
                              OR (e.date_end >= now()
                                  AND e.date_end <= now() + interval '15 day')
                            ORDER BY e.date_begin""" % (str(self.env.user.tz),
                                                        str(self.env.user.tz)))
        event = self._cr.dictfetchall()

#       Announcement
        self._cr.execute("""SELECT ha.id,
                        ha.name
                FROM hr_announcement ha
                WHERE ha.state = 'approved'
                      AND (ha.date_start AT TIME ZONE '%s' <= now()::date
                      AND ha.date_end AT TIME ZONE '%s' >= now()::date)
                ORDER BY ha.date_start""" % (str(self.env.user.tz),
                                             str(self.env.user.tz)))
        announcements = self._cr.dictfetchall()

        return {
            'birthday': birthday,
            'event': event,
            'announcements': announcements,
        }
