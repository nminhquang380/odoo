from odoo import fields, models, api
from odoo.exceptions import ValidationError


class CongNo(models.Model):
    _name = "qldt.cong_no"
    _description = "Quản lý công nợ"
    _rec_name = "ma_ho_ten_sinh_vien"

    # ma_dich_vu = fields.Char('Mã dịch vụ')
    # ten_dich_vu = fields.Char('Tên dịch vụ')
    # mo_ta_ngan_dich_vu = fields.Html('Mô tả dịch vụ')

    khoa_nganh_id = fields.Char(
        related="sinh_vien_id.khoi_lop_id.khoa_nganh_id.ten_khoa_nganh",
        store=True,
        string="Khóa sinh viên",
    )
    khoi_lop_id = fields.Char(
        related="sinh_vien_id.khoi_lop_id.ten_khoi_lop", store=True, string="Khối lớp"
    )
    ma_ho_ten_sinh_vien = fields.Char(
        compute="_tinh_ma_ho_ten_sinh_vien", store=True, string="Sinh viên"
    )
    sinh_vien_id = fields.Many2one(
        comodel_name="sinh_vien", ondelete="cascade", string="Sinh viên"
    )
    ten_day_du_sinh_vien = fields.Char(
        related="sinh_vien_id.name", string="Tên sinh viên"
    )
    ma_dinh_danh = fields.Char(
        related="sinh_vien_id.ma_dinh_danh", string="Mã sinh viên")
    # cần thêm logic validate kỳ năm học
    # trường ky_nam_hoc_id đang không dùng nhưng không hiểu sao bỏ là lỗi :v
    ky_nam_hoc_id = fields.Many2one(
        comodel_name="ky_nam_hoc", ondelete="set null", string="Kỳ năm học"
    )
    # công nợ âm - sinh viên nợ trường, và ngược lại
    cong_no = fields.Integer(
        # default=0,
        compute="_compute_tinh_cong_no",
        string="Công nợ",
        group_operator=False,
        store=True,
    )

    so_tien_phai_nop = fields.Integer(
        compute="_compute_tinh_so_tien_phai_nop",
        store=True,
        string="Số tiền phải trả",
        group_operator=False,
    )

    so_tien_duoc_nhan = fields.Integer(
        string="Số tiền được hưởng", group_operator=False
    )

    so_tien_sv_da_thanh_toan = fields.Integer(
        string="Số tiền SV đã thanh toán", group_operator=False
    )
    so_tien_nha_truong_da_thanh_toan = fields.Integer(
        string="Số tiền nhà trường đã thanh toán", group_operator=False
    )

    hoa_don_ids = fields.One2many(
        comodel_name="qldt.hoa_don",
        inverse_name="cong_no_id",
        string="Danh sách hóa đơn",
    )

    @api.depends(
        "sinh_vien_id",
    )
    def _tinh_ma_ho_ten_sinh_vien(self):
        for record in self:
            record.ma_ho_ten_sinh_vien = str(record.ma_dinh_danh) + " - " + str(record.ten_day_du_sinh_vien)

    @api.depends(
        "so_tien_phai_nop",
        "so_tien_duoc_nhan",
        "so_tien_sv_da_thanh_toan",
        "so_tien_nha_truong_da_thanh_toan",
        "hoa_don_ids",
    )
    def _compute_tinh_cong_no(self):
        for record in self:
            so_tien_phai_nop = 0
            so_tien_nha_truong_da_nhan = 0
            for vl in record.hoa_don_ids:
                so_tien_phai_nop += vl.tong_so_tien
                so_tien_nha_truong_da_nhan += vl.so_tien_da_nhan
            record.so_tien_phai_nop = so_tien_phai_nop
            record.so_tien_sv_da_thanh_toan = so_tien_nha_truong_da_nhan
            if not record.so_tien_phai_nop:
                record.so_tien_phai_nop = 0
            if not record.so_tien_duoc_nhan:
                record.so_tien_duoc_nhan = 0
            # record.cong_no = (record.so_tien_phai_nop - record.so_tien_sv_da_thanh_toan) + (record.so_tien_duoc_nhan - record.so_tien_nha_truong_da_thanh_toan)
            record.cong_no = (record.so_tien_sv_da_thanh_toan - record.so_tien_phai_nop) - (
                        record.so_tien_nha_truong_da_thanh_toan - record.so_tien_duoc_nhan)
            # else:
            #     record.cong_no = 0 # cần check lại logic đoạn này



    @api.constrains("sinh_vien_id")
    def unique_sv_cong_no(self):
        for record in self:
            cong_no = self.env["qldt.cong_no"].search([("sinh_vien_id","=", record.sinh_vien_id.id)])
            if len(cong_no) > 1:
                raise ValidationError(f"Sinh viên {record.sinh_vien_id.ma_dinh_danh} đã có bản ghi công nợ trên hệ thống!")


