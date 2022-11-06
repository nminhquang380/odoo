import re

from odoo import fields, models, api
from odoo.exceptions import ValidationError

from .constants_of_selection_fields import cap_don_vi, loai_don_vi


class DanhMucVanBanQuyDinh(models.Model):
    _name = "danh_muc.van_ban_quy_dinh"
    _description = "Quản lý Danh mục Văn bản quy định"
    _rec_name = "ma_van_ban_quy_dinh"

    ma_van_ban_quy_dinh = fields.Char("Mã Văn bản quy định", required=True)
    ten_van_ban_quy_dinh = fields.Char("Tên Văn bản quy định", required=True)
    noi_dung_tom_tat = fields.Text("Nội dung tóm tắt")
    file_dinh_kem = fields.Binary("File đính kèm", required=True)
    ten_file_dinh_kem = fields.Char("Tên file đính kèm")
    hinh_thuc_dao_tao_ids = fields.Many2many(comodel_name='hinh_thuc_dao_tao',
                                             string='Hình thức đào tạo')
    _sql_constraints = [
        ('unique_ma_van_ban_quy_dinh', 'unique (ma_van_ban_quy_dinh)',
         'Mã văn bản quy định đã được sử dụng'),
    ]


class DanhMucKhoa(models.Model):
    _name = "danh_muc.khoa"
    _description = "Quản lý danh mục khoa"
    _rec_name = "ten_khoa"

    ma_khoa = fields.Char("Mã khoa", required=True)
    ten_khoa = fields.Char("Tên khoa", required=True)
    so_dien_thoai = fields.Char("Điện thoại liên hệ")
    email = fields.Char("Email")
    gioi_thieu_khoa = fields.Html("Giới thiệu khoa")
    hinh_thuc_dao_tao_ids = fields.Many2many(comodel_name='hinh_thuc_dao_tao',
                                             string='Hình thức đào tạo')

    @api.constrains("so_dien_thoai")
    def validate_phone(self):
        if self.so_dien_thoai:
            match = re.match("^[0-9]\d{9,10}$", self.so_dien_thoai)
            if not match:
                raise ValidationError("Số điện thoại không đúng!")

    @api.constrains("email")
    def _kiem_tra_email(self):
        for record in self:
            reg = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            match = re.fullmatch(
                reg,
                record.email,
            )
            if match is None:
                raise models.ValidationError("Email chưa đúng định dạng!")


class DanhMucNganhHoc(models.Model):
    """
        Định nghĩa danh mục ngành học
        TODO:
        - Phân quyền chi tiết hơn cho QTV hệ từ xa:
            - QTV hệ từ xa có được edit các thông tin liên quan đến danh mục ngành học của hình thức đào tạo từ xa không?
            - ....
    """
    _name = "danh_muc.nganh_hoc"
    _description = "Quản lý Danh mục ngành học"
    _rec_name = "ten_nganh_hoc"

    ma_nganh_hoc = fields.Char("Mã ngành học", required=True)
    ten_nganh_hoc = fields.Char("Tên ngành học", required=True)
    ma_khoa_quan_ly = fields.Many2one(comodel_name="danh_muc.khoa",
                                      ondelete="set null",
                                      string="Khoa quản lý")
    van_ban_quy_dinh_id = fields.Many2one(
        comodel_name="danh_muc.van_ban_quy_dinh",
        ondelete="set null",
        string="Văn bản quy định",
    )
    file_dinh_kem = fields.Binary("File đính kèm")
    ten_file_dinh_kem = fields.Char("Tên file đính kèm")
    hinh_thuc_dao_tao_ids = fields.Many2many(comodel_name='hinh_thuc_dao_tao',
                                             string='Hình thức đào tạo')

    _sql_constraints = [
        (
            "ma_nganh_hoc_unique",
            "UNIQUE(ma_nganh_hoc)",
            "Mã ngành học đã được sử dụng! Mỗi ngành học chỉ có 01 mã duy nhất.",
        ),
    ]

    @api.model
    def create(self, values):
        """
            Nếu danh mục ngành học đã tồn tại thì ghi đè
            TODO:
                1. làm rõ logic xem có ghi đè danh mục ngành học nếu ngành đã tồn tại ?
                2. hình thức đào tạo là many2many -> có cần import cả cột này không ?
        """
        nganh_hoc_da_ton_tai = self.env['danh_muc.nganh_hoc'].search([
            ('ma_nganh_hoc', '=', values['ma_nganh_hoc'])
        ])
        if not nganh_hoc_da_ton_tai:
            res = super(DanhMucNganhHoc, self).create(values)
            return res
        else:
            # xử lý trường hợp import many2many (nếu cần): file import cần có 2 dòng, cùng 1 mã ngành - tên ngành
            # nhưng khác hình thức đào tạo, trong code sẽ append phần hình thức đào tạo
            return nganh_hoc_da_ton_tai


