from odoo import models, api, fields
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class HocPhanCoSoDaoTaoKhac(models.Model):
    _name = "qldt.hoc_phan_co_so_dao_tao_khac"
    _description = "Học phần của cơ sở đào tạo khác"
    _rec_name = "ten_hoc_phan"

    ma_hoc_phan = fields.Char(string="Mã học phần/chứng chỉ của cơ sở đào tạo khác")
    ten_hoc_phan = fields.Char(string="Tên học phần/chứng chỉ của cơ sở đào tạo khác")
    so_tin_chi = fields.Integer(string="Số tín chỉ (nếu có)")
    co_so_dao_tao_chung_nhan = fields.Char(string="Cơ sở đào tạo chứng nhận")
    link_hoc_phan = fields.Char(string="Đường dẫn/Link (nếu có)")
    hoc_phan_tuong_duong_id = fields.Many2one(
        comodel_name="qldt.hoc_phan_tuong_duong",
        ondelete="cascade",
        string="Học phần tương đương",
    )
    so_cu = fields.Binary(
        string="Tài liệu/minh chứng", help="chỉ upload 1 file PDF"
    )
    ten_file_minh_chung = fields.Char("Tên file tài liệu/minh chứng", store=True)


class HocPhanTuongDuong(models.Model):
    _name = "qldt.hoc_phan_tuong_duong"
    _description = "Quản lý danh sách học phần tương đương"
    _rec_name = "noi_dung_chuyen_doi"

    ma_hoc_phan_tuong_duong = fields.Char("Mã học phần tương đương")
    noi_dung_chuyen_doi = fields.Char(string="Nội dung chuyển đổi",)
    ctk_id = fields.Many2one(
        comodel_name="chuong_trinh_khung",
        ondelete="cascade",
        string="Chương trình khung tham chiếu",
    )

    hoc_phan_id = fields.Many2many(
        comodel_name="mon_hoc_dieu_kien",
        string="Học phần thuộc CTK của cơ sở đào tạo",
    )

    hoc_phan_co_so_dao_tao_khac = fields.Many2many(
        comodel_name="qldt.hoc_phan_co_so_dao_tao_khac",
        string="Danh sách học phần tương đương (của cơ sở đào tạo khác)",
    )

    mon_hoc_dieu_kien_id = fields.Many2one(
        comodel_name="mon_hoc_dieu_kien",
        ondelete="set null",
        string="Môn học thuộc chương trình khung",
    )

    @api.constrains("hoc_phan_id")
    def validate_hoc_phan_id(self):
        if not self.hoc_phan_id:
            raise ValidationError('Chưa chọn học phần thuộc CTK của cơ sở đào tạo.')


class QuyTacCongNhanKQHT(models.Model):
    """
        Định nghĩa các quy tắc công nhận kết quả học tập
    """

    _name = "qldt.quy_tac_cong_nhan_kqht"
    _description = "Quản lý quy tắc công nhận kết quả học tập"

    ma_quy_tac = fields.Char(string="Mã quy tắc")
    ten_quy_tac = fields.Char(string="Tên quy tắc")
    van_ban_quy_dinh = fields.Many2one(
        comodel_name="danh_muc.van_ban_quy_dinh", string="Văn bản quy định"
    )
