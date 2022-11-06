import logging
from odoo import models, api, fields
from odoo.exceptions import ValidationError
from .constants_of_selection_fields import trang_thai_ket_qua_mon_hoc
from . import common_model_name

_logger = logging.getLogger(__name__)

"""
    File này chứa các quy tắc đánh giá kết quả học tập như sau:
        - Quy tắc quy đổi học phần tương đương
        - Quy tắc đánh gía tính điểm học phần: từ thang 10 -> điểm chữ -> thang 4
        - Quy tắc xếp loại học lực
        - Quy tắc xử lý, cảnh bảo kết quả học tập theo tín chỉ:
            - Học lại
            - Cảnh cáo học tập
            - Buộc thôi học
"""

class DanhMucQuyTacDanhGiaTinhDiemHocPhan(models.Model):
    """
        Model này sẽ định nghĩa một nhóm quy tắc đổi điểm 10 -> chữ -> thang4 từ điểm 0=>10
    """
    _name = "qldt.danh_muc_quy_tac_danh_gia_tinh_diem_hoc_phan"
    _description = "Danh mục quy tắc đánh giá - tính điểm học phần"
    _rec_name = "ten_danh_muc_quy_tac"

    ten_danh_muc_quy_tac = fields.Char("Tên danh mục quy tắc", required="True")
    ma_danh_muc_quy_tac = fields.Char("Mã danh mục quy tắc", required="True")
    van_ban_quy_dinh = fields.Many2one(
        comodel_name=common_model_name.model_danh_muc_van_ban_quy_dinh,
        ondelete="set null",
        string="Văn bản quy định",
    )
    hinh_thuc_dao_tao_ap_dung = fields.Many2one(
        comodel_name='hinh_thuc_dao_tao',
        string='Hình thức đào tạo áp dụng')
    quy_tac_danh_gia_tinh_tiem_hoc_phan = fields.One2many("qldt.quy_tac_danh_gia_tinh_diem_hoc_phan", "danh_muc_quy_danh_gia_tinh_tiem_hoc_phan", string="Các quy tắc đánh giá tính điểm học phần")


class QuyTacDanhGiaTinhDiemHocPhan(models.Model):
    """
        Định nghĩa quy tắc đổi điểm thang 10 -> điểm chữ -> thang 4
        Định nghĩa này là từng khoảng điểm và được tổng hợp trong DanhMucQuyTacDanhGiaTinhDiemHocPhan
    """

    _name = "qldt.quy_tac_danh_gia_tinh_diem_hoc_phan"
    _description = "Quy tắc đánh giá - tính điểm học phần"
    _rec_name = "ma_quy_tac"

    ma_quy_tac = fields.Char("Mã quy tắc", required="True")
    van_ban_quy_dinh = fields.Many2one(
        comodel_name=common_model_name.model_danh_muc_van_ban_quy_dinh,
        ondelete="set null",
        string="Văn bản quy định",
    )
    # lưu ý các loai_hoc_phan_ap_dung đã được gán với logic trong sv_ltc_ds nên chú ý khi sửa
    loai_hoc_phan_ap_dung = fields.Selection(
        [
            ("hoc_phan_tinh_diem", "Học phần tính điểm"),
            ("hoc_phan_khong_tinh_diem", "Học phần không tính điểm"),
            ("hoc_phan_dac_biet_khac", "Học phần đặc biệt khác"),
        ],
        string="Loại học phần áp dụng",
    )
    danh_muc_quy_danh_gia_tinh_tiem_hoc_phan = fields.Many2one(
        comodel_name="qldt.danh_muc_quy_tac_danh_gia_tinh_diem_hoc_phan",
        ondelete="cascade",
        string="Danh mục quy tắc đánh giá - tính điểm học phần",)
    gia_tri_diem = fields.Char(string="Điểm quy đổi hệ chữ", required="True")
    # !!! Do theo quy chế điểm hệ 10 => điểm hệ chữ => điểm hệ 4 nên sẽ không có điểm hệ 4 min-max.
    # Điểm hệ 4 sẽ được quy đổi trực tiếp theo khoảng từ điểm hệ 10
    # gia_tri_diem_thang_4_max = fields.Float(string="Giá trị điểm thang 4 tối đa")
    # gia_tri_diem_thang_4_min = fields.Float(string="Giá trị điểm thang 4 tối thiểu")
    gia_tri_diem_thang_4 = fields.Float(string="Giá trị quy đổi điểm thang 4")
    gia_tri_diem_thang_10_max = fields.Float(string="Giá trị điểm thang 10 tối đa", required="True")
    gia_tri_diem_thang_10_min = fields.Float(string="Giá trị điểm thang 10 tối thiểu", required="True")
    ghi_chu = fields.Html(string="Ghi chú")
    da_qua = fields.Boolean(string="Đã đạt")

    trang_thai_hoc_phan = fields.Selection(
        selection=trang_thai_ket_qua_mon_hoc,
        string="Trạng thái học phần", required=True
    )
    # @api.constrains("gia_tri_diem_thang_4_max")
    # def validate_gia_tri_diem_thang_4_max(self):
    #     if self.gia_tri_diem_thang_4_max < 0 or self.gia_tri_diem_thang_4_max > 4:
    #         raise ValidationError("Giá trị điểm thang 4 tối đa không đúng!")
    #
    # @api.constrains("gia_tri_diem_thang_4_min")
    # def validate_gia_tri_diem_thang_4_min(self):
    #     if self.gia_tri_diem_thang_4_min < 0 or self.gia_tri_diem_thang_4_min > 4:
    #         raise ValidationError("Giá trị điểm thang 4 tối thiểu không đúng!")

    @api.constrains("gia_tri_diem_thang_10_max")
    def validate_gia_tri_diem_thang_10_max(self):
        for record in self:
            if record.gia_tri_diem_thang_10_max < 0 or record.gia_tri_diem_thang_10_max > 10:
                raise ValidationError("Giá trị điểm thang 10 tối đa không đúng!")

    @api.constrains("gia_tri_diem_thang_10_min")
    def validate_gia_tri_diem_thang_10_min(self):
        for record in self:
            if record.gia_tri_diem_thang_10_min < 0 or record.gia_tri_diem_thang_10_min > 10:
                raise ValidationError("Giá trị điểm thang 10 tối thiểu không đúng!")
    #TODO validate cả trường hợp điểm min>max


