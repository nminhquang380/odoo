import uuid
import logging
from odoo.exceptions import ValidationError

from odoo import models, fields, api, tools, _

_logger = logging.getLogger(__name__)


class KhoaSinhVien(models.Model):
    _name = "khoa_sinh_vien"
    _description = "Khóa sinh viên"
    _rec_name = "ten_hien_thi"

    ten_hien_thi = fields.Char(compute="_compute_ten_hien_thi",
                               store=True,
                               string="Tên khóa sinh viên",
                               readonly=False)
    so_thu_tu_khoa = fields.Integer("Số thứ tự khóa")
    nganh_ids = fields.One2many("khoa_nganh",
                                "khoa_sinh_vien_id",
                                string="Danh sách ngành học")
    nam_hoc = fields.Many2one(comodel_name="nam_hoc", string="Năm học")
    # ky_nhap_hoc = fields.Many2one("ky_nam_hoc", string="Kỳ nhập học")
    hinh_thuc_dao_tao_id = fields.Many2one(comodel_name='hinh_thuc_dao_tao',
                                           ondelete='set null',
                                           string='Hình thức đào tạo')

    @api.depends("so_thu_tu_khoa", "hinh_thuc_dao_tao_id")
    def _compute_ten_hien_thi(self):
        for record in self:
            if record.so_thu_tu_khoa != 0:
                record.ten_hien_thi = "D" + str(record.so_thu_tu_khoa)
                if record.hinh_thuc_dao_tao_id.ten_hinh_thuc_dao_tao_viet_tat:
                    record.ten_hien_thi += record.hinh_thuc_dao_tao_id.ten_hinh_thuc_dao_tao_viet_tat
                    # đoạn này là quickfix việc phân biệt giữa các khóa sinh viên của nhiều hình thức đào tạo khác nhau
                    # cần sửa lại logic nối tên hình thức đào tạo viết tắt, vd: D17TX , D17CQ
            else:
                record.ten_hien_thi = ""

    @api.constrains("nganh_ids")
    def validate_nganh_ids(self):
        if not self.nganh_ids:
            raise ValidationError("Chưa chọn danh sách ngành học!")

    @api.model
    def create(self, vals):
        if vals.get('hinh_thuc_dao_tao_id') and vals.get('so_thu_tu_khoa'):
            khoa_sv_da_ton_tai = self.env['khoa_sinh_vien'].search([
                ('hinh_thuc_dao_tao_id', '=', vals['hinh_thuc_dao_tao_id']),
                ('so_thu_tu_khoa', '=', vals['so_thu_tu_khoa'])
            ])
            if khoa_sv_da_ton_tai:
                khoa_sv_da_ton_tai.write(vals)
                return khoa_sv_da_ton_tai
            else:
                res = super(KhoaSinhVien, self).create(vals)
                return res
        else:
            res = super(KhoaSinhVien, self).create(vals)
            return res
