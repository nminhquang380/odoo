from odoo import models, api, fields
from odoo.exceptions import ValidationError

from .constants_of_selection_fields import trang_thai_phieu_yeu_cau_cong_nhan_kqht

import logging

_logger = logging.getLogger(__name__)


class CongNhanKQHT(models.Model):
    """
        Class này đinh nghĩa ra model chứa các thông tin liên quan đến công nhận kết quả học tập của từng sinh viên
        Công nhận kết quả học tập bao gồm chuyển đổi tương đương các học phần + chứng chỉ mà sinh viên đã hoàn thành
        sang chương trình học tập hiện tại (chương trình khung hiện tại của sinh viên)
    """
    _name = "qldt.cong_nhan_kqht"
    _description = "Quản lý công nhận kết quả học tập"
    _rec_name = "sinh_vien_id"

    sinh_vien_id = fields.Many2one(
        comodel_name="sinh_vien", ondelete="cascade", string="Mã sinh viên"
    )
    ten_sv = fields.Char(related="sinh_vien_id.name",
                         store=True, string="Tên SV")
    khoi_lop_id = fields.Many2one(
        comodel_name="khoi_lop",
        ondelete="cascade",
        related="sinh_vien_id.khoi_lop_id",
        store=True,
        string="Khối lớp",
    )

    ten_day_du_sv = fields.Char(
        related="sinh_vien_id.name", store=True, string="Tên sinh viên"
    )

    ctk_nganh_id = fields.Many2one(
        comodel_name="chuong_trinh_khung",
        ondelete="set null",
        related="sinh_vien_id.ctk_nganh_id",
        store=True,
        string="Chương trình khung ngành",
    )
    ctk_chuyen_nganh_id = fields.Many2one(
        comodel_name="chuong_trinh_khung",
        ondelete="set null",
        related="sinh_vien_id.ctk_chuyen_nganh_id",
        store=True,
        string="Chương trình khung chuyên ngành",
    )

    mon_hoc_thuoc_chuong_trinh_khung = fields.Many2many(
        comodel_name="mon_hoc_dieu_kien",
        string="Môn học thuộc chương trình khung"
    )

    mon_hoc_da_hoan_thanh = fields.Many2many(
        comodel_name="qldt.hoc_phan_co_so_dao_tao_khac",
        string="Môn học/chứng chỉ thuộc cơ sở đào tạo khác"
    )

    sv_hp_ds_ids = fields.One2many(
        "sv_hp_ds",
        "cong_nhan_ket_qua_hoc_tap_id",
        "Danh sách điểm học phần của sinh viên",
    )

    file_minh_chung = fields.Binary("File minh chứng")
    ten_file_minh_chung = fields.Char("Tên file minh chứng", store=True)
    ghi_chu = fields.Text(string="Ghi chú")

    @api.model
    def create(self, values):
        record = super(CongNhanKQHT, self).create(values)
        self = self.with_context(MyModelLoopBreaker=True)
        if record.sinh_vien_id and record.mon_hoc_thuoc_chuong_trinh_khung:
            # Xóa các điểm học phần cũ
            hoc_phan_cu_ids = self.env["sv_hp_ds"].search(
                [
                    ["cong_nhan_ket_qua_hoc_tap_id", "=", record.id],
                    ["hoc_phan_id", "not in", [
                        x.hoc_phan_id.id for x in record.mon_hoc_thuoc_chuong_trinh_khung]]
                ]
            )
            hoc_phan_cu_ids.unlink()

            # Thêm các học phần hiện tại
            for mon_hoc in record.mon_hoc_thuoc_chuong_trinh_khung:
                id_ = self.env["sv_hp_ds"].search(
                    [
                        ["sinh_vien_id", "=", record.sinh_vien_id.id],
                        ["hoc_phan_id", "=", mon_hoc.hoc_phan_id.id]
                    ],
                    limit=1,
                )
                if len(id_) == 0:
                    id_ = self.env["sv_hp_ds"].create(
                        {
                            "sinh_vien_id": record.sinh_vien_id.id,
                            "hoc_phan_id": mon_hoc.hoc_phan_id.id
                        }
                    )
                id_.trang_thai = "Miễn"
                id_.cong_nhan_ket_qua_hoc_tap_id = record.id
        else:
            record.sv_hp_ds_ids = False
        return record

    def write(self, values):
        if self.env.context.get('MyModelLoopBreaker'):
            return
        self = self.with_context(MyModelLoopBreaker=True)
        res = super(CongNhanKQHT, self).write(values)
        # Xóa các điểm học phần cũ
        hoc_phan_cu_ids = self.env["sv_hp_ds"].search(
            [
                ["cong_nhan_ket_qua_hoc_tap_id", "=", self.id],
                ["hoc_phan_id", "not in", [
                    x.hoc_phan_id.id for x in self.mon_hoc_thuoc_chuong_trinh_khung]]
            ]
        )
        hoc_phan_cu_ids.unlink()

        # Thêm các học phần hiện tại
        for mon_hoc in self.mon_hoc_thuoc_chuong_trinh_khung:
            id_ = self.env["sv_hp_ds"].search(
                [
                    ["sinh_vien_id", "=", self.sinh_vien_id.id],
                    ["hoc_phan_id", "=", mon_hoc.hoc_phan_id.id]
                ],
                limit=1,
            )
            if len(id_) == 0:
                id_ = self.env["sv_hp_ds"].create(
                    {
                        "sinh_vien_id": self.sinh_vien_id.id,
                        "hoc_phan_id": mon_hoc.hoc_phan_id.id
                    }
                )
            id_.trang_thai = "Miễn"
            id_.cong_nhan_ket_qua_hoc_tap_id = self.id
        return res

    @api.depends("khoi_lop_id")
    def _compute_lay_ctk(self):
        for record in self:
            if record.khoi_lop_id:
                ctk_hien_tai = self.env["chuong_trinh_khung"].search(
                    [("khoa_nganh_ids", "in", [record.khoi_lop_id.khoa_nganh_id.id])]
                )
                record.ctk_id = ctk_hien_tai.id


