import logging

from odoo import models, api, fields

from .constants_model_name import model_sinh_vien,  model_ky_nam_hoc,  model_chuong_trinh_khung

_logger = logging.getLogger(__name__)

"""
    Phần dưới đây là các Model đánh giá kết quả học tập
"""


class KetQuaHocTapSinhVien(models.Model):
    """
        #Deprecated
        Class này có thể không được sử dụng trong tương lai
    """
    _name = "qldt.ket_qua_hoc_tap_sinh_vien"
    _description = "Kết quả học tập sinh viên"

    ma_ket_qua = fields.Char("")
    sinh_vien_id = fields.Many2one(
        comodel_name="sinh_vien", ondelete="cascade", string="Sinh viên"
    )
    ky_nam_hoc_id = fields.Many2one(
        comodel_name="ky_nam_hoc", ondelete="set null", string="Kỳ năm học"
    )
    ma_sinh_vien = fields.Char(
        related="sinh_vien_id.ma_dinh_danh", store=True, string="Mã sinh viên"
    )
    ten_sinh_vien = fields.Char(
        related="sinh_vien_id.name", store=True, string="Tên sinh viên"
    )

    # Thông tin về điểm TB học kỳ + học lực + điểm TB tích lũy
    diem_tb_hoc_ky = fields.Float(
        compute="_compute_diem_trung_binh_hoc_ky",
        store=True,
        string="Điểm trung bình học kỳ",
    )
    hoc_luc = fields.Char(
        compute="_compute_xep_loai_hoc_luc_hoc_ky",
        default="Chưa xét",
        store=True,
        string="Xếp loại học lực",
    )
    diem_tb_tich_luy = fields.Float(
        compute="_compute_diem_trung_binh_tich_luy",
        store=True,
        string="Điểm trung bình tích lũy",
    )

    # linking với kết quả học tập theo kỳ
    # ket_qua_hoc_tap_hoc_ky_id = fields.Many2one(
    #     comodel_name='qldt.ket_qua_hoc_tap_hoc_ky',
    #     ondelete='set null',
    #     string="Kết qủa học tập học kỳ"
    # )

    @api.depends("sinh_vien_id", "ky_nam_hoc_id")
    def _compute_diem_trung_binh_hoc_ky(self):
        pass

    @api.depends("diem_tb_hoc_ky")
    def _compute_xep_loai_hoc_luc_hoc_ky(self):
        quy_tac_xep_hoc_luc = self.env["qldt.quy_tac_xep_loai_hoc_luc"].search([
        ])
        for record in self:
            for quy_tac in quy_tac_xep_hoc_luc:
                if (
                    quy_tac.gia_tri_diem_thang_10_min
                    <= record.diem_tb_hoc_ky
                    <= quy_tac.gia_tri_diem_thang_10_max
                ):
                    record.hoc_luc = quy_tac.loai_hoc_luc

    @api.depends("sinh_vien_id")
    def _compute_diem_trung_binh_tich_luy(self):
        pass

    # @api.depends('diem_tb_hoc_ky_thang_10')
    # def _compute_xep_loai_hoc_luc(self):
    #     '''
    #         Fetch bộ quy tắc đánh gía kết quả học tập, sau đó đối chiếu điểm -> lấy ra kết quả học lực
    #     '''
    #     for record in self:
    #         quy_tac_xep_loai_hoc_luc = self.env['qldt.quy_tac_xep_loai_hoc_luc'].search([])
    #         if record.diem_tb_hoc_ky_thang_10 != -1:
    #             for muc_hoc_luc in quy_tac_xep_loai_hoc_luc:
    #                 if muc_hoc_luc.gia_tri_diem_thang_10_min \
    #                         <= record.diem_tb_hoc_ky_thang_10 \
    #                         <= record.gia_tri_diem_thang_10_max:
    #                     record.xep_loai_hoc_luc_hoc_ky = muc_hoc_luc.id
    #         elif record.diem_tb_hoc_ky_thang_4 != -1:
    #             for muc_hoc_luc in quy_tac_xep_loai_hoc_luc:
    #                 if muc_hoc_luc.gia_tri_diem_thang_4_min \
    #                         <= record.diem_tb_hoc_ky_thang_4 \
    #                         <= record.gia_tri_diem_thang_4_max:
    #                     record.xep_loai_hoc_luc_hoc_ky = muc_hoc_luc.id