class DanhMucChuyenNganh(models.Model):
    _name = "danh_muc.chuyen_nganh"
    _description = "Quản lý Danh mục chuyên ngành"
    _rec_name = "ma_chuyen_nganh"

    ma_chuyen_nganh = fields.Char("Mã chuyên ngành", required=True)
    ten_chuyen_nganh = fields.Char("Tên chuyên ngành", required=True)
    ma_nganh_hoc = fields.Many2one(comodel_name="danh_muc.nganh_hoc",
                                   ondelete="set null",
                                   string="Thuộc ngành ")
    van_ban_quy_dinh_id = fields.Many2one(
        comodel_name="danh_muc.van_ban_quy_dinh",
        ondelete="set null",
        string="Văn bản quy định",
    )
    file_dinh_kem = fields.Binary("File đính kèm")
    ten_file_dinh_kem = fields.Char("Tên file đính kèm")
    hinh_thuc_dao_tao_ids = fields.Many2many(comodel_name='hinh_thuc_dao_tao',
                                             string='Hình thức đào tạo')


class DanhMucHocPhan(models.Model):
    _name = "danh_muc.hoc_phan"
    _description = "Quản lý danh mục học phần"
    _rec_name = "ma_hoc_phan"

    ma_hoc_phan = fields.Char("Mã học phần", required=True)
    ten_hoc_phan = fields.Char("Tên học phần", required=True)
    van_ban_quy_dinh_id = fields.Many2one(
        comodel_name="danh_muc.van_ban_quy_dinh",
        ondelete="set null",
        string="Văn bản quy định",
    )
    file_dinh_kem = fields.Binary("File đính kèm")
    ten_file_dinh_kem = fields.Char("Tên file đính kèm")


class DanhMucPhi(models.Model):
    _name = "danh_muc.phi"
    _description = "Quản lý danh mục phí"
    _rec_name = "ten_phi"

    ma_phi = fields.Char("Mã loại phí", required=True)
    ten_phi = fields.Char("Tên loại phí")
    don_vi_tien_te = fields.Char(default="VND", string="Đơn vị tiền tệ")
    van_ban_quy_dinh_id = fields.Many2one(
        comodel_name="danh_muc.van_ban_quy_dinh",
        ondelete="set null",
        string="Văn bản quy định",
    )
    # gia_tien = fields.Integer(
    #     # default = 0,
    #     string="Giá tiền"
    # )
    file_dinh_kem = fields.Binary("File đính kèm")
    ten_file_dinh_kem = fields.Char("Tên file đính kèm")
    hinh_thuc_dao_tao_id = fields.Many2many(comodel_name='hinh_thuc_dao_tao',
                                            string='Hình thức đào tạo')
    _sql_constraints = [
        ('unique_ma_phi', 'unique (ma_phi)', 'Mã loại phí đã được sử dụng'),
    ]

    @api.constrains("gia_tien")
    def validate_gia_tien(self):
        if self.gia_tien <= 0:
            raise ValidationError("Giá tiền không hợp lệ!")


class DanhMucBieuGia(models.Model):
    _name = "danh_muc.bieu_gia"
    _description = "Quản lý danh mục biểu giá"
    _rec_name = "ten_bieu_gia"

    # ma_bieu_gia = fields.Char('Mã biểu giá')
    loai_phi_id = fields.Many2one(comodel_name="danh_muc.phi",
                                  ondelete="set null",
                                  string="Loại phí")
    ma_bieu_gia = fields.Char("Mã biểu giá", required=True)
    ten_bieu_gia = fields.Char("Tên biểu giá", required=True)
    gia_tien = fields.Integer(
        # default = 0,
        string="Giá tiền")
    don_vi_tien_te = fields.Char(default="VND", string="Đơn vị tiền tệ")
    nam_hoc_ap_dung = fields.Many2one(comodel_name="nam_hoc",
                                      string="Năm học áp dụng")
    khoa_nganh_ids = fields.One2many(comodel_name="khoa_nganh",
                                     inverse_name="bieu_gia_id",
                                     string="Khóa ngành áp dụng")
    van_ban_quy_dinh_id = fields.Many2one(
        comodel_name="danh_muc.van_ban_quy_dinh",
        ondelete="set null",
        string="Văn bản quy định",
    )
    file_dinh_kem = fields.Binary("File đính kèm")
    ten_file_dinh_kem = fields.Char("Tên file đính kèm")
    hinh_thuc_dao_tao_id = fields.Many2many(comodel_name='hinh_thuc_dao_tao',
                                            string='Hình thức đào tạo')
    _sql_constraints = [
        ('unique_ma_bieu_gia', 'unique (ma_bieu_gia)',
         'Mã biểu giá đã được sử dụng'),
    ]

    @api.constrains("gia_tien")
    def validate_gia_tien(self):
        if self.gia_tien <= 0:
            raise ValidationError("Giá tiền không hợp lệ!")