class PhieuYeuCauCongNhanKQHT(models.Model):
    _name = "qldt.yc_cong_nhan_kqht"
    _description = "Quản lý phiếu yêu cầu công nhận kết quả học tập"
    _rec_name = "sinh_vien_id"

    sinh_vien_id = fields.Many2one(
        comodel_name="sinh_vien", ondelete="cascade", string="Mã sinh viên"
    )
    ten_sv = fields.Char(related="sinh_vien_id.name",
                         store=True, string="Tên SV")
    khoi_lop_id = fields.Many2one(
        comodel_name="khoi_lop",
        ondelete="cascade",
        related="sinh_vien_id.khoi_lop_id",
        store=True,
        string="Khối lớp",
    )

    ctk_id = fields.Many2one(
        comodel_name="chuong_trinh_khung",
        ondelete="set null",
        compute="_compute_lay_ctk",
        store=True,
        string="Chương trình khung",
    )

    mon_hoc_thuoc_chuong_trinh_khung = fields.Many2many(
        comodel_name="mon_hoc_dieu_kien",
        string="Môn học thuộc chương trình khung"
    )

    mon_hoc_da_hoan_thanh = fields.Many2many(
        comodel_name="qldt.hoc_phan_co_so_dao_tao_khac",
        string="Môn học/chứng chỉ thuộc cơ sở đào tạo khác"
    )
    trang_thai = fields.Selection(
        selection=trang_thai_phieu_yeu_cau_cong_nhan_kqht,
        string="Trạng thái"
    )
    file_minh_chung = fields.Binary("File minh chứng")
    ten_file_minh_chung = fields.Char("Tên file minh chứng", store=True)
    ghi_chu = fields.Text(string="Ghi chú")

    @api.depends("khoi_lop_id")
    def _compute_lay_ctk(self):
        for record in self:
            if record.khoi_lop_id:
                ctk_hien_tai = self.env["chuong_trinh_khung"].search(
                    [("khoa_nganh_ids", "in", [record.khoi_lop_id.khoa_nganh_id.id])]
                )
                record.ctk_id = ctk_hien_tai.id

