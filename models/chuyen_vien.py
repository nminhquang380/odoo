from odoo import models, fields, api


class ChuyenVien(models.Model):
    _name = 'chuyen_vien'
    _description = 'Cán bộ'
    _inherit = ['tac_nhan']

    user_group_string = "website_slides.group_website_slides_mentor"