class DanhMucCoSoDaoTao(models.Model):
    """
        Thông tin cơ bản của 1 cơ sở đào tạo, dùng cho quản lý danh mục
    """

    _name = "danh_muc.co_so_dao_tao"
    _description = "Quản lý thông tin tóm tắt của cơ sở đào tạo"
    _rec_name = "ten_co_so_dao_tao"

    ten_co_so_dao_tao = fields.Char(string="Tên cơ sở đào tạo")
    ky_hieu_co_so_dao_tao = fields.Char(string="Ký hiệu cơ sở đào tạo")
    so_dien_thoai = fields.Char(string="Số điện thoại")
    dia_chi = fields.Char(string="Địa chỉ")
    ghi_chu = fields.Html(string="Ghi chú")
    _sql_constraints = [
        ('unique_ky_hieu_co_so_dao_tao', 'unique (ky_hieu_co_so_dao_tao)',
         'Ký hiệu cơ sở đào tạo đã được sử dụng'),
    ]

    @api.constrains("so_dien_thoai")
    def validate_phone(self):
        if self.so_dien_thoai:
            match = re.match("^[0-9]\d{9,10}$", self.so_dien_thoai)
            if not match:
                raise ValidationError("Số điện thoại không đúng!")

    # TODO: valid số điện thoại

class DanhMucTrinhDoHinhDaoTao(models.Model):
    _name = "danh_muc.trinh_do_hinh_dao_tao"
    _description = "Quản lý thông tin trình độ, hình thức đào tạo"
    _rec_name = "ten_trinh_do_hinh_dao_tao"

    ten_trinh_do_hinh_dao_tao = fields.Char(string="Tên trình độ, hình thức đào tạo")
    ky_hieu_trinh_do_hinh_dao_tao = fields.Char(string="Ký hiệu trình độ, hình thức đào tạo")
    hinh_thuc_dao_tao_id = fields.Many2one(comodel_name="hinh_thuc_dao_tao",
                                        string="Hình thức đào tạo")

    _sql_constraints = [
        ('unique_ky_hieu_trinh_do_hinh_dao_tao', 'unique (ky_hieu_trinh_do_hinh_dao_tao)',
         'Ký hiệu trình độ, hình thức đào tạo đã được sử dụng'),
    ]
    
class PhuongPhapDanhGiaHocPhan(models.Model):
    """
        class này dùng để quản lý phương pháp đánh giá học phần
            Một phương pháp đánh giá học phần gắn với 1 hình thức đào tạo nhất định và
                có một danh sách các đầu điểm tương ứng
                chỗ này cần xem xét để bổ sung thêm các thông tin khác
    """

    _name = "danh_muc.phuong_phap_danh_gia_hoc_phan"
    _description = "Phương pháp đánh giá học phần"
    _rec_name = "mo_ta_phuong_phap"

    mo_ta_phuong_phap = fields.Char(string="Tên phương pháp")
    hinh_thuc_dao_tao_ap_dung = fields.Many2one(
        comodel_name="hinh_thuc_dao_tao",
        ondelete="set null",
        string="Hình thức đào tạo áp dụng",
    )
    dau_diem_ids = fields.Many2many(comodel_name="danh_muc.dau_diem",
                                    string="Danh sách đầu điểm sử dụng")

    # @api.onchange("hinh_thuc_dao_tao_ap_dung")
    # def them_hau_to_vao_mo_ta_phuong_phap(self):
    #     for record in self:
    #         if (
    #             record.hinh_thuc_dao_tao_ap_dung.ten_hinh_thuc_dao_tao_viet_tat
    #             and record.mo_ta_phuong_phap
    #         ):
    #             record.mo_ta_phuong_phap += (
    #                 "-"
    #                 + record.hinh_thuc_dao_tao_ap_dung.ten_hinh_thuc_dao_tao_viet_tat
    #             )