class KetQuaHocTapHocKy(models.Model):
    """
        Hiện class này đang dùng cho menu quản lý kết quả học tập học kỳ, năm học
        Hiện class này không sử dụng, thay vào đó là sinh_vien_hoc_ky
    """

    _name = "qldt.ket_qua_hoc_tap_hoc_ky"
    _description = "Kết quả học tập theo học kỳ"

    _sql_constraints = [
        (
            "kiem_tra_ban_ghi_ket_qua_hoc_tap_theo_ky_la_duy_nhat",
            "unique(ky_nam_hoc_id,khoi_lop_id,lop_hanh_chinh_id)",
            "Chỉ được phép tạo 1 bản ghi kết quả học tập trong 1 học kỳ của 1 lớp hành chính",
        )
    ]
    ky_nam_hoc_id = fields.Many2one(
        comodel_name="ky_nam_hoc",
        ondelete="cascade",
        required=True,
        string="Kỳ năm học",
    )
    # thông tin phụ, dùng để hiển thị dạng group-by
    nam_hoc = fields.Char(
        related="ky_nam_hoc_id.nam_hoc_id.ten_nam_hoc", store=True, string="Năm học"
    )
    khoi_lop_id = fields.Many2one(
        comodel_name="khoi_lop", ondelete="cascade", required=True, string="Khối lớp"
    )
    lop_hanh_chinh_id = fields.Many2one(
        comodel_name="lop_hanh_chinh",
        ondelete="cascade",
        required=True,
        string="Lớp hành chính",
    )

    ket_qua_hoc_tap_sinh_vien_ids = fields.Many2many(
        comodel_name="qldt.ket_qua_hoc_tap_sinh_vien",
        # inverse_name='ket_qua_hoc_tap_hoc_ky_id',
        # compute='_compute_danh_sach_ket_qua_hoc_tap_sinh_vien_theo_lop_hanh_chinh',
        # store=True,
        string="Kết quả học tập sinh viên",
    )

    @api.onchange("lop_hanh_chinh_id")
    def _compute_danh_sach_ket_qua_hoc_tap_sinh_vien_theo_lop_hanh_chinh(self):
        """
            Lấy danh sách kết qủa học tập sinh viên theo lớp hành chính
        """
        for record in self:
            if not record.khoi_lop_id or not record.ky_nam_hoc_id:
                return
            danh_sach_sinh_vien = self.env["sinh_vien"].search(
                [("lop_hanh_chinh_id", "=", record.lop_hanh_chinh_id.id)]
            )
            # record.ket_qua_hoc_tap_sinh_vien_ids = danh_sach_sinh_vien.ids
            danh_sach_ket_qua_hoc_tap_sinh_vien = self.env[
                "qldt.ket_qua_hoc_tap_sinh_vien"
            ].search([("sinh_vien_id.id", "in", danh_sach_sinh_vien.ids)])

            if danh_sach_ket_qua_hoc_tap_sinh_vien:
                for ket_qua_sinh_vien in danh_sach_ket_qua_hoc_tap_sinh_vien:
                    if ket_qua_sinh_vien.sinh_vien_id.id not in danh_sach_sinh_vien.ids:
                        values = {
                            "sinh_vien_id": ket_qua_sinh_vien.sinh_vien_id.id,
                            "ky_nam_hoc_id": record.ky_nam_hoc_id.id,
                            "diem_tb_hoc_ky": -1,
                            "diem_tb_tich_luy": -1,
                        }
                        r = self.env["qldt.ket_qua_hoc_tap_sinh_vien"].create(
                            values)
                        # danh_sach_ket_qua_sinh_vien.append(r)
            else:
                for sinh_vien in danh_sach_sinh_vien:
                    # đoạn này cần tìm các bản ghi trong sv-ltc-ds của sinh viên này
                    # sao cho các lớp tín chỉ thuộc kì năm học đang xét
                    # rồi tính điểm tổng kết học kỳ
                    lop_tin_chi_sinh_vien_da_hoc_trong_ky_nay = self.env[
                        "sv_ltc_ds"
                    ].search(
                        [
                            ("ky_hoc", "=", record.ky_nam_hoc_id.ma_ky_nam_hoc),
                            ("sinh_vien_id", "=", sinh_vien.id),
                        ]
                    )
                    chuong_trinh_khung_sv = self.env["chuong_trinh_khung"].search(
                        [
                            (
                                "khoa_nganh_ids",
                                "in",
                                sinh_vien.khoi_lop_id.khoa_nganh_id.id,
                            )
                        ]
                    )
                    ky_ctk_hien_tai = sinh_vien.khoi_lop_id.ky_ctk_hien_tai
                    danh_sach_hoc_phan_ky_hien_tai = self.env[
                        "mon_hoc_dieu_kien"
                    ].search(
                        [
                            ("ctk_id", "=", chuong_trinh_khung_sv.id),
                            ("hoc_ky", "=", ky_ctk_hien_tai),
                        ]
                    )
                    tong_so_mon_hoc_cua_ky_hien_tai = len(
                        danh_sach_hoc_phan_ky_hien_tai
                    )
                    tong_so_tin_chi = 0
                    tong_diem_thang_10 = 0
                    tong_diem_thang_4 = 0
                    diem_tong_ket_hoc_ky_thang_10 = 0
                    diem_tong_ket_hoc_ky_thang_4 = 0
                    if lop_tin_chi_sinh_vien_da_hoc_trong_ky_nay:
                        for lop_tin_chi in lop_tin_chi_sinh_vien_da_hoc_trong_ky_nay:
                            tong_so_tin_chi += lop_tin_chi.so_tin_chi
                            tong_diem_thang_10 += (
                                lop_tin_chi.diem_tong_ket * lop_tin_chi.so_tin_chi
                            )
                            tong_diem_thang_4 += (
                                lop_tin_chi.diem_tong_ket_thang_4
                                * lop_tin_chi.so_tin_chi
                            )
                        diem_tong_ket_hoc_ky_thang_10 = round(
                            tong_diem_thang_10 / tong_so_tin_chi, 2
                        )
                        diem_tong_ket_hoc_ky_thang_4 = round(
                            tong_diem_thang_4 / tong_so_tin_chi, 2
                        )
                    values = {
                        "sinh_vien_id": sinh_vien.id,
                        "ky_nam_hoc_id": record.ky_nam_hoc_id.id,
                        "diem_tb_hoc_ky": diem_tong_ket_hoc_ky_thang_10,
                        "diem_tb_tich_luy": -1,
                    }
                    r = self.env["qldt.ket_qua_hoc_tap_sinh_vien"].create(
                        values)
                    _logger.info("\n\nCreated {}".format(r))
                    # danh_sach_ket_qua_sinh_vien.append(r)
            danh_sach_ket_qua_hoc_tap_sinh_vien = self.env[
                "qldt.ket_qua_hoc_tap_sinh_vien"
            ].search([("sinh_vien_id.id", "in", danh_sach_sinh_vien.ids)])
            record.ket_qua_hoc_tap_sinh_vien_ids = danh_sach_ket_qua_hoc_tap_sinh_vien


