import logging
from odoo import fields, models, api
from odoo.exceptions import ValidationError
from .constants_trang_thai_sinh_vien import trang_thai_sv_hp_hoc_lai
from .constants_of_selection_fields import trang_thai_ket_qua_mon_hoc

_logger = logging.getLogger(__name__)


class SinhVienLopTinChiDiemSo(models.Model):
    _name = "sv_ltc_ds"
    _description = "Sinh viên-lớp tín chỉ-điểm số"
    _rec_name = "sinh_vien_id"

    sinh_vien_id = fields.Many2one("sinh_vien",
                                   string="Sinh viên",
                                   ondelete="cascade")
    lop_tin_chi_id = fields.Many2one("lop_tin_chi",
                                     string="Lớp tín chỉ",
                                     ondelete="cascade")
    ma_hoa_lich_hoc_lop_tin_chi = fields.Char(
        string="Mã hóa lịch học lớp tín chỉ",
        related="lop_tin_chi_id.ma_hoa_lich_hoc",
        store=True,
    )
    ma_lop = fields.Char(string="Mã lớp",
                         related="lop_tin_chi_id.ma_lop",
                         store=True)
    so_tin_chi = fields.Integer("Số tín chỉ", related="hoc_phan_id.so_tin_chi")
    hoc_phan_id = fields.Many2one(
        "slide.channel",
        "Học phần",
        related="lop_tin_chi_id.mon_hoc_ids",
        store=True,
        readonly=False,
    )
    ten_hoc_phan = fields.Char(
        string="Học phần",
        related="hoc_phan_id.ten_hoc_phan",
        store=True,  # đặt store=true để group by trên list view
    )
    ky_hoc = fields.Char(string="Kỳ học",
                         related="ky_hoc_id.ma_ky_nam_hoc",
                         store=True)
    # thêm trường này để phục vụ tạo search panel bên tay trái
    # mặc dù có thể không thật sự cần thiết
    ky_hoc_id = fields.Many2one(
        comodel_name="ky_nam_hoc",
        related="lop_tin_chi_id.ky_nam_hoc_id",
        store=True,
        string="Kỳ năm học",
        readonly=False,
    )
    nam_hoc = fields.Char(string="Năm học",
                          related="nam_hoc_id.ten_nam_hoc",
                          store=True)
    nam_hoc_id = fields.Many2one(
        comodel_name="nam_hoc",
        string="Năm học",
        related="lop_tin_chi_id.ky_nam_hoc_id.nam_hoc_id",
        store=True,
    )
    khoi_lop = fields.Char(string="Khối lớp",
                           related="sinh_vien_id.khoi_lop_id.ten_khoi_lop",
                           store=True)
    so_thu_tu_lop = fields.Integer("Số thứ tự lớp",
                                   related="lop_tin_chi_id.so_thu_tu_lop",
                                   store=True)
    dot_dk_tin_chi = fields.Many2one(
        "dot_dang_ky_tin_chi",
        related="lop_tin_chi_id.dot_dk_tin_chi_id",
        store=True)
    # slide_channel_partner_id = fields.Many2one(
    #     "slide.channel.partner",
    #     compute="_compute_slide_channel_partner",
    #     store=True
    # )
    # quy_tac_tinh_diem_dang_su_dung = fields.Many2one(
    #     comodel_name="qldt.quy_tac_danh_gia_tinh_diem_hoc_phan",
    #     ondelete="set null",
    #     compute="_compute_cap_nhat_diem_tong_ket_theo_quy_tac_moi",
    #     store=True,
    #     string="Quy tắc tính điểm đang sử dụng",
    # )
    # store lại để phục vụ hiển thị
    ma_dinh_danh = fields.Char("Mã sinh viên",
                               related="sinh_vien_id.ma_dinh_danh",
                               store=True)
    name = fields.Char("Tên sinh viên",
                       related="sinh_vien_id.name",
                       store=True)

    email = fields.Char("Email đăng nhập",
                        related="sinh_vien_id.email",
                        store=True)

    # Diem tieng anh
    is_diem_tieng_anh = fields.Boolean("Có phải là học phần tiếng Anh?",
                                       default=False)
    diem_nghe = fields.Char("Điểm nghe")
    diem_doc = fields.Char("Điểm đọc")
    diem_viet = fields.Char("Điểm viết")
    diem_noi = fields.Char("Điểm nói")
    diem_tong_tieng_anh = fields.Char("Điểm tổng tiếng Anh")

    ###########################################################################################
    # các loại trọng số
    diem_attendance = fields.Float("Điểm tham gia học tập trên lớp",
                                   default=False,
                                   group_operator=False)
    diem_trung_binh_kiem_tra_tren_lop = fields.Float(
        "Điểm trung bình các bài kiểm tra trên lớp",
        default=False,
        group_operator=False)
    diem_bai_tap = fields.Float("Điểm bài tập/thuyết trình theo nhóm",
                                default=False,
                                group_operator=False)
    diem_thi_nghiem = fields.Float(string="Điểm thí nghiệm - thực hành",
                                   group_operator=False)
    diem_cuoi_ky = fields.Char("Điểm kiểm tra cuối kỳ",
                               default=False,
                               group_operator=False)
    tu_dong_tinh_diem = fields.Boolean(default=False,
                                       string="Tự động tính điểm tổng kết")
    du_dau_diem = fields.Boolean(default=False, string="Đã đủ các đầu điểm")
    da_qua = fields.Boolean(string="Đã đạt", default=False)
    trang_thai_sv_ltc_ds = fields.Selection(
        selection=trang_thai_ket_qua_mon_hoc,
        string="Trang thái",
    )
    ##########################################################################################
    # các loại điểm tổng kết
    diem_thi_lan_2 = fields.Char(string="Điểm thi lần 2")
    diem_tong_ket = fields.Char(
        string="Điểm tổng kết",
        compute="_compute_diem_tong_ket_new",
        store=True,
        readonly=False,
        group_operator=False,
    )
    diem_tong_ket_thang_4 = fields.Char(
        compute="_compute_diem_tong_ket_thang_4_new",
        store=True,
        string="Điểm tổng kết - thang 4",
    )
    diem_tong_ket_dang_chu = fields.Char(
        compute="_compute_diem_tong_ket_dang_chu_new",
        store=True,
        string="Điểm TK dạng chữ")
    loai_hoc_phan_ap_dung = fields.Selection(
        [
            (
                "1",
                "Học phần tính điểm",
            ),  # cần xem xét cách đăt tên key, nên để là '1' hay 'hoc_phan_tinh_diem')
            ("2", "Học phần không tính điểm"),
            ("3", "Học phần đặc biệt khác"),
        ],
        default="1",
        string="Loại học phần áp dụng",
    )
    sv_hp_ds_id = fields.Many2one("sv_hp_ds", store=True)
    sinh_vien_hoc_ky_id = fields.Many2one("qldt.sinh_vien_hoc_ky", store=True)
    # sv_hp_ds_id = fields.Many2one("sv_hp_ds",
    #                               compute="_compute_sv_hp_ds_id_new",
    #                               store=True)
    # sinh_vien_hoc_ky_id = fields.Many2one(
    #     "qldt.sinh_vien_hoc_ky",
    #     compute="_compute_sinh_vien_hoc_ky_id",
    #     store=True)
    _sql_constraints = [
        (
            "check_range_diem_attendance",
            "CHECK(diem_attendance >= 0 AND diem_attendance <= 10)",
            "Điểm tham gia học tập trên lớp không trong ngưỡng từ 0 đến 10.",
        ),
        (
            "check_range_diem_bai_tap",
            "CHECK(diem_bai_tap >= 0 AND diem_bai_tap <= 10)",
            "Điểm bài tập/thuyết trình theo nhóm không trong ngưỡng từ 0 đến 10.",
        ),
        (
            "check_range_diem_trung_binh_kiem_tra_tren_lop",
            "CHECK(diem_trung_binh_kiem_tra_tren_lop >= 0 AND diem_trung_binh_kiem_tra_tren_lop <= 10)",
            "Điểm trung bình các bài kiểm tra trên lớp không trong ngưỡng từ 0 đến 10.",
        ),
        (
            "check_range_diem_cuoi_ky",
            "CHECK(diem_cuoi_ky >= 0 AND diem_cuoi_ky <= 10)",
            "Điểm cuối kỳ không trong ngưỡng từ 0 đến 10",
        ),
        ("unique_sv_ltc_nhom_lop_tc",
         "UNIQUE(sinh_vien_id, lop_tin_chi_id, nhom_lop_tin_chi_id)",
         "Sinh viên đã ở trong lớp này"),
    ]

    @api.depends(
        "diem_attendance",
        "diem_bai_tap",
        "diem_trung_binh_kiem_tra_tren_lop",
        "diem_cuoi_ky",
        "lop_tin_chi_id.ts_attendance",
        "lop_tin_chi_id.ts_bai_tap",
        "lop_tin_chi_id.ts_trung_binh_kiem_tra_tren_lop",
        "lop_tin_chi_id.ts_cuoi_ky",
        "tu_dong_tinh_diem",
        "du_dau_diem",
    )
    def _compute_diem_tong_ket_new(self):
        """
            Hàm '_compute_diem_tong_ket' cũ đang là 'Nếu đủ các đầu điểm thì tính điểm tổng kết, nếu không thì thôi'
            như thế sẽ không hợp lý khi một sinh viên bị 0 điểm một đầu điểm thành phần => viết hàm mới này
            TODO: xử lý trường hợp số lượng các ddau diem thay doi theo quy che dao tao
        """
        for record in self:
            if record.tu_dong_tinh_diem and record.du_dau_diem:
                ts_attendance = record.lop_tin_chi_id.ts_attendance
                ts_bai_tap = record.lop_tin_chi_id.ts_bai_tap
                ts_thi_nghiem = record.lop_tin_chi_id.ts_thi_nghiem
                ts_trung_binh_kiem_tra_tren_lop = (
                    record.lop_tin_chi_id.ts_trung_binh_kiem_tra_tren_lop)
                ts_cuoi_ky = record.lop_tin_chi_id.ts_cuoi_ky
                #đoạn 4 dòng dưới chưa hiểu lắm là theo quy chế nào
                if record.diem_cuoi_ky == "C" or record.diem_cuoi_ky == "V" or record.diem_cuoi_ky == "DC":
                    record.diem_tong_ket = "0"
                elif record.diem_cuoi_ky == "H":
                    record.diem_tong_ket = False
                elif ((not record.diem_attendance and ts_attendance)
                      or (not record.diem_bai_tap and ts_bai_tap)
                      or (not record.diem_trung_binh_kiem_tra_tren_lop
                          and ts_trung_binh_kiem_tra_tren_lop)
                      or (not record.diem_cuoi_ky and ts_cuoi_ky)):
                    record.diem_tong_ket = 0
                else:
                    record.diem_tong_ket = (
                        (record.diem_attendance * ts_attendance +
                         record.diem_bai_tap * ts_bai_tap +
                         record.diem_trung_binh_kiem_tra_tren_lop *
                         ts_trung_binh_kiem_tra_tren_lop +
                         record.diem_thi_nghiem * ts_thi_nghiem +
                         float(record.diem_cuoi_ky) * ts_cuoi_ky) / 100)

    @api.depends(
        "diem_tong_ket",
    )
    def _compute_diem_tong_ket_dang_chu_new(self):
        for record in self:
            print("Có chạy nha")
            if record.tu_dong_tinh_diem:
                danh_muc_quy_tac_tinh_diem = record.hoc_phan_id.hinh_thuc_dao_tao_id.danh_muc_quy_tac_tinh_diem_hoc_phan_id
                if not danh_muc_quy_tac_tinh_diem:
                    raise ValidationError(
                        f"Hình thức đào tạo {record.hoc_phan_id.hinh_thuc_dao_tao_id.ten_hinh_thuc_dao_tao} chưa có danh mục quy tắc đánh giá điểm học phần"
                    )
                quy_tac_tinh_diem_tong_ket = self.env[
                    "qldt.quy_tac_danh_gia_tinh_diem_hoc_phan"].search([
                    ("danh_muc_quy_danh_gia_tinh_tiem_hoc_phan", "=",
                     danh_muc_quy_tac_tinh_diem.id)])
                if not quy_tac_tinh_diem_tong_ket:
                    raise ValidationError("Không tìm thấy quy tắc tính điểm học phần!")
                #khi không có điểm tổng kết => chưa đủ đầu điểm
                if record.diem_tong_ket == None or record.diem_tong_ket == '':
                    for gia_tri_diem in quy_tac_tinh_diem_tong_ket:
                        if gia_tri_diem.trang_thai_hoc_phan == 'chua_du_dau_diem':
                            record.diem_tong_ket_dang_chu = gia_tri_diem.gia_tri_diem
                            record.trang_thai_sv_ltc_ds = 'chua_du_dau_diem'
                            return record.trang_thai_sv_ltc_ds
                #khi có điểm tổng kết và học phần không tính điểm
                elif not record.hoc_phan_id.hoc_phan_tinh_diem and record.diem_tong_ket:
                    for gia_tri_diem in quy_tac_tinh_diem_tong_ket:
                        if gia_tri_diem.loai_hoc_phan_ap_dung == 'hoc_phan_khong_tinh_diem' and (gia_tri_diem.gia_tri_diem_thang_10_min <= float(
                                record.diem_tong_ket) <=
                                gia_tri_diem.gia_tri_diem_thang_10_max):
                            record.diem_tong_ket_dang_chu = gia_tri_diem.gia_tri_diem
                            record.trang_thai_sv_ltc_ds = gia_tri_diem.trang_thai_hoc_phan
                            return record.trang_thai_sv_ltc_ds
                #khi có điểm tổng kết và học phần có tính điểm
                elif record.diem_tong_ket and record.hoc_phan_id.hoc_phan_tinh_diem:
                    for gia_tri_diem in quy_tac_tinh_diem_tong_ket:
                        if gia_tri_diem.loai_hoc_phan_ap_dung == 'hoc_phan_tinh_diem' and (gia_tri_diem.gia_tri_diem_thang_10_min <= float(
                                record.diem_tong_ket) <=
                                gia_tri_diem.gia_tri_diem_thang_10_max):
                            record.diem_tong_ket_dang_chu = gia_tri_diem.gia_tri_diem
                            record.trang_thai_sv_ltc_ds = gia_tri_diem.trang_thai_hoc_phan
                            return record.trang_thai_sv_ltc_ds
                else:
                    record.diem_tong_ket_dang_chu = False

    @api.depends("diem_tong_ket_dang_chu")
    def _compute_diem_tong_ket_thang_4_new(self):
        """
            Theo thông tư 08 thì điểm thang 10 -> điểm chữ -> điểm thang 4
            Điểm thang 4 dùng để tính điểm trung bình học kỳ, năm học hoặc tích lũy
        """
        for record in self:
            if record.tu_dong_tinh_diem:
                if record.diem_tong_ket_dang_chu:
                    danh_muc_quy_tac_tinh_diem = record.hoc_phan_id.hinh_thuc_dao_tao_id.danh_muc_quy_tac_tinh_diem_hoc_phan_id
                    if not danh_muc_quy_tac_tinh_diem:
                        raise ValidationError(
                            f"Hình thức đào tạo {record.hoc_phan_id.hinh_thuc_dao_tao_id.ten_hinh_thuc_dao_tao} chưa có danh mục quy tắc đánh giá điểm học phần"
                        )
                    quy_tac_tinh_diem_hoc_phan = self.env[
                        "qldt.quy_tac_danh_gia_tinh_diem_hoc_phan"].search([
                            ("danh_muc_quy_danh_gia_tinh_tiem_hoc_phan", "=",
                             danh_muc_quy_tac_tinh_diem.id)
                        ])
                    if not quy_tac_tinh_diem_hoc_phan:
                        raise ValidationError(
                            "Không tìm thấy quy tắc tính điểm học phần!")
                    for vl in quy_tac_tinh_diem_hoc_phan:
                        if (record.diem_tong_ket_dang_chu == vl.gia_tri_diem):
                            record.diem_tong_ket_thang_4 = vl.gia_tri_diem_thang_4
                            break
                else:
                    record.diem_tong_ket_thang_4 = False


    @api.depends("diem_tong_ket")
    def _compute_sv_hp_ds_id_new(self):
        hoc_phan_ids = self.mapped("hoc_phan_id.id")
        sv_hp_ds = self.env["sv_hp_ds"].search([("hoc_phan_id", "in",
                                                 hoc_phan_ids)])
        map_sv_hp = {}
        for record in self:
            hoc_phan_instance = sv_hp_ds.filtered(
                lambda x: x.sinh_vien_id == record.sinh_vien_id and x.
                hoc_phan_id == record.hoc_phan_id)
            # hoc_phan_instance = self.env["sv_hp_ds"].search([
            #     ("sinh_vien_id", "=", record.sinh_vien_id.id),
            #     ("hoc_phan_id", "=", record.hoc_phan_id.id),
            # ])
            if len(hoc_phan_instance) > 0:
                record.sv_hp_ds_id = hoc_phan_instance[0]
            else:
                if record.sinh_vien_id and record.hoc_phan_id:
                    map_string = f"{record.sinh_vien_id.id}|{record.hoc_phan_id.id}"
                    if map_string not in map_sv_hp:
                        map_sv_hp[map_string] = self.env["sv_hp_ds"].create({
                            "sinh_vien_id":
                            record.sinh_vien_id.id,
                            "hoc_phan_id":
                            record.hoc_phan_id.id,
                        })
                    record.sv_hp_ds_id = map_sv_hp[map_string]
                else:
                    record.sv_hp_ds_id = record.sv_hp_ds_id

    @api.depends("diem_tong_ket", "du_dau_diem")
    def _compute_sinh_vien_hoc_ky_id(self):
        # for record in self:
        #     print(record)
        #     sinh_vien_hoc_ky = self.env["qldt.sinh_vien_hoc_ky"].search(
        #         [
        #             ("sinh_vien_id", "=", record.sinh_vien_id.id),
        #             ("ky_nam_hoc_id", "=", record.ky_hoc_id.id),
        #         ]
        #     )
        #     if sinh_vien_hoc_ky:
        #         for vl in sinh_vien_hoc_ky:
        #             record.sinh_vien_hoc_ky_id = vl
        #     else:
        #         if record.sinh_vien_id:
        #             sinh_vien_hoc_ky = self.env["qldt.sinh_vien_hoc_ky"].create(
        #                 {
        #                     "sinh_vien_id": record.sinh_vien_id.id,
        #                     "ky_nam_hoc_id": record.ky_hoc_id.id,
        #                 }
        #             )
        #             record.sinh_vien_hoc_ky_id = sinh_vien_hoc_ky.id
        map_sv_hoc_ky = {}
        ky_hoc_ids = self.mapped("ky_hoc_id.id")
        sinh_vien_hoc_ky = self.env["qldt.sinh_vien_hoc_ky"].search([
            ("ky_nam_hoc_id", "in", ky_hoc_ids)
        ])
        for record in self:
            svhk = sinh_vien_hoc_ky.filtered(
                lambda x: x.sinh_vien_id == record.sinh_vien_id and x.
                ky_nam_hoc_id == record.ky_hoc_id)
            if len(svhk) > 0:
                record.sinh_vien_hoc_ky_id = svhk[0]
            else:
                if record.sinh_vien_id and record.ky_hoc_id:
                    map_string = f"{record.sinh_vien_id.id}|{record.ky_hoc_id.id}"
                    if (map_string not in map_sv_hoc_ky):
                        map_sv_hoc_ky[map_string] = self.env[
                            "qldt.sinh_vien_hoc_ky"].create({
                                "sinh_vien_id":
                                record.sinh_vien_id.id,
                                "ky_nam_hoc_id":
                                record.ky_hoc_id.id,
                            })
                    record.sinh_vien_hoc_ky_id = map_sv_hoc_ky[map_string]
                else:
                    record.sinh_vien_hoc_ky_id = record.sinh_vien_hoc_ky_id