class DanhMucDauDiem(models.Model):
    """
        class này dùng để quản lý danh mục đầu điểm tương ứng với một phương pháp đánh giá học phần
        danh mục đầu điểm gồm danh sách các tên đầu điểm áp dụng cho một phương pháp đánh giá nhất định
        Ví dụ:
            Đối với trung tâm 1, khóa D17 trở về trước chỉ có 1 đầu điểm là điểm thi cuối phần
            Từ khóa D18 thì dùng 3 đầu điểm
            Các khóa sau này dùng bao nhiêu đầu điểm thì vẫn chưa rõ
            Đối với hệ chính quy thì có 5 đầu điểm cho 1 môn, kể cả điểm thi cuối phần
        Do đó cần dùng class này cho việc quản lý số lượng đầu điểm khác nhau cho từng khóa đào tọa
        Đầu điểm khác với trọng số, vì đầu điểm là tên của điểm, còn trọng số là tỉ trọng của điểm đó trong bước
            đánh giá kết quả học phần
    """

    _name = "danh_muc.dau_diem"
    _description = "Quản lý tên đầu điểm"
    _rec_name = "ten_dau_diem"
    ten_dau_diem = fields.Char(string="Tên đầu điểm")
    phuong_phap_danh_gia_hoc_phan_id = fields.Many2many(
        comodel_name="danh_muc.phuong_phap_danh_gia_hoc_phan",
        string="Được sử dụng trong phương pháp đánh giá",
    )


class DanhMucDonVi(models.Model):
    """
        Class này mô tả 1 node trong cây cơ cấu tổ chức
        Schema dữ liệu được kế thừa từ:
            https://gitlab.com/livw08/sotaysinhvien-v4/-/blob/ptit/src/modules/khoa/khoa.schema.ts
        Đơn vị là một định nghĩa tổng quát, bao gồm: Học viện, cơ sở đào tạo, khoa, bộ môn, phòng, ban, trung tâm...
    """
    _name = "danh_muc.don_vi"
    _description = "Quản lý thông tin đơn vị"
    _rec_name = "ma_don_vi"

    _parent_store = True
    _parent_name = "don_vi_cap_tren_id"
    parent_path = fields.Char(index=True)

    ten_don_vi = fields.Char(string='Tên đơn vị')
    ma_don_vi = fields.Char(string='Mã đơn vị')
    don_vi_cap_tren_id = fields.Many2one(comodel_name="danh_muc.don_vi",
                                         string="Đơn vị cấp trên")
    don_vi_cap_duoi_ids = fields.One2many(comodel_name="danh_muc.don_vi",
                                          inverse_name="don_vi_cap_tren_id",
                                          string="Danh sách đơn vị cấp dưới")

    ma_don_vi_cap_tren = fields.Char(string="Mã đơn vị cấp trên",
                                     help="Mã đơn vị cấp cao hơn, \
        ví dụ, đơn vị hiện tại là bộ môn thì mã đơn vị cấp cao hơn là mã khoa tương ứng"
                                     )
    is_root = fields.Boolean(string="Là node gốc?")
    loai_don_vi = fields.Selection(selection=loai_don_vi, string="Loại đơn vị")
    cap_don_vi = fields.Selection(selection=cap_don_vi, string="Cấp đơn vị")
    _sql_constraints = [
        ('unique_ma_don_vi', 'unique (ma_don_vi)',
         'Mã đơn vị đã được sử dụng'),
    ]


class DanhMucHDSD(models.Model):
    """
        Class này mô hình hóa hướng dẫn sử dụng, gồm các cặp <tên hướng dẫn : file đính kèm>
    """
    _name = "danh_muc.hdsd"
    _description = "Danh mục hướng dẫn sử dụng"
    _rec_name = "ma_hdsd"

    ma_hdsd = fields.Char("Mã hướng dẫn sử dụng")
    ten_hdsd = fields.Char("Tên hướng dẫn sử dụng")
    duong_dan_file = fields.Char("Đường dẫn file HDSD (nếu có)")
    duong_dan_he_thong = fields.Char("Đường dẫn hệ thống")
    # file_dinh_kem = fields.Binary("File hướng dẫn")


class DanhMucTemplateTietHoc(models.Model):
    _name = "danh_muc.template_tiet_hoc"
    _description = "Danh mục nhóm tiết học"
    _rec_name = "ma_template_tiet_hoc"

    ma_template_tiet_hoc = fields.Char(string='Mã nhóm tiết học',
                                       required=True)
    ten_template_tiet_hoc = fields.Char(string='Tên nhóm tiết học',
                                        required=True)

    tiethoc_id = fields.One2many(
        comodel_name="danh_muc.tiet_hoc",
        inverse_name="template_tiet_hoc_id",
    )
    hinh_thuc_dao_tao_id = fields.Many2one(comodel_name="hinh_thuc_dao_tao",
                                           string="Hình thức đào tạo",
                                           required=True)
    _sql_constraints = [
        ("unique_ma_template_tiet_hoc", "UNIQUE(ma_template_tiet_hoc)",
         "Mã nhóm tiết học đã được sử dụng!"),
        ("unique_ten_template_tiet_hoc", "UNIQUE(ten_template_tiet_hoc)",
         "Tên nhóm tiết học đã được sử dụng!")
    ]


