import logging

from odoo import models, fields, api
from odoo.exceptions import ValidationError

from .constants_model_name import model_sinh_vien, model_ky_nam_hoc, model_chuong_trinh_khung
from .constants_of_selection_fields import trang_thai_sinh_vien_hoc_ky, quy_tac_xu_ly_ket_qua_hoc_tap_theo_tin_chi

_logger = logging.getLogger(__name__)


class SinhVienHocKy(models.Model):
    """
        Class này mô hình hóa sinh viên - học kỳ,  gồm các thông tin:
            - Mã SV
            - Kỳ năm học (VD: 20211 ~ kỳ 1 năm 2021)
            - CTK
            - Kỳ chương trình khung (VD: kỳ số 5 trong CTK CNTT 2021)
            - Tổng số tín chỉ đã đăng ký ~ số tiền phải đóng
            - Tổng số tín chỉ được miễn (căn cứ theo chương trình khung)
            - Điểm TB tích lũy học kỳ
            - Xếp loại học lực học kỳ
            ....
    """
    _name = "qldt.sinh_vien_hoc_ky"
    _description = "Quản lý thông tin sinh viên - học kỳ"
    _rec_name = "sinh_vien_id"

    sinh_vien_id = fields.Many2one(comodel_name=model_sinh_vien,
                                   ondelete="cascade",
                                   string="Sinh viên")
    ma_dinh_danh = fields.Char(related="sinh_vien_id.ma_dinh_danh",
                               store=True,
                               string="Mã sinh viên")
    ten_sv = fields.Char(related="sinh_vien_id.name",
                         store=True,
                         string="Tên đầy đủ")
    ky_nam_hoc_id = fields.Many2one(comodel_name=model_ky_nam_hoc,
                                    ondelete="cascade",
                                    string="Kỳ năm học")
    ctk_nganh_id = fields.Many2one(comodel_name=model_chuong_trinh_khung,
                                   ondelete="cascade",
                                   related="sinh_vien_id.ctk_nganh_id",
                                   store=True,
                                   string="Chương trình khung ngành")
    ctk_chuyen_nganh_id = fields.Many2one(
        comodel_name=model_chuong_trinh_khung,
        ondelete="cascade",
        related="sinh_vien_id.ctk_chuyen_nganh_id",
        store=True,
        string="Chương trình khung chuyên ngành")
    sv_ltc_ds_ids = fields.One2many(comodel_name="sv_ltc_ds",
                                          inverse_name="sinh_vien_hoc_ky_id",
                                          string="Danh sách lớp tín chỉ điểm số")
    ky_ctk = fields.Integer(string="Kỳ chương trình khung")
    tong_so_tin_chi_da_dang_ky = fields.Integer(
        string="Tổng số tín chỉ đã đăng ký",
        compute="_compute_tong_so_tin_chi",
        store=True,
    )
    tong_so_tin_chi_duoc_mien = fields.Integer(
        string="Tổng số tín chỉ được miễn"
    )  # giá trị này cần được tính theo kết quả quy đổi các học phần (nếu có) tại thời điểm đăng ký nhu cầu học tập
    diem_tb_tich_luy_hoc_ky = fields.Float(string="Điểm TBCTL học kỳ")
    diem_tb_chung_hoc_ky = fields.Float(string="Điểm TBC học kỳ")
    tong_so_tin_chi_trong_hoc_ky = fields.Integer(
        string="Số tín chỉ trong học kỳ", compute="_compute_tong_so_tin_chi", store=True)
    tong_so_tin_chi_tich_luy_sau_hoc_ky = fields.Integer(
        string="Số tín chỉ tích lũy sau học kỳ", compute="_compute_tong_so_tin_chi_tich_luy", store=True)
    so_tin_chi_truot_trong_hoc_ky = fields.Integer("Số tín chỉ trượt trong kỳ")
    tong_so_tin_chi_truot = fields.Integer("Tổng số tín chỉ trượt")
    diem_tb_tich_luy_hoc_ky_thang_4 = fields.Float(
        string="Điểm TBCTL học kỳ thang 4")
    diem_tb_chung_hoc_ky_thang_4 = fields.Float(
        string="Điểm TBC học kỳ thang 4")

    xep_loai_hoc_luc_hoc_ky = fields.Char(string="Xếp loại học lực học kỳ")
    trang_thai = fields.Selection(selection=trang_thai_sinh_vien_hoc_ky,
                                  string="Trạng thái")
    ket_qua_hoc_tap_nam_hoc_id = fields.Many2one(
        comodel_name="qldt.ket_qua_hoc_tap_nam_hoc",
        ondelete="cascade",
        string="Thuộc nhóm kết quả năm học")
    hinh_thuc_dao_tao_id = fields.Many2one(comodel_name="hinh_thuc_dao_tao",
                                           related="sinh_vien_id.hinh_thuc_dao_tao_id",
                                           string="Hình thức đào tạo")

    @api.constrains("diem_tb_tich_luy_hoc_ky_thang_4", "diem_tb_chung_hoc_ky_thang_4")
    def constrains_diem_thang_4(self):
        for record in self:
            if record.diem_tb_tich_luy_hoc_ky_thang_4 > 4 or record.diem_tb_chung_hoc_ky_thang_4 > 4:
                raise ValidationError("Điểm học kỳ thang 4 không được vượt quá 4.0!")

    @api.depends("sv_ltc_ds_ids", "sv_ltc_ds_ids.diem_tong_ket_thang_4")
    def _compute_tong_so_tin_chi_tich_luy(self):
        for record in self:
            diem_tich_luy = 0
            tong_diem = 0
            tc_tich_luy = 0
            tong_tc = 0
            for vl in record.sv_ltc_ds_ids:
                if vl.da_qua and vl.hoc_phan_id.hoc_phan_tinh_diem:
                    diem_tich_luy += (float(vl.diem_tong_ket_thang_4)*float(vl.so_tin_chi))
                    tc_tich_luy += float(vl.so_tin_chi)
                    tong_tc += float(vl.so_tin_chi)
                    tong_diem += float(vl.diem_tong_ket_thang_4)*float(vl.so_tin_chi)
                elif vl.hoc_phan_id.hoc_phan_tinh_diem:
                    tong_diem += float(vl.diem_tong_ket_thang_4)*float(vl.so_tin_chi)
                    tong_tc += float(vl.so_tin_chi)
            record.tong_so_tin_chi_tich_luy_sau_hoc_ky = tc_tich_luy
            if diem_tich_luy and tc_tich_luy:
                record.diem_tb_tich_luy_hoc_ky_thang_4 = float(diem_tich_luy/tc_tich_luy)
            if tong_diem and tong_tc:
                record.diem_tb_chung_hoc_ky_thang_4 = float(tong_diem/tong_tc)


    @api.onchange("trang_thai", "ky_nam_hoc_id.trang_thai")
    def _thuc_hien_xu_ly_ket_qua_hoc_tap(self):
        """
            Xử lý kết quả học tập:
                1. Cảnh cáo học tập
                    Nếu sinh viên bị dính 1 trong 2 điều kiện xử lý kết quả học tập thì bị cảnh cáo học tập
                        (tạo mới 1 bản ghi trong xử lý kết quả học tập)
                2. Học lại
        """

        canh_cao = self.env[
            'qldt.quy_tac_xu_ly_ket_qua_hoc_tap_theo_tin_chi'].search(
                [('hinh_thuc_xu_ly', '=', 'Bị cảnh cáo học tập')]
            )  # đoạn này tiềm ẩn lỗi trong trường hợp tên hình thức xử lý có thay đổi, không phải là "Bị cảnh cáo ... nữa"
        if self._xu_ly_ket_qua_hoc_tap_theo_dieu_kien_1() \
                or self._xu_ly_ket_qua_hoc_tap_theo_dieu_kien_2()\
                or self._xu_ly_ket_qua_hoc_tap_theo_dieu_kien_3():
            sinh_vien_da_bi_canh_cao = self.env[
                "qldt.sinh_vien_bi_canh_cao_hoc_tap"].search([
                    ("sinh_vien_hoc_ky_id", '=', self._origin.id)
                ])
            self.env["qldt.sinh_vien_bi_canh_cao_hoc_tap"].create({
                "sinh_vien_hoc_ky_id":
                self._origin.id,
                "quy_tac_xu_ly":
                canh_cao.id,
            })
        self._xu_ly_thoi_hoc()

    def _xu_ly_ket_qua_hoc_tap_theo_dieu_kien_1(self):
        """
            Hàm này kiểm tra xem sinh viên có bị cảnh cáo học tập không, nếu:
            tổng số tín bị F > tổng số tín đã đăng ký trong kỳ
        """
        # lấy danh sách các học phần sinh viên đã đăng ký trong 1 kỳ
        ds_sv_ltc_ds = self.env['sv_ltc_ds'].search([
            ('sinh_vien_id', '=', self.sinh_vien_id.id),
            ('ky_hoc_id', '=', self.ky_nam_hoc_id.id)
        ])
        _logger.info("\n\n ds_sv_ltc_ds: {}".format(ds_sv_ltc_ds))
        if not ds_sv_ltc_ds:
            return False

        so_tin_chi_bi_f = 0
        tong_so_tin_chi = 0
        for each_record in ds_sv_ltc_ds:
            tong_so_tin_chi += each_record.so_tin_chi
            if each_record.diem_tong_ket_dang_chu == 'F':
                so_tin_chi_bi_f += each_record.so_tin_chi

        if so_tin_chi_bi_f / tong_so_tin_chi > 0.5:
            return True
        return False

    def _xu_ly_ket_qua_hoc_tap_theo_dieu_kien_2(self):
        """
            Hàm này kiểm tra xem sinh viên có bị cảnh cáo học tập không, nếu:
            - điểm TB TL của học kỳ 1 năm nhất < 0.8
            - hoặc điểm TB TL của các học kỳ khác < 1.0
        """
        ket_qua_hoc_tap_ky_1_ctk = self.env['qldt.sinh_vien_hoc_ky'].search([
            ('sinh_vien_id', '=', self.sinh_vien_id.id), ('ky_ctk', '=', 1)
        ])
        ket_qua_hoc_tap_ky_khac = self.env['qldt.sinh_vien_hoc_ky'].search([
            ('sinh_vien_id', '=', self.sinh_vien_id.id), ('ky_ctk', '!=', 1)
        ])
        _logger.info("\n\n {}".format(ket_qua_hoc_tap_ky_1_ctk))
        if ket_qua_hoc_tap_ky_1_ctk and ket_qua_hoc_tap_ky_1_ctk.diem_tb_tich_luy_hoc_ky < 0.8:
            return True
        if ket_qua_hoc_tap_ky_khac:
            for diem_tb_hk in ket_qua_hoc_tap_ky_khac:
                if diem_tb_hk.diem_tb_tich_luy_hoc_ky and diem_tb_hk.diem_tb_tich_luy_hoc_ky < 1.0:
                    return True

        return False

    def _xu_ly_ket_qua_hoc_tap_theo_dieu_kien_3(self):
        """
            Hàm này kiểm tra xem sinh viên có bị cảnh cáo học tập không, nếu:
            - Điểm TB TL < 1.2 với svien năm 1 (kết thúc kỳ 1 và 2 của CTK)
                thế nào là sv năm 1: đã có 2 bản ghi kỳ 1 và 2 ở sv_hoc_ky
            - Điểm TB TL < 1.4 với SV năm 2
            - Điểm TB TL < 1.6 với SV năm 3
            - Điểm TB TL < 1.8 với SV các năm tiếp theo
        """
        # ket_qua_nam_hoc = self.env['qldt.ket_qua_hoc_tap_nam_hoc'].search([
        #     ('sinh_vien_hoc_ky_ids','in',self.id),
        # ])
        # if not ket_qua_nam_hoc: return False
        ket_qua_hoc_tap_cua_sv_theo_ky = self.env[
            'qldt.sinh_vien_hoc_ky'].search([('sinh_vien_id', '=',
                                              self.sinh_vien_id.id)])
        _logger.info(
            "\n\n kiem tra dk 3 : {}".format(ket_qua_hoc_tap_cua_sv_theo_ky))
        nam_hoc = int(len(ket_qua_hoc_tap_cua_sv_theo_ky) / 2)
        _logger.info("\n\n năm học {}".format(nam_hoc))
        if nam_hoc == 1 and self.sinh_vien_id.diem_tich_luy < 1.2:
            return True
        if nam_hoc == 2 and self.sinh_vien_id.diem_tich_luy < 1.4:
            return True
        if nam_hoc == 3 and self.sinh_vien_id.diem_tich_luy < 1.6:
            return True
        if nam_hoc > 3 and self.sinh_vien_id.diem_tich_luy < 1.8:
            return True

        return False

    @api.depends("sinh_vien_id.sv_ltc_ds_ids")
    def _compute_tong_so_tin_chi(self):
        for record in self:
            if record.sinh_vien_id.sv_ltc_ds_ids:
                ltc_ky_nay = record.sinh_vien_id.sv_ltc_ds_ids.filtered(
                    lambda x: x.ky_hoc_id == record.ky_nam_hoc_id)
                record.tong_so_tin_chi_da_dang_ky = sum(
                    [i.so_tin_chi for i in ltc_ky_nay])
                record.tong_so_tin_chi_trong_hoc_ky = record.tong_so_tin_chi_da_dang_ky
            else:
                record.tong_so_tin_chi_da_dang_ky = 0
                record.tong_so_tin_chi_trong_hoc_ky = 0

    def _xu_ly_thoi_hoc(self):
        """
            Kiểm tra các điều kiện để cho sinh viên thôi học:
                1. Thời gian học vượt quá thời gian đào tạo tối đa của hình thức đào tạo
                2. Tự ý bỏ học 1 kỳ học chính trở lên
                3. Bị cảnh cáo học vụ trên 2 lần
        """
        if self._thoi_hoc_do_vuot_qua_thoi_gian():
            quy_tac_xu_ly = self.env[
                'qldt.quy_tac_xu_ly_ket_qua_hoc_tap_theo_tin_chi'].search(
                    ['hinh_thuc_xu_ly', 'ilike', 'thôi học'])
            vals = {
                'sinh_vien_id': self.sinh_vien_id.id,
                'quy_tac_xu_ly': quy_tac_xu_ly.id
            }
            self.env['qldt.sinh_vien_bi_thoi_hoc'].create(vals)
        else:
            sv_bi_canh_cao = self.env[
                'qldt.sinh_vien_bi_canh_cao_hoc_tap'].search([
                    ('sinh_vien_id', '=', self.sinh_vien_id.id)
                ])
            if len(sv_bi_canh_cao) == 3:
                return True
        return False

    def _thoi_hoc_do_vuot_qua_thoi_gian(self):
        so_ky_hoc_toi_da_cho_phep = self.hinh_thuc_dao_tao_id.thoi_gian_dao_tao_toi_da * 2
        so_ky_da_hoc = self.env['qldt.sinh_vien_hoc_ky'].search([
            ('sinh_vien_id', '=', self.sinh_vien_id.id)
        ])
        if so_ky_da_hoc and len(so_ky_da_hoc) > so_ky_hoc_toi_da_cho_phep:
            return True
        return False