class QuyTacDanhGiaTinhDiemHocKy(models.Model):
    _name = "qldt.quy_tac_danh_gia_tinh_diem_hoc_ky"
    _description = "Quy tắc đánh giá - tính điểm học kỳ"
    _rec_name = "ma_quy_tac"

    ma_quy_tac = fields.Char("Mã quy tắc", required="True")
    van_ban_quy_dinh = fields.Many2one(
        comodel_name=common_model_name.model_danh_muc_van_ban_quy_dinh,
        ondelete="set null",
        string="Văn bản quy định",
    )
    gia_tri_diem = fields.Char(string="Giá trị điểm chữ")
    # 2 điểm này cần có validate giới hạn 0 <= x <= 10 hoặc 4
    diem_quy_doi_thang_4 = fields.Float(string="Điểm quy đổi thang 4")
    diem_quy_doi_thang_10 = fields.Float(string="Điểm quy đổi thang 10")

    ghi_chu = fields.Html("Ghi chú")

    # ap_dung_cho_loai_hoc_phan = fields.Selection([
    #     ('hoc_phan_co_tinh_diem',"Học phần có tính điểm"),
    #     ('hoc_phan_khong_tinh_diem','Học phần không tính điểm'),
    # ],string='Áp dụng cho loại học phần')

    @api.constrains("diem_quy_doi_thang_4")
    def validate_diem_quy_doi_thang_4(self):
        if self.diem_quy_doi_thang_4 < 0 or self.diem_quy_doi_thang_4 > 4:
            raise ValidationError("Giá trị điểm quy đổi thang 4 không đúng!")

    @api.constrains("diem_quy_doi_thang_10")
    def validate_diem_quy_doi_thang_10(self):
        if self.diem_quy_doi_thang_10 < 0 or self.diem_quy_doi_thang_10 > 10:
            raise ValidationError("Giá trị điểm quy đổi thang 10 không đúng!")

class DanhMucQuyTacXepLoaiHocLuc(models.Model):
    """
        Model này sẽ định nghĩa danh mục quy tắc tính điểm học lực của sinh viên
    """
    _name = "qldt.danh_muc_quy_tac_xep_loai_hoc_luc"
    _description = "Danh mục quy tắc đánh giá - tính điểm học lực"
    _rec_name = "ten_danh_muc_quy_tac"

    ten_danh_muc_quy_tac = fields.Char("Tên danh mục quy tắc", required="True")
    van_ban_quy_dinh = fields.Many2one(
        comodel_name=common_model_name.model_danh_muc_van_ban_quy_dinh,
        ondelete="set null",
        string="Văn bản quy định",
    )
    quy_tac_danh_gia_xep_loai_hoc_luc = fields.One2many(comodel_name="qldt.quy_tac_xep_loai_hoc_luc", inverse_name="danh_muc_quy_tac_danh_gia_xep_loai_hoc_luc", string="Các quy tắc đánh giá xếp loại học lực")


