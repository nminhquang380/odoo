import logging

from odoo import models, fields, api
from .constants_of_selection_fields import vai_tro_don_vi_selection, hoc_ham_hoc_vi

_logger = logging.getLogger(__name__)


class CanBo(models.Model):
    _name = "can_bo"
    _description = "Cán bộ"
    _inherit = ["tac_nhan"]
    # _rec_name = "name"
    _rec_name = "ma_dinh_danh_ten"

    user_group_string = "website_slides.group_website_can_bo"
    vai_tro_string = "can_bo"
    don_vi_goc = fields.Many2one(comodel_name='danh_muc.don_vi',
                                 ondelete='set null',
                                 string='Đơn vị gốc')
    ma_dinh_danh_ten_cb = fields.Char(compute="_compute_ma_dinh_danh_ten_cb",
                                      store=True,
                                      string="Mã định danh - tên cán bộ")
    vai_tro_goc = fields.Selection(selection=vai_tro_don_vi_selection,
                                   string='Vai trò gốc')
    vai_tro_kiem_nhiem = fields.One2many(comodel_name='vai_tro_kiem_nhiem',
                                         inverse_name='nhan_vien_id',
                                         string='Vai trò kiêm nhiệm')
    hoc_ham_hoc_vi = fields.Selection(selection=hoc_ham_hoc_vi,
                                      string='Học hàm - học vị')
    chuc_vu = fields.Char("Chức vụ")
    chuc_danh_chuyen_mon = fields.Char("Chức danh chuyên môn")
    lop_tin_chi_ids = fields.Many2many(comodel_name="lop_tin_chi",
                                       string="Lớp tín chỉ")
    lop_hanh_chinh_ids = fields.One2many(comodel_name="lop_hanh_chinh",
                                         inverse_name="can_bo_id",
                                         string="Lớp hành chính phụ trách")
    loaiNoiSinh = fields.Selection([
        ("0", "Trong nước"),
        ("1", "Nước ngoài")
        ], string="Loại nơi sinh")
    noiSinhNuocNgoai = fields.Char("Nơi sinh nước ngoài")

    @api.depends("name", "ma_dinh_danh")
    def _compute_ma_dinh_danh_ten_cb(self):
        for record in self:
            if record.name and record.ma_dinh_danh:
                record.ma_dinh_danh_ten_cb = record.ma_dinh_danh + "-" + record.name


class ChuyenVien(models.Model):
    """
        Tạm thời chưa xóa để tránh lỗi key error
    """
    _name = "chuyen_vien"
    _description = "Chuyên viên"
    _inherit = ["tac_nhan"]

    user_group_string = "website_slides.group_website_slides_mentor"
