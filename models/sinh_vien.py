from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from .constants_user_groups import portal_user
from .constants_trang_thai_sinh_vien import trang_thai_sv_dang_hoc
from .constants_of_selection_fields import trang_thai_sinh_vien
import re


class SinhVien(models.Model):
    _name = "sinh_vien"
    _description = "Sinh viên"
    _inherit = ["tac_nhan"]
    _rec_name = "ma_dinh_danh"

    user_group_string = portal_user
    vai_tro_string = "sinh_vien"
    # giá trị này lấy trong base_groups.xml tương ứng với loại user

    # giới tính kế thừa từ trường gioi_tinh của model res_partner
    #
    ghi_chu = fields.Text("Ghi chú")  # ghi chu tt1
    # Hồ sơ sinh viên Edusoft
    # MaSV = fields.Char('Mã sinh viên', size=50, required=True)

    AvatarSV = fields.Image("Avatar sinh viên")
    # MaDT = fields.Char('Mã dân tộc', size=50
    MaDT = fields.Selection(
        [
            ("1", "Kinh"),
            ("2", "Tày"),
            ("3", "Thái"),
            ("4", "Hoa"),
            ("5", "Khmer"),
            ("6", "Mường"),
            ("7", "Nùng"),
            ("8", "HMông"),
            ("9", "Dao"),
            ("10", "Gia-rai"),
            ("11", "Ngái"),
        ],
        string="Dân tộc",
    )
    # fields.Selection([('0', 'Nội chú'),
    #                   ('1', 'Thường chú'),
    #                   ('2', 'Tạm chú')], 'Loại cư trú')
    MaTG = fields.Char("Mã tôn giáo", size=50)
    MaNg = fields.Many2one(comodel_name="quan_ly_nganh_hoc.nganh",
                           ondelete="set null",
                           string="Ngành")
    MaChngNg = fields.Many2one(
        comodel_name="quan_ly_nganh_hoc.chuyen_nganh",
        ondelete="set null",
        string="Chuyên ngành",
    )
    TheThuVien = fields.Char("Thẻ thư viện", size=500)
    SoTaiKhoan = fields.Char("Số tài khoản ngân hàng", size=500)
    MaNH = fields.Char("Mã ngân hàng", size=50)
    CHINHANHNH = fields.Char("Chi nhánh ngân hàng", size=500)
    SoNamBD = fields.Integer("Số năm bộ đội")
    SoNamTNXP = fields.Integer("Số năm thanh niên xung phong")
    CanNang = fields.Float("Cân nặng")
    ChieuCao = fields.Float("Chiều cao")
    MADBQUOCTICH = fields.Char("Mã DB quốc tịch", size=500) # Quốc tịch
    CoNghe = fields.Integer("Có nghề?")
    CQCT = fields.Char("Tên cơ quan công tác", size=500)
    CVCQCT = fields.Char("Chức vụ cơ quan công tác", size=500)
    DangHoc = fields.Integer("Đang học")
    DC_DCHK = fields.Char("Địa chỉ hộ khẩu", size=500) # hộ khẩu
    DC_DCHK2 = fields.Char("Địa chỉ hộ khẩu 2", size=500)
    DC_DCLLSV = fields.Char("Địa chỉ liên lạc", size=500)
    DC_DCTT = fields.Char("Địa chỉ thường trú", size=500) # thường trú
    DC_DCVC = fields.Char("Đia chỉ vợ/chồng", size=500)
    DC_DT1HK = fields.Char("Tel hộ khẩu", size=500)
    DC_DT1LLSV = fields.Char("Điện thoại liên lạc", size=500) # Số điện thoại
    DC_DT1TT = fields.Char("Tel thường chú", size=500)
    DC_DT1VC = fields.Char("Tel vợ/chồng", size=500)
    DC_DT2HK = fields.Char("Tel hộ khẩu 2", size=500)
    DC_DT2LLSV = fields.Char("Điện thoại liên lạc 2", size=500)
    DC_DT2TT = fields.Char("Tel thường chú 2", size=500)
    DC_DT2VC = fields.Char("Tel vợ/chồng 2", size=500)
    DC_Eml1HK = fields.Char("Email hộ khẩu", size=500)
    DC_EML1LLSV = fields.Char("Email liên lạc", size=500)
    DC_Eml1TT = fields.Char("Email thường chú", size=500)
    DC_Eml1VC = fields.Char("Email vợ/chồng", size=500)
    DC_Eml2HK = fields.Char("Email hộ khẩu 2", size=500)
    DC_EML2LL = fields.Char("Email liên lạc 2", size=500)  # Trùng dc_eml2llsv?
    DC_Eml2TT = fields.Char("Email thường chú 2", size=500)
    DC_Eml2VC = fields.Char("Email vợ/chồng 2", size=500)
    DC_GcHK = fields.Char("Ghi chú địa chỉ hộ khẩu", size=500)
    DC_GcLL = fields.Char("Ghi chú địa chỉ liên lạc", size=500)
    DC_GcTT = fields.Char("Ghi chú địa chỉ thường chú", size=500)
    DC_GcVC = fields.Char("Ghi chú địa chỉ vợ chồng", size=500)
    MADBHKSV = fields.Char("Mã DB HK SV", size=500)
    MADBLLSV = fields.Char("Mã DB LL SV", size=500)
    MADBTTSV = fields.Char("Mã DB TT SV", size=500)
    MADBVCSV = fields.Char("Mã DB VC SV", size=500)
    DCCQCT = fields.Char("Địa chỉ cơ quan công tác", size=500)
    DKKinhTe = fields.Selection([("0", "Có khả năng"), ("1", "Cố gắng"),
                                 ("2", "Khó khăn")], "Điều kiện kinh tế")
    GcSV = fields.Char("Ghi chú sinh viên", size=4000)
    GcThPhanGD = fields.Char("Ghi chú thành phần gia đình", size=4000)
    MADBCQCTSV = fields.Char("Mã ĐB CQ CT", size=500)
    LoaiCuTru = fields.Selection([("0", "Nội chú"), ("1", "Thường chú"),
                                  ("2", "Tạm chú")], "Loại cư trú")
    MatCha = fields.Integer("Cha đã mất?")
    MatMe = fields.Integer("Mẹ đã mất?")
    NgayNgTru = fields.Datetime("Ngày ngoại trú")
    NgNghiepVC = fields.Char("Nghề nghiệp vợ/chồng", size=500)
    NgSinhCha = fields.Char("Ngày sinh cha", size=500)
    NgSinhMe = fields.Char("Ngày sinh mẹ", size=500)
    NguoiLL = fields.Char("Người liên lạc", size=500)
    NguonTuyen = fields.Selection(
        [
            ("0", "Trúng tuyển"),
            ("1", "Chuyển trường"),
            ("2", "Cử tuyển"),
            ("3", "Xét tuyển"),
            ("4", "Tuyển thẳng"),
            ("5", "Nguồn khác"),
        ],
        "Nguồn tuyển",
    )
    NNgCha = fields.Char("Nghề nghiệp cha", size=500)
    NNgMe = fields.Char("Nghề nghiệp mẹ", size=500)
    NoiCapCMND = fields.Char("Nơi cấp CMND", size=500)
    PhongKTX = fields.Char("Phòng kí túc xá", size=500)
    QueQuan = fields.Char("Quê quán", size=500)
    SoAnhChiEm = fields.Integer("Số anh chị em")
    TenCha = fields.Char("Tên cha", size=500)
    TenChuHo = fields.Char("Tên chủ hộ", size=500)
    TenChuHoHK = fields.Char("Tên chủ hộ (HK)", size=500)
    TenMe = fields.Char("Tên mẹ", size=500)
    TenVC = fields.Char("Tên vợ/chồng", size=500)
    ThPhanGD = fields.Selection(
        [("0", "Công nhân viên chức"), ("1", "Nhà nước"), ("2", "Khác")],
        "Thành phần gia đình",
    )
    loaiNoiSinh = fields.Selection([
        ("0", "Trong nước"),
        ("1", "Nước ngoài")
        ], string="Loại nơi sinh")
    noiSinhNuocNgoai = fields.Char("Nơi sinh nước ngoài")

    TrChuyen = fields.Char("Trường chuyển", size=500)
    # NgCapCMND = fields.Char('Ngày cấp CMND', size=500)
    NgCapCMND = fields.Date("Ngày cấp CMND")
    MADBNOISINHSV = fields.Char("Mã ĐB nơi sinh", size=500) # Nơi sinh
    DC_EML2LLSV = fields.Char("Email 2 liên lạc sinh viên", size=500)
    DC_DT1Me = fields.Char("Điện thoại liên lạc mẹ", size=500)
    DC_DT1Cha = fields.Char("Điện thoại liên lạc cha", size=500)
    GhiChuView1 = fields.Char("Ghi chú dùng bên detailright", size=500)
    TenHo = fields.Char("Tên hộ", size=500)
    DC_DTNgLL = fields.Char("Điện thoại người liên lạc", size=500)
    DC_EmlNgLL = fields.Char("Email người liên lạc", size=500)
    SoBD = fields.Char("Số báo danh", size=500)
    Diem1 = fields.Float("Điểm 1")
    Diem2 = fields.Float("Điểm 2")
    Diem3 = fields.Float("Điểm 3")
    Diem4 = fields.Float("Điểm 4")
    DiemUT = fields.Float("Điểm ưu tiên")
    Diem5 = fields.Float("Điểm 5")
    DiemTong = fields.Float("Điểm tổng")
    # NganhThi = fields.Char('Ngành thi', size=500)
    NganhThi = fields.Many2one(comodel_name="quan_ly_nganh_hoc.nganh",
                               ondelete="set null",
                               string="Ngành thi")
    KhoiThi = fields.Char("Khối thi", size=500)
    NhomKVTS = fields.Selection(
        [
            ("Khu vực 1", "1"),
            ("Khu vực 2 nông thôn", "2NT"),
            ("Khu vực 2", "2"),
            ("Khu vực 3", "3"),
        ],
        "Nhóm khu vực",
    )
    DOITUONGTS = fields.Selection(
        [
            ("0", "Không có đối tượng"),
            ("1", "Đối tượng 01"),
            ("2", "Đối tượng 02"),
            ("3", "Đối tượng 03"),
            ("4", "Đối tượng 04"),
            ("5", "Đối tượng 05"),
            ("6", "Đối tượng 06"),
            ("7", "Đối tượng 07"),
            ("8", "Nhóm đối tượng 3"),
        ],
        "Đối tượng tuyển sinh",
    )
    NAMTN = fields.Integer("Năm tốt nghiệp PTTH")
    MaSoThue = fields.Char("Mã số thuế", size=500)
    TenDVThue = fields.Char("Tên đơn vị thuế", size=500)
    TTSV = fields.Integer("Thứ tự sinh viên")
    TGianCT = fields.Char("Thời gian thâm niên công tác", size=500)
    DotTS = fields.Char("Đợt tuyển sinh", size=500)
    DIEMCHUAN = fields.Float("Điểm chuẩn theo tổ hợp xét tuyển")
    HocLuc = fields.Selection([("0", "Giỏi"), ("1", "Khá"),
                               ("2", "Trung bình"), ("3", "Yếu")], "Học lực")
    HanhKiem = fields.Selection([("0", "Tốt"), ("1", "Khá"),
                                 ("2", "Trung bình"), ("3", "Yếu")],
                                "Hạnh kiểm")
    SoBHSV = fields.Char("Số bảo hiểm sinh viên", size=50) # Bảo hiểm y tế
    MaBVKCB = fields.Char("Mã bệnh viện KCB", size=50)
    NgSinhGH = fields.Char("Ngày sinh giám hộ", size=500)
    TenGiamHo = fields.Char("Tên giám hộ", size=500)
    LoaiKhuyetTat = fields.Selection(
        [
            ("1", "Khuyết tật vận động"),
            ("2", "Khuyết tật nghe nói"),
            ("3", "Khuyết tật nhìn"),
            ("4", "Khuyết tật thần kinh tâm thần"),
            ("5", "Khuyết tật trí tuệ"),
            ("6", "Khuyết tật khác"),
        ],
        "Loại khuyết tật",
    )
    NNgGH = fields.Char("Nghề nghiệp giám hộ", size=500)
    NgayNHOC = fields.Date("Ngày nhập học")
    DVDKDTHI = fields.Char("Đơn vị đăng ký dự thi", size=500)

    lop_hanh_chinh_ids = fields.Many2many("lop_hanh_chinh",
                                          string="Danh sách lớp hành chính")
    lop_hanh_chinh_id = fields.Many2one(
        comodel_name="lop_hanh_chinh",
        compute="_compute_lop_hanh_chinh_hien_tai",
        string="Lớp hành chính hiện tại",
        store=True)
    sv_ltc_ds_ids = fields.One2many("sv_ltc_ds",
                                    "sinh_vien_id",
                                    string="Sinh viên-lớp tín chỉ-điểm số")
    sv_hp_ds_ids = fields.One2many(
        comodel_name="sv_hp_ds",
        inverse_name="sinh_vien_id",
        string="Kết quả học tập theo học phần",
    )
    lop_tin_chi_ids = fields.Many2many(comodel_name="lop_tin_chi",
                                       string="Danh sách lớp tín chỉ")
    nhom_lop_tin_chi_ids = fields.Many2many(
        comodel_name="nhom_lop_tin_chi", string="Danh sách nhóm lớp tín chỉ")

    @api.depends("sv_ltc_ds_ids")
    def _compute_danh_sach_lop_tin_chi(self):
        for record in self:
            if record.sv_ltc_ds_ids is not False:
                record.lop_tin_chi_ids = record.sv_ltc_ds_ids.mapped(
                    "lop_tin_chi_id")
            else:
                record.lop_tin_chi_ids = False

    dot_nhap_hoc_id = fields.Many2one("dot_nhap_hoc", string="Đợt nhập học")
    khoa_nganh_id = fields.Many2one(
        comodel_name="khoa_nganh",
        # related="lop_hanh_chinh_id.khoi_lop_id.khoa_nganh_id",
        store=True,
        string="Khóa ngành",
    )
    khoa_chuyen_nganh_id = fields.Many2one(
        comodel_name="khoa_chuyen_nganh",
        related="lop_hanh_chinh_id.khoa_chuyen_nganh_id",
        store=True,
        string="Khóa chuyên ngành",
    )
    # khoa_nganh_id_import = fields.Many2one(
    #     comodel_name="khoa_nganh",
    #     string="Khóa ngành (Import)",
    # )
    nganh_id = fields.Many2one(comodel_name="quan_ly_nganh_hoc.nganh",
                               related="lop_hanh_chinh_id.nganh",
                               store=True,
                               name="Ngành học")
    ten_nganh = fields.Char(string="Tên ngành",
                            related="nganh_id.name.ten_nganh_hoc",
                            store=True)
    ma_nganh = fields.Char(string="Mã ngành",
                           related="nganh_id.name.ma_nganh_hoc",
                           store=True)
    hinh_thuc_dao_tao_id = fields.Many2one(comodel_name='hinh_thuc_dao_tao',
                                           string='Hình thức đào tạo')
    trinh_hinh_id = fields.Many2one(comodel_name="danh_muc.trinh_do_hinh_dao_tao",
                                    string="Trình độ, hình thức đào tạo")
    ten_don_vi = fields.Char(string="Tên đơn vị",
                             related="don_vi_id.ten_don_vi",
                             store=True)
    ma_don_vi = fields.Char(string="Mã đơn vị",
                            related="don_vi_id.ma_don_vi",
                            store=True)
    khoi_lop_id = fields.Many2one(comodel_name="khoi_lop",
                                  related="lop_hanh_chinh_id.khoi_lop_id",
                                  store=True,
                                  string="Khối lớp")
    khoa_sinh_vien_id = fields.Many2one(
        "khoa_sinh_vien",
        string="Khóa sinh viên",
        related="lop_hanh_chinh_id.khoa_sinh_vien",
        store=True,
    )
    ctk_nganh_id = fields.Many2one(
        comodel_name="chuong_trinh_khung",
        related="lop_hanh_chinh_id.chuong_trinh_khung_nganh_id",
        # compute="_compute_chuong_trinh_khung",
        store=True,
        string="Chương trình khung ngành",
    )
    ctk_chuyen_nganh_id = fields.Many2one(
        comodel_name="chuong_trinh_khung",
        related="lop_hanh_chinh_id.chuong_trinh_khung_chuyen_nganh_id",
        store=True,
        string="Chương trình khung chuyên ngành",
    )
    cong_no_id = fields.One2many(comodel_name="qldt.cong_no",
                                 inverse_name="sinh_vien_id",
                                 string="Công nợ")
    diem_tich_luy = fields.Float(
        compute="_compute_diem_tich_luy",
        store=True,
        string="Điểm TL (thang 10)",
    )
    diem_tich_luy_thang_4 = fields.Float(
        compute="_compute_diem_tich_luy_thang_4",
        store=True,
        string="Điểm TL (thang 4)",
    )
    trang_thai = fields.Char(string="Trạng thái", default="Đang học")
    trang_thai_sinh_vien = fields.Selection(selection=trang_thai_sinh_vien,
                                            default="Đang học",
                                            string="Trạng thái sinh viên")

    @api.model
    def create(self, values):
        res = super(SinhVien, self).create(values)
        res.partner_id.sinh_vien_id = res.id
        return res

    def _create_user(self):
        user_group = self.env.ref(self.user_group_string) or False
        users_res = self.env['res.users']
        for record in self:
            if not record.user_id:
                if record.ngay_sinh:
                    password = record.ngay_sinh.strftime("%d%m%Y")
                else:
                    password = "ptitdu"
                login = str(record.ma_dinh_danh)
                match = re.match(
                    "^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$",
                    login,
                )
                if match is None:
                    login = login.upper()
                user_id = users_res.create({
                    # 'name':
                    # record.name,
                    'partner_id': record.partner_id.id,
                    'login': login,
                    'password': password,
                    'groups_id': user_group,
                    # 'tz':
                    # self._context.get('tz'),
                    'vai_tro': self.vai_tro_string,
                })
                record.user_id = user_id

    @api.depends('lop_hanh_chinh_ids')
    def _compute_lop_hanh_chinh_hien_tai(self):
        for record in self:
            if record.lop_hanh_chinh_ids:
                record.lop_hanh_chinh_id = record.lop_hanh_chinh_ids[-1]
            else:
                record.lop_hanh_chinh_id = False

    @api.depends("sv_hp_ds_ids")
    def _compute_diem_tich_luy(self):
        """
            TODO:
                1. Cẩn sửa trang_thai -> trang_thai_sinh_vien
        """
        for record in self:
            if record.sv_hp_ds_ids:
                if record.trang_thai == trang_thai_sv_dang_hoc:
                    tong_so_tin_chi = 0
                    tong_diem = 0
                    for ban_ghi in record.sv_hp_ds_ids:
                        if ban_ghi.diem_hoc_phan != 0:
                            tong_diem += ban_ghi.diem_hoc_phan * ban_ghi.so_tin_chi
                            tong_so_tin_chi += ban_ghi.so_tin_chi
                        else:
                            if ban_ghi.ghi_chu and ban_ghi.ghi_chu != "":
                                continue
                    if tong_so_tin_chi != 0:
                        record.diem_tich_luy = tong_diem / tong_so_tin_chi
                else:
                    record.diem_tich_luy = 0
            else:
                record

    @api.depends("diem_tich_luy")
    def _compute_diem_tich_luy_thang_4(self):
        """
            TODO:
                1. Cẩn sửa trang_thai -> trang_thai_sinh_vien
        """
        for record in self:
            if record.diem_tich_luy:
                # tính tạm, công thức này bị sai, công thức đúng là tính điểm tất cả các môn thang 4 * tín chỉ / tổng số tín chỉ
                if record.trang_thai == trang_thai_sv_dang_hoc:
                    record.diem_tich_luy_thang_4 = record.diem_tich_luy * 0.4
                else:
                    record.diem_tich_luy_thang_4 = 0