# class KQHTDuocCongNhan(models.Model):
#     """
#         Cần nghĩ lại tên class này cho dễ hiểu hơn
#         Class này định nghĩa 1 bản ghi kết quả học tập được công nhận của sinh viên
#         ví dụ, sinh viên có chứng chỉ tiếng anh, có chứng chỉ này được miễn học 2 môn tiếng anh và được công nhận điểm 9
#         việc miễn học này được quy định trong danh sách học phần tương đương
#         do đó khi sinh viên có chứng chỉ tiếng anh rồi thì cần có 1 bản ghi lưu lại các thông tin như:
#             - quy tắc công nhận tương ứng
#             - học phần được công nhận
#             - sở cứ ( file upload)
#             - ngày hết hạn
#         class này dùng để định nghĩa model chứa các thông tin này
#     """
#
#     _name = "qldt.kqht_duoc_cong_nhan"
#     _description = "Kết quả học tập được công nhận"
#
#     noi_dung_chuyen_doi = fields.Many2one(
#         comodel_name="qldt.hoc_phan_tuong_duong",
#         ondelete="cascade",
#         string="Học phần tương đương",
#     )
#
#     danh_sach_mon_hoc_duoc_chuyen_doi = fields.Many2many(
#         comodel_name="mon_hoc_dieu_kien", related="noi_dung_chuyen_doi.hoc_phan_id"
#     )  # trường thông tin này dùng cho domain filter của ten_hoc_phan
#     # hiện chưa tìm được cách domain filter trực tiếp mà ko dùng related fields
#     # ten_hoc_phan = fields.Many2one(
#     #     comodel_name='mon_hoc_dieu_kien',
#     #     ondelete='cascade',
#     #     domain="[('id','in',danh_sach_mon_hoc_duoc_chuyen_doi)]", # domain filter theo related field ở trên
#     #     string="Tên học phần của CTK hiện tại"
#     # )
#     ten_hoc_phan = fields.Many2many(
#         comodel_name="mon_hoc_dieu_kien",
#         related="noi_dung_chuyen_doi.hoc_phan_id",
#         # store=True,
#         string="Tên học phần của CTK hiện tại",
#     )
#     ma_hoc_phan = fields.Char(
#         related="ten_hoc_phan.hoc_phan_id.ma_hoc_phan_moi",  # chỗ này cần linking với list môn học của nội dung chuyển đổi
#         store=True,
#         string="Mã học phần",
#     )
#     # hoc_phan_co_so_dao_tao_khac_id = fields.One2many(
#     #     comodel_name='qldt.hoc_phan_co_so_dao_tao_khac',
#     #     related='noi_dung_chuyen_doi.hoc_phan_co_so_dao_tao_khac',
#     #     # store=True,
#     #     string='Học phần - CC tương đương'
#     # )
#     hoc_phan_cs_khac = fields.One2many(
#         comodel_name="qldt.hoc_phan_co_so_dao_tao_khac",
#         related="noi_dung_chuyen_doi.hoc_phan_co_so_dao_tao_khac",
#     )  # trường này cũng dùng cho  domain filter ở bên dưới
#     hoc_phan_co_so_dao_tao_khac_id = fields.Many2one(
#         comodel_name="qldt.hoc_phan_co_so_dao_tao_khac",
#         ondelete="cascade",
#         domain="[('id','in',hoc_phan_cs_khac)]",  # domain filter
#         string="Học phần/chứng chỉ tương đương",
#     )
#
#     file_minh_chung = fields.Binary(string="File minh chứng")
#     ten_file_minh_chung = fields.Char("Tên file minh chứng", store=True)
#     ngay_het_han = fields.Date(string="Ngày hết hạn")
#     diem_quy_doi = fields.Float(string="Điểm quy đổi")
#     cong_nhan_kqht_id = fields.Many2one(
#         comodel_name="qldt.cong_nhan_kqht",
#         ondelete="cascade",
#         string="Thuộc bản ghi công nhận kết quả học tập",
#     )