class KetQuaHocTapNamHoc(models.Model):
    """
        Class này tạm thời chưa dùng do có thể hiển thị kết quả năm học dưới dạng group by trong menu
        quản lý kết quả học tập theo học kỳ
    """

    _name = "qldt.ket_qua_hoc_tap_nam_hoc"
    _description = "Kết quả học tập theo năm học"

    nam_hoc_id = fields.Many2one(
        comodel_name="nam_hoc", ondelete="set null", string="Năm học"
    )

    sinh_vien_hoc_ky_ids = fields.One2many(
        comodel_name="qldt.sinh_vien_hoc_ky",
        inverse_name="ket_qua_hoc_tap_nam_hoc_id",
        string="Kết quả học tập của SV theo học kỳ"
    )

    sinh_vien_id = fields.Many2one(
        comodel_name=model_sinh_vien,
        ondelete="cascade",
        string="Sinh viên"
    )
    ten_sv = fields.Char(
        related="sinh_vien_id.name",
        store=True,
        string="Tên đầy đủ"
    )
    ctk_nganh_id = fields.Many2one(
        comodel_name=model_chuong_trinh_khung,
        ondelete="cascade",
        related="sinh_vien_id.ctk_nganh_id",
        store=True,
        string="Chương trình khung ngành"
    )
    ctk_chuyen_nganh_id = fields.Many2one(
        comodel_name=model_chuong_trinh_khung,
        ondelete="cascade",
        related="sinh_vien_id.ctk_chuyen_nganh_id",
        store=True,
        string="Chương trình khung chuyên ngành"
    )

    diem_tb_tich_luy_nam_hoc= fields.Float(
        string="Điểm TBCTL năm học"
    )
    diem_tb_chung_nam_hoc = fields.Float(
        string="Điểm TBC năm học"
    )
    tong_so_tin_chi_trong_nam_hoc = fields.Integer(
        string="Số tín chỉ năm học"
    )
    tong_so_tin_chi_tich_luy_sau_nam_hoc = fields.Integer(
        string="Số tín chỉ tích lũy sau năm học"
    )
    diem_tb_tich_luy_nam_hoc_thang_4 = fields.Float(
        string="Điểm TBCTL năm học thang 4"
    )
    diem_tb_chung_nam_hoc_thang_4 = fields.Float(
        string="Điểm TBC năm học thang 4"
    )
    trang_thai = fields.Char(
        string="Trạng thái"
    )
    # ky_nam_hoc = fields.Many2one(
    #     comodel_name='ky_nam_hoc',
    #     ondelete='cascade',
    #     string="Kỳ năm học"
    # )
    # khoi_lop = fields.Many2one(
    #     comodel_name='khoi_lop',
    #     string="Tên khối lớp"
    # )
    # lop_hanh_chinh = fields.Char(
    #     related='ket_qua_hoc_ky_id.lop_hanh_chinh',
    #     store=True,
    #     string="Lớp hành chính"
    # )

    # diem_tb_nam_hoc_thang_4 = fields.Float(
    #     string="Điểm trung bình năm học - thang 4"
    # )
    # diem_tb_nam_hoc_thang_10 = fields.Float(
    #     string="Điểm trung bình năm học- thang 10"
    # )
    # xep_loai_hoc_luc_nam_hoc = fields.Many2one(
    #     comodel_name='qldt.quy_tac_xep_loai_hoc_luc',
    #     ondelete='set null',
    #     string='Xếp loại học lực'
    # )
    #
    # @api.depends('diem_tb_nam_hoc_thang_10')
    # def _compute_xep_loai_hoc_luc(self):
    #     '''
    #         Fetch bộ quy tắc đánh gía kết quả học tập, sau đó đối chiếu điểm -> lấy ra kết quả học lực
    #     '''
    #     for record in self:
    #         quy_tac_xep_loai_hoc_luc = self.env['qldt.quy_tac_xep_loai_hoc_luc'].search([])
    #         if record.diem_tb_nam_hoc_thang_10 != -1:
    #             for muc_hoc_luc in quy_tac_xep_loai_hoc_luc:
    #                 if muc_hoc_luc.gia_tri_diem_thang_10_min \
    #                         <= record.diem_tb_hoc_ky_thang_10 \
    #                         <= record.gia_tri_diem_thang_10_max:
    #                     record.xep_loai_hoc_luc_nam_hoc = muc_hoc_luc.id
    #         elif record.diem_tb_nam_hoc_thang_4 != -1:
    #             for muc_hoc_luc in quy_tac_xep_loai_hoc_luc:
    #                 if muc_hoc_luc.gia_tri_diem_thang_4_min \
    #                         <= record.diem_tb_hoc_ky_thang_4 \
    #                         <= record.gia_tri_diem_thang_4_max:
    #                     record.xep_loai_hoc_luc_nam_hoc = muc_hoc_luc.id


