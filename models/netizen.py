from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class Mentor(models.Model):
    _name = "netizen"
    _description = "Netizen"
    _inherit = ["tac_nhan"]

    # login
    user_group_string = "website_slides.group_website_slides_netizen"

    name = fields.Char("Tên đầy đủ", size=500)

    # @api.model
    # def create(self, vals_list):
    #     _logger.info("\n\nhello from Mentor model: %r"%(vals_list))
    #     res = super(Mentor, self).create(vals_list)
    #     return res