# class Phi(models.Model):
#     """
#         Quản lý các loại phí trong 1 bản ghi công nợ của 1 sinh viên
#     """
#
#     _name = "qldt.phi"
#     _description = "Quản lý chi tiết các loại phí"
#     _rec_name = "ten_loai_phi"
#
#     ten_loai_phi = fields.Char("Tên loại phí")
#     thuoc_danh_muc_phi = fields.Many2one(
#         comodel_name="danh_muc.phi", ondelete="set null", string="Thuộc danh mục phí"
#     )
#     bieu_gia_id = fields.Many2one(
#         comodel_name="danh_muc.bieu_gia", ondelete="set null", string="Biểu giá áp dụng"
#     )
#     don_gia = fields.Integer(related="bieu_gia_id.gia_tien", string="Đơn giá")
#     so_luong = fields.Integer(string="Số lượng")
#     tong_so_tien_du_kien = fields.Integer(
#         compute="_compute_tinh_tong_so_tien_du_kien",
#         store=True,
#         string="Tổng số tiền dự kiến",
#     )
#     tong_so_tien_thuc_te = fields.Integer(
#         compute="_compute_tinh_tong_so_tien_thuc_te",
#         store=True,
#         string="Tổng số tiền thực tế",
#     )
#     thuoc_ban_ghi_cong_no_id = fields.Many2one(
#         comodel_name="qldt.cong_no", ondelete="cascade", string="Thuộc bản ghi công nợ"
#     )
#
#     @api.depends("tong_so_tien_du_kien")
#     def _compute_tinh_tong_so_tien_thuc_te(self):
#         """
#             Cần check lại logic tính tổng số tiền thực tế của đoạn này
#         """
#         for record in self:
#             record.tong_so_tien_thuc_te = record.tong_so_tien_du_kien
#
#     @api.depends("so_luong", "don_gia")
#     def _compute_tinh_tong_so_tien_du_kien(self):
#         for record in self:
#             record.tong_so_tien_du_kien = record.don_gia * record.so_luong

class HoaDon(models.Model):
    """
        Hóa đơn của sinh viên sau mỗi lần đăng ký tín chỉ
    """

    _name = "qldt.hoa_don"
    _description = "Hóa đơn"
    _rec_name = "ten_hoa_don"
    ten_hoa_don = fields.Char("Tên hóa đơn")
    ma_hoa_don = fields.Char("Mã hóa đơn")

    _sql_constraints = [
        ('unique_ma_hoa_don', 'unique(ma_hoa_don)',
         "Mã hóa đơn đã tồn tại")
    ]

    mo_ta_dich_vu = fields.Text("Mô tả dịch vụ")
    tong_so_tien = fields.Float(
        compute="_tinh_tong_so_tien",
        store=True,
        string="Tổng số tiền",
    )
    cong_no_id = fields.Many2one(
        comodel_name="qldt.cong_no", ondelete="cascade", string="Thuộc bản ghi công nợ"
    )
    sinh_vien_id = fields.Many2one(
        related="cong_no_id.sinh_vien_id", string="Sinh viên"
    )
    ap_dung_thanh_toan_truc_tuyen = fields.Boolean(string="Áp dụng thanh toán trực tuyến", default=False)
    so_tien_da_nhan = fields.Float(string="Số tiền nhà trường đã nhận")
    cong_no_hoa_don = fields.Float(string="Công nợ hóa đơn", compute="_tinh_cong_no_hoa_don", store=True)
    ma_thanh_toan = fields.Char(string="Mã thanh toán")
    so_tien_tren_ma_thanh_toan = fields.Float(string="Số tiền yêu cầu trên mã thanh toán")
    trang_thai = fields.Selection(selection=[
        ('-1', 'Chưa thanh toán'),
        ('0', 'Thanh toán thiếu'),
        ('1', 'Thanh toán đủ'),
        ('2', 'Thanh toán thừa'),
    ], string="Trạng thái hóa đơn", compute="_tinh_trang_thai_thanh_toan", store=True, default='-1')
    gia_tien_mot_dich_vu = fields.Float(string="Giá tiền 01 đơn vị dịch vụ")
    so_luong_don_vi_dich_vu = fields.Float(string="Số lượng đơn vị dịch vụ")
    ky_nam_hoc_id = fields.Many2one(
        comodel_name="ky_nam_hoc", ondelete="set null", string="Thuộc kỳ năm học"
    )
    hinh_thuc_dao_tao_id = fields.Many2one(comodel_name="hinh_thuc_dao_tao", related="ky_nam_hoc_id.hinh_thuc_dao_tao_id",
                                           string="Hình thức đào tạo")
    ngay_nop_tien = fields.Datetime(string="Ngày nộp tiền")
    khoan_thu_id = fields.Many2one(
        comodel_name="danh_muc.khoan_thu",
        ondelete="set null",
        string="Mã khoản thu (nếu có)"
    )

    @api.depends("gia_tien_mot_dich_vu", "so_luong_don_vi_dich_vu")
    def _tinh_tong_so_tien(self):
        for record in self:
            if record.gia_tien_mot_dich_vu and record.so_luong_don_vi_dich_vu:
                record.tong_so_tien = record.gia_tien_mot_dich_vu * record.so_luong_don_vi_dich_vu

    @api.depends("so_tien_da_nhan", "tong_so_tien")
    def _tinh_cong_no_hoa_don(self):
        for record in self:
            record.cong_no_hoa_don = record.so_tien_da_nhan - record.tong_so_tien

    @api.depends("cong_no_hoa_don")
    def _tinh_trang_thai_thanh_toan(self):
        for record in self:
            if record.cong_no_hoa_don < 0 and (abs(record.cong_no_hoa_don) == record.tong_so_tien):
                record.trang_thai = '-1'
            elif record.cong_no_hoa_don < 0 and (abs(record.cong_no_hoa_don) < record.tong_so_tien):
                record.trang_thai = '0'
            elif record.cong_no_hoa_don == 0:
                record.trang_thai = '1'
            elif record.cong_no_hoa_don > 0:
                record.trang_thai = '2'


