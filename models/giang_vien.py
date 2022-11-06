import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class GiangVien(models.Model):
    _name = "giang_vien"
    _description = "Giảng viên"
    _inherit = ["tac_nhan"]
    _rec_name = "ma_dinh_danh_ten"

    user_group_string = "website_slides.group_website_slides_officer"
    vai_tro_string = "giang_vien"
    # vai_tro = ('3','giang_vien')
    lop_tin_chi_ids = fields.One2many("lop_tin_chi", "giang_vien_id")
    ham_hoc_vi = fields.Selection([("ThS", "Thạc sĩ"),
                                   ("GVC", "Giảng viên chính"),
                                   ("TS", "Tiến sĩ"),
                                   ("PGS.TS", "Phó giáo sư tiến sĩ"),
                                   ("GS", "Giáo sư")])
    # ten_id_gv = fields.Char(
    #     "ID Giảng viên", compute="_compute_giang_vien_id", store=True)
    hoc_ham_ten_id_gv = fields.Char(_compute="_compute_hoc_ham_ten_id_gv",
                                    store=True,
                                    string="Giảng viên")
    ma_gv = fields.Char("Mã giảng viên")
    chuc_vu = fields.Char("Chức vụ")

    @api.depends("name", "ma_dinh_danh")
    def _compute_hoc_ham_ten_id_gv(self):
        for record in self:
            if record.name and record.ma_dinh_danh:
                record.hoc_ham_ten_id_gv = record.name + '-' + record.ma_dinh_danh

    # @api.depends("name", "ham_hoc_vi", "ma_dinh_danh")
    # def _compute_giang_vien_id(self):
    #     '''
    #         Phục vụ mục đích hiển thị
    #     '''
    #     for record in self:
    #         if record.name and record.ma_dinh_danh:
    #             record.ten_id_gv = record.name + '-' + record.ma_dinh_danh
    #         else:
    #             record.ten_id_gv = record.ten_id_gv
    #         if record.ham_hoc_vi:
    #             record.ten_id_gv = record.ham_hoc_vi + '.' + record.ten_id_gv
