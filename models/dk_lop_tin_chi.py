from odoo import fields, models


class DangKyLopTinChi(models.Model):
    _name = "dk_lop_tin_chi"
    _description = "Đăng ký lớp tín chỉ"

    # TODO: làm view thông tin đăng ký lớp tín chỉ của sinh viên
    dot_dk_tin_chi_id = fields.Many2one("dot_dang_ky_tin_chi", "Đợt đăng ký tín chỉ")
    sinh_vien_id = fields.Many2one("sinh_vien", "Sinh viên")
    lop_tin_chi_ids = fields.Many2many("lop_tin_chi", string="Danh sách lớp tín chỉ")
