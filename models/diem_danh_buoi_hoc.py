from odoo import fields, models, api
from odoo.exceptions import ValidationError


class DiemDanhBuoiHoc(models.Model):
    _name = "diem_danh_buoi_hoc"
    _description = "Điểm danh theo buổi học"

    sinh_vien_id = fields.Many2one("sinh_vien", "Sinh viên")
    ten_sinh_vien = fields.Char("Tên sinh viên",
                                related="sinh_vien_id.name",
                                store=True)
    buoi_hoc_id = fields.Many2one(
        "buoi_hoc",
        "Buổi học",
    )
    tuan_hoc = fields.Integer("Tuần học",
                              related="buoi_hoc_id.tuan_hoc",
                              store=True)
    diem_cong = fields.Integer("Điểm cộng", )
    trang_thai = fields.Selection([
        ("Vắng", "Vắng"),
        ("Có mặt", "Có mặt"),
    ], "Trạng thái")

    _sql_constraints = [
        ("unique_sinh_vien_buoi_hoc", "UNIQUE(sinh_vien_id, buoi_hoc_id)",
         "Đã có sinh viên trong buổi học này")
    ]

    @api.constrains("sinh_vien_id", "buoi_hoc_id")
    def _check_sinh_vien_trong_lop(self):
        for record in self:
            if record.sinh_vien_id not in record.buoi_hoc_id.lop_tin_chi_id.sinh_vien_ids:
                raise ValidationError(
                    "Sinh viên không thuộc lớp có buổi học này!")