class DanhMucTietHoc(models.Model):
    _name = "danh_muc.tiet_hoc"
    _description = "Danh mục tiết học"
    _rec_name = "tiet_hoc"

    tiet_hoc = fields.Integer("Tiết học", required=True, group_operator=False)
    gio_bat_dau = fields.Integer("Giờ bắt đầu",
                                 required=True,
                                 group_operator=False)
    phut_bat_dau = fields.Integer("Phút bắt đầu",
                                  required=True,
                                  group_operator=False)
    gio_ket_thuc = fields.Integer("Giờ kết thúc",
                                  required=True,
                                  group_operator=False)
    phut_ket_thuc = fields.Integer("Phút kết thúc",
                                   required=True,
                                   group_operator=False)

    template_tiet_hoc_id = fields.Many2one(
        comodel_name="danh_muc.template_tiet_hoc",
        string="Nhóm tiết học",
        required=True)

    hinh_thuc_dao_tao_id = fields.Many2one(
        related="template_tiet_hoc_id.hinh_thuc_dao_tao_id",
        store=True,
        string="Hình thức đào tạo",
    )

    _sql_constraints = [(
        "validate_gio_bat_dau_constraint",
        "CHECK(gio_bat_dau >= 0 AND gio_bat_dau < 24)",
        "Sai khung giờ bắt đầu (0 - 23)!",
    ),
                        (
                            "validate_gio_ket_thuc_constraint",
                            "CHECK(gio_ket_thuc >= 0 AND gio_ket_thuc < 24)",
                            "Sai khung giờ kết thúc (0 - 23)!",
                        ),
                        (
                            "validate_phut_bat_dau_constraint",
                            "CHECK(phut_bat_dau >= 0 AND phut_bat_dau < 60)",
                            "Sai khung phút bắt đầu (0 - 59)!",
                        ),
                        (
                            "validate_phut_ket_thuc_constraint",
                            "CHECK(phut_ket_thuc >= 0 AND phut_ket_thuc < 60)",
                            "Sai khung phút kết thúc (0 - 59)!",
                        )]


class DanhMucMienGiamPhi(models.Model):
    _name = "danh_muc.mien_giam_phi"
    _description = "Danh mục miễn giảm các loại phí"
    _rec_name = "ten_loai_mien_giam"

    ten_loai_mien_giam = fields.Char(string="Tên loại phí được miễn giảm")
    van_ban_quy_dinh = fields.Many2one(
        comodel_name='danh_muc.van_ban_quy_dinh',
        ondelete='set null',
        string="Văn bản - quy định")
    kieu_mien_giam_phan_tram = fields.Float("Mức giảm tính theo %")
    kieu_mien_giam_truc_tiep = fields.Integer("Mức giảm tính theo VND")
    ghi_chu = fields.Char("Ghi chú")


class DanhMucDonViThuHuong(models.Model):
    _name = "danh_muc.don_vi_thu_huong"
    _description = "Danh mục đơn vị thụ hưởng"
    _rec_name = "ten_don_vi"

    ma_don_vi = fields.Many2one(comodel_name='danh_muc.don_vi')
    ten_don_vi = fields.Char(related="ma_don_vi.ten_don_vi",
                             store=True,
                             string="Tên đơn vị")
    so_tai_khoan = fields.Char("Số tài khoản")
    ten_ngan_hang = fields.Char("Tên ngân hàng")
    chi_nhanh = fields.Char("Chi nhánh")
    ghi_chu = fields.Char("Ghi chú")


class DanhMucKhoanThu(models.Model):
    _name = "danh_muc.khoan_thu"
    _description = "Danh mục khoản thu"
    _rec_name = "ma_khoan_thu"

    ma_khoan_thu = fields.Char(string="Mã khoản thu")
    ten_khoan_thu = fields.Char(string="Tên khoản thu")
    van_ban_quy_dinh = fields.Many2one(
        comodel_name="danh_muc.van_ban_quy_dinh",
        ondelete="cascade",
        string="Văn bản - quy định")
    ghi_chu = fields.Char(string="Ghi chú")


    _sql_constraints = [
        ('unique_ma_khoan_thu', 'unique(ma_khoan_thu)',
         "Mã khoản thu đã được sử dụng!")
    ]