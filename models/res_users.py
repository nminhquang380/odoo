# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields
import logging
from .constants_of_selection_fields import vai_tro_selection

_logger = logging.getLogger(__name__)


class Users(models.Model):
    _inherit = "res.users"

    vai_tro = fields.Selection(vai_tro_selection, string="Vai trò")

    hinh_thuc_dao_tao_id = fields.Many2one(
        comodel_name="hinh_thuc_dao_tao",
        string="Hình thức đào tạo",
    )
    partner_id = fields.Many2one("res.partner", ondelete="cascade")

    def write(self, vals):
        """ Trigger automatic subscription based on updated user groups """
        res = super(Users, self).write(vals)
        if vals.get("groups_id"):
            added_group_ids = [
                command[1] for command in vals["groups_id"] if command[0] == 4
            ]
            added_group_ids += [
                id for command in vals["groups_id"] if command[0] == 6
                for id in command[2]
            ]
            # self.env['slide.channel'].sudo().search([('enroll_group_ids', 'in', added_group_ids)])._action_add_members(self.mapped('partner_id'))
        return res

    def get_gamification_redirection_data(self):
        res = super(Users, self).get_gamification_redirection_data()
        res.append({"url": "/slides", "label": "See our eLearning"})
        return res