class QuyTacXepLoaiHocLuc(models.Model):
    """
        Định nghĩa quy tắc xếp loại học lực theo thông tư 08: SV được xếp loại học lực theo 3 loại điểm sau:
            - Điểm TB học kỳ
            - Điểm TB năm học
            - Điểm TB tích lũy
            6. Sinh viên được xếp trình độ năm học căn cứ số tín chỉ tích lũy được
            từ đầu khóa học (gọi tắt là N) và số tín chỉ trung bình một năm học theo kế
            hoạch học tập chuẩn (gọi tắt là M), cụ thể như sau >> đoạn này hơi tối nghĩa nên hem hỉu
    """

    _name = "qldt.quy_tac_xep_loai_hoc_luc"
    _description = " Quy tắc xếp loại học lực"

    ma_quy_tac = fields.Char("Mã quy tắc")
    van_ban_quy_dinh = fields.Many2one(
        comodel_name=common_model_name.model_danh_muc_van_ban_quy_dinh,
        ondelete="set null",
        string="Văn bản quy định",
    )
    loai_hoc_luc = fields.Char(string="Loại học lực")
    gia_tri_diem_thang_4_max = fields.Float(string="Giá trị điểm thang 4 tối đa")
    gia_tri_diem_thang_4_min = fields.Float(string="Giá trị điểm thang 4 tối thiểu")
    gia_tri_diem_thang_10_max = fields.Float(string="Giá trị điểm thang 10 tối đa")
    gia_tri_diem_thang_10_min = fields.Float(string="Giá trị điểm thang 10 tối thiểu")
    danh_muc_quy_tac_danh_gia_xep_loai_hoc_luc = fields.Many2one("qldt.danh_muc_quy_tac_xep_loai_hoc_luc", string="Danh mục quy tắc xếp loại học lực")

    @api.constrains("gia_tri_diem_thang_4_max")
    def validate_gia_tri_diem_thang_4_max(self):
        if self.gia_tri_diem_thang_4_max < 0 or self.gia_tri_diem_thang_4_max > 4:
            raise ValidationError("Giá trị điểm thang 4 tối đa không đúng!")

    @api.constrains("gia_tri_diem_thang_4_min")
    def validate_gia_tri_diem_thang_4_min(self):
        if self.gia_tri_diem_thang_4_min < 0 or self.gia_tri_diem_thang_4_min > 4:
            raise ValidationError("Giá trị điểm thang 4 tối thiểu không đúng!")

    @api.constrains("gia_tri_diem_thang_10_max")
    def validate_gia_tri_diem_thang_10_max(self):
        if self.gia_tri_diem_thang_10_max < 0 or self.gia_tri_diem_thang_10_max > 10:
            raise ValidationError("Giá trị điểm thang 10 tối đa không đúng!")

    @api.constrains("gia_tri_diem_thang_10_min")
    def validate_gia_tri_diem_thang_10_min(self):
        if self.gia_tri_diem_thang_10_min < 0 or self.gia_tri_diem_thang_10_min > 10:
            raise ValidationError("Giá trị điểm thang 10 tối thiểu không đúng!")


class QuyTacXuLyKetQuaHocTapTheoTinChi(models.Model):
    _name = "qldt.quy_tac_xu_ly_ket_qua_hoc_tap_theo_tin_chi"
    _description = "Quy tắc xử lý kết quả học tập theo tín chỉ"
    _rec_name = "hinh_thuc_xu_ly"

    ma_quy_tac = fields.Char("Mã quy tắc")
    van_ban_quy_dinh = fields.Many2one(
        comodel_name=common_model_name.model_danh_muc_van_ban_quy_dinh,
        ondelete="set null",
        string="Văn bản quy định",
    )
    hinh_thuc_xu_ly = fields.Char(string="Hình thức xử lý")
    # class này cần bổ sung các điều kiện tương ứng với từng hình thức xử lý
    # căn cứ theo điều 11 chương III của thông tư 08-2021