"""
========================================================
"""

"""
    Phần dưới đây là các Model xử lý kết quả học tập,
    Quy tắc xử lý kết quả học tập được mô tả ở file quy_tac_danh_gia_ket_qua_hoc_tap.py
    Khi vượt quá giới hạn số dòng 1 file .py theo PEP-8 thì cần chuyển sang file mới
"""


class SinhVienBiCanhCaoHocTap(models.Model):
    """
        Class này Mô hình hóa thông tin sinh viên bị cảnh cáo học tập:
        TODO:
            - Lấy thông tin từ bảng sinh viên - học kỳ (quản lý thông tin sinh viên theo học kỳ) thay vì
                bảng sinh viên - lớp tín chỉ - điểm số

    """
    _name = "qldt.sinh_vien_bi_canh_cao_hoc_tap"
    _description = "Quản lý danh sách sinh viên bị cảnh cáo học tập"

    sinh_vien_hoc_ky_id = fields.Many2one(
        comodel_name='qldt.sinh_vien_hoc_ky',
        ondelete='cascade',
        string="Kết quả học tập của sinh viên theo học kỳ"
    )

    sinh_vien_id = fields.Many2one(
        comodel_name="sinh_vien",
        related="sinh_vien_hoc_ky_id.sinh_vien_id",
        store=True,
        string="Sinh viên",
    )
    ten_sinh_vien = fields.Char(
        related="sinh_vien_hoc_ky_id.ten_sv",
        string="Tên đầy đủ"
    )
    ky_nam_hoc_id = fields.Many2one(
        related="sinh_vien_hoc_ky_id.ky_nam_hoc_id",
        ondelete="cascade",
        store=True,
        string="Kỳ năm học",
    )
    khoi_lop_id = fields.Many2one(
        comodel_name="khoi_lop",
        ondelete="cascade",
        compute="_compute_tinh_khoi_lop_theo_sinh_vien",
        store=True,
        string="Khối lớp",
    )
    quy_tac_xu_ly = fields.Many2one(
        comodel_name="qldt.quy_tac_xu_ly_ket_qua_hoc_tap_theo_tin_chi",
        ondelete="set null",
        string="Hình thức xử lý",
    )

    nguyen_nhan = fields.Html(
        string="Nguyên nhân"
    )
    @api.depends("sinh_vien_id")
    def _compute_tinh_khoi_lop_theo_sinh_vien(self):
        for record in self:
            if record.sinh_vien_id:
                record.khoi_lop_id = record.sinh_vien_id.khoi_lop_id.id
            else:
                record.khoi_lop_id = False

    def test(self):
        _logger.info(
            "\n\n test tính năng lấy danh sách sinh viên bị cảnh cáo học tập holyshitttt\n\n")


