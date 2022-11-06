from odoo import fields, models, api
from odoo.exceptions import ValidationError
import re


class NamHoc(models.Model):
    _name = "nam_hoc"
    _description = "Năm học"
    _rec_name = "ten_nam_hoc"

    ten_nam_hoc = fields.Char("Tên năm học", compute="_compute_ten_nam_hoc", store=True)
    nam_hoc = fields.Integer("Năm học")
    nam_hoc_char = fields.Char("Năm học", compute="_compute_nam_hoc_char", store=True)
    thoi_gian_bat_dau = fields.Date("Thời gian bắt đầu")
    thoi_gian_ket_thuc = fields.Date("Thời gian kết thúc")

    _sql_constraints = [
        ('unique_ten_nam_hoc', 'unique (ten_nam_hoc)', 'Năm học đã tồn tại')
    ]

    @api.onchange("thoi_gian_bat_dau", "thoi_gian_ket_thuc")
    def validate_thoi_gian_nam_hoc(self):
        if self.thoi_gian_bat_dau and self.thoi_gian_ket_thuc:
            if self.thoi_gian_bat_dau > self.thoi_gian_ket_thuc:
                raise ValidationError(
                    "Thời gian kết thúc năm học không được sớm hơn thời gian bắt đầu!"
                )

    @api.depends("nam_hoc")
    def _compute_ten_nam_hoc(self):
        for record in self:
            if record.nam_hoc:
                nam_ke_tiep = record.nam_hoc + 1
                record.ten_nam_hoc = str(record.nam_hoc) + "-" + str(nam_ke_tiep)
            else:
                record.ten_nam_hoc = ""

    @api.depends("nam_hoc")
    def _compute_nam_hoc_char(self):
        for record in self:
            if record.nam_hoc:
                record.nam_hoc_char = str(record.nam_hoc)
            else:
                record.nam_hoc_char = ""

    @api.constrains("nam_hoc")
    def validate_nam_hoc(self):
        nam = str(self.nam_hoc)
        match = re.match("^(19|[2-9][0-9])\d{2}$", nam)
        if match is None:
            raise ValidationError("Năm học không hợp lệ!")
