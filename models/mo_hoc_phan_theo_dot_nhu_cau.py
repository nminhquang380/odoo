from odoo import models, fields

class MoHocPhanTheoDotNhuCau(models.Model):
    _name = "mo_hoc_phan_theo_dot_nhu_cau"
    _description = "Mở học phần cho đợt đăng ký nhu cầu"

    sinh_vien_ids = fields.Many2many(
        comodel_name="sinh_vien",
        string="Danh sách sinh viên",
    )
    hoc_phan_ids = fields.Many2many(
        comodel_name="slide.channel",
        string="Danh sách học phần mở",
    )