class SinhVienBiThoiHoc(models.Model):
    _name = "qldt.sinh_vien_bi_thoi_hoc"
    _description = "Quản lý danh sách sinh viên bị thôi học"

    sinh_vien_id = fields.Many2one(
        comodel_name="sinh_vien",
        ondelete="cascade",
        string="Mã sinh viên",
    )
    # sinh viên - lớp tín chỉ - điểm số
    sv_ltc_ds_id = fields.Many2one(
        comodel_name="sv_ltc_ds", ondelete="cascade", string="Kết quả học tập"
    )
    ky_nam_hoc_id = fields.Many2one(
        comodel_name="ky_nam_hoc",
        ondelete="cascade",
        compute="_compute_tinh_ky_nam_hoc_theo_lop_tin_chi",
        store=True,
        string="Kỳ năm học",
    )
    khoi_lop_id = fields.Many2one(
        comodel_name="khoi_lop",
        ondelete="cascade",
        compute="_compute_tinh_khoi_lop_theo_sinh_vien",
        store=True,
        string="Khối lớp",
    )
    quy_tac_xu_ly = fields.Many2one(
        comodel_name="qldt.quy_tac_xu_ly_ket_qua_hoc_tap_theo_tin_chi",
        ondelete="set null",
        string="Hình thức xử lý",
    )
    hinh_thuc_dao_tao_id = fields.Many2one(
        comodel_name="hinh_thuc_dao_tao",
        related="sinh_vien_id.hinh_thuc_dao_tao_id",
        string="Hình thức đào tạo"
    )
    thoi_gian_dao_tao_toi_da = fields.Float(
        related='hinh_thuc_dao_tao_id.thoi_gian_dao_tao_toi_da',
        store=True,
        string='Thời gian đào tạo tối đa'
    )
    bao_luu_ket_qua = fields.Boolean(string="Bảo lưu kết quả")

    @api.depends("sinh_vien_id")
    def _compute_tinh_khoi_lop_theo_sinh_vien(self):
        for record in self:
            if record.sinh_vien_id:
                record.khoi_lop_id = record.sinh_vien_id.khoi_lop_id.id

    @api.depends("sv_ltc_ds_id")
    def _compute_tinh_ky_nam_hoc_theo_lop_tin_chi(self):
        for record in self:
            if record.sv_ltc_ds_id:
                record.ky_nam_hoc_id = record.sv_ltc_ds_id.ky_hoc_id.id


class SinhVienHocLai(models.Model):
    _name = "qldt.sinh_vien_hoc_lai"
    _description = "Quản lý danh sách sinh viên học lại"

    sinh_vien_id = fields.Many2one(
        comodel_name="sinh_vien",
        related="sv_ltc_ds_id.sinh_vien_id",
        store=True,
        string="Sinh viên",
    )
    # sinh viên - lớp tín chỉ - điểm số
    sv_ltc_ds_id = fields.Many2one(
        comodel_name="sv_ltc_ds",
        ondelete="cascade",
        required=True,
        string="Mã sinh viên"
    )  # cần thay đổi string của trường này nếu thay đổi _rec_name của sv_ltc_ds
    ky_nam_hoc_id = fields.Many2one(
        comodel_name="ky_nam_hoc",
        ondelete="cascade",
        compute="_compute_tinh_ky_nam_hoc_theo_lop_tin_chi",
        store=True,
        string="Kỳ năm học",
    )
    khoi_lop_id = fields.Many2one(
        comodel_name="khoi_lop",
        ondelete="cascade",
        compute="_compute_tinh_khoi_lop_theo_sinh_vien",
        store=True,
        string="Khối lớp",
    )
    quy_tac_xu_ly = fields.Many2one(
        comodel_name="qldt.quy_tac_xu_ly_ket_qua_hoc_tap_theo_tin_chi",
        ondelete="set null",
        string="Hình thức xử lý",
    )
    lop_tin_chi_id = fields.Many2one(
        comodel_name="lop_tin_chi",
        related="sv_ltc_ds_id.lop_tin_chi_id",
        store=True,
        string="Lớp tín chỉ",
    )
    hoc_phan = fields.Many2one(
        comodel_name="slide.channel",
        related="sv_ltc_ds_id.lop_tin_chi_id.mon_hoc_ids",
        store=True,
        string="Học phần",
    )
    so_tin_chi = fields.Integer(
        related="sv_ltc_ds_id.so_tin_chi", store=True, string="Số tín chỉ"
    )
    diem_tb_hoc_phan = fields.Char(
        related="sv_ltc_ds_id.diem_tong_ket",
        store=True,
        string="Điểm trung bình học phần",
    )
    diem_tong_ket_dang_chu = fields.Char(
        related="sv_ltc_ds_id.diem_tong_ket_dang_chu",
        store=True,
        string="Điểm xếp loại (chữ)",
    )

    @api.depends("sinh_vien_id")
    def _compute_tinh_khoi_lop_theo_sinh_vien(self):
        for record in self:
            if record.sinh_vien_id:
                record.khoi_lop_id = record.sinh_vien_id.khoi_lop_id.id
            else:
                record.khoi_lop_id = False

    @api.depends("sv_ltc_ds_id")
    def _compute_tinh_ky_nam_hoc_theo_lop_tin_chi(self):
        for record in self:
            if record.sv_ltc_ds_id:
                record.ky_nam_hoc_id = record.sv_ltc_ds_id.ky_hoc_id.id
            else:
                record.ky_nam_hoc_id = False


# class DanhMucThangDiemChu(models.Model):
#     _name = 'qldt.diem.danh_muc_thang_diem_chu'
#     _description = 'Danh mục thang điểm chữ'
#     _rec_name = 'ma_thang_diem'
#
#     ma_thang_diem = fields.Char("Mã thang điểm")
#     ten_thang_diem = fields.Char("Tên thang điểm")
#     van_ban_quy_dinh_id = fields.Many2one(
#         comodel_name='danh_muc.van_ban_quy_dinh',
#         ondelete='set null',
#         string='Văn bản quy định'
#     )
#     thang_diem_dau_vao = fields.
#
# class DiemChu(models.Model):
#     _name = 'qldt.diem.diem_chu'
#     _description = 'Thang điểm chữ'
#
#     ma_thang_diem = fields.Many2one(
#         comodel_name='qldt.diem.danh_muc_thang_diem_chu',
#         ondelete='set null',
#         string='Mã thang điểm'
#     )
#     ten_thang_diem = fields.Char(
#         related='ma_thang_diem.ten_thang_diem',
#         store=True,
#         string="Tên thang điểm"
#     )
#     ky_hieu_diem = fields.Char(
#         string="Ký hiệu điểm"
#     )
#
#     ghi_chu = fields.Html(
#         string="Ghi chú"
#     )
