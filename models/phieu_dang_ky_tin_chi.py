import logging
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from .env_thanh_toan import base_url_hoc_phi
import re
import requests
import datetime
import random
import uuid

_logger = logging.getLogger(__name__)


class PhieuDangKyTinChi(models.Model):
    _name = "phieu_dang_ky_tin_chi"
    _description = "Phiếu đăng ký tín chỉ"
    _rec_name = "ten_phieu_dktc"

    ten_phieu_dktc = fields.Char("Mã phiếu",
                                 store=True,
                                 compute="_compute_ten_phieu_dktc")

    dot_dang_ky_nhu_cau_id = fields.Many2one(
        "dot_dang_ky_nhu_cau",
        string="Đợt đăng ký nhu cầu",
        related="dot_dang_ky_tin_chi_id.dot_dang_ky_hoc_phan_id",
        store=True)
    dot_dang_ky_tin_chi_id = fields.Many2one("dot_dang_ky_tin_chi",
                                             string="Đợt đăng ký tín chỉ")
    ap_dung_thanh_toan_truc_tuyen = fields.Boolean(
        related="dot_dang_ky_tin_chi_id.ap_dung_thanh_toan_truc_tuyen",
        store=True)
    sinh_vien_id = fields.Many2one("sinh_vien", string="Sinh viên")
    sv_hp_dktc_id = fields.One2many(
        "sv_hp_dktc",
        "phieu_dang_ky_tin_chi_id",
        string="Danh sách tín chỉ đăng ký",
    )
    tong_so_tin_chi = fields.Integer(
        "Tổng số tín chỉ",
        compute="_compute_tong_so_tin_chi",
        store=True,
        readonly=False,
    )
    tong_hoc_phi = fields.Integer(compute="_compute_tong_hoc_phi",
                                  store=True,
                                  string="Tổng học phí")
    so_tien_da_nhan = fields.Float(string="Số tiền nhà trường đã nhận")
    name = fields.Char("Họ và tên",
                       size=100,
                       related="sinh_vien_id.name",
                       store=True)
    ma_sinh_vien = fields.Char("Mã sinh viên",
                               size=20,
                               related="sinh_vien_id.ma_dinh_danh",
                               store=True)
    lop_hanh_chinh_id = fields.Many2one(
        comodel_name='lop_hanh_chinh',
        related='sinh_vien_id.lop_hanh_chinh_id',
        ondelete='set null',
        string="Mã lớp hành chính")
    ten_lop_hanh_chinh = fields.Char(
        related="lop_hanh_chinh_id.ten_lop_hanh_chinh",
        store=True,
        string="Tên lớp hành chính")
    so_dien_thoai = fields.Char("Số điện thoại", size=20)
    hinh_thuc_dao_tao_id = fields.Many2one(
        comodel_name="hinh_thuc_dao_tao",
        related="dot_dang_ky_tin_chi_id.hinh_thuc_dao_tao_id",
        store=True,
        string="Hình thức đào tạo")
    ma_thanh_toan = fields.Char(
        # compute="_compute_get_ma_thanh_toan",
        store=True,
        string="Mã thanh toán")
    hoc_phi_ap_dung = fields.Many2one(
        string="Học phí 1 tín chỉ áp dụng",
        size=100,
        related="sinh_vien_id.khoa_nganh_id.hoc_phi_ids",
        store=True)
    hoc_phi_mot_tin_chi = fields.Float(
        string="Giá tiền một tín chỉ",
        related="hoc_phi_ap_dung.gia_tin_chi_chung",
        store=True)
    khoan_thu_id = fields.Many2one(comodel_name="danh_muc.khoan_thu",
                                   related="hoc_phi_ap_dung.khoan_thu_id",
                                   ondelete="set null",
                                   string="Mã khoản thu (nếu có)")
    don_vi_thu_huong = fields.Many2one(
        comodel_name='danh_muc.don_vi_thu_huong',
        ondelete='set null',
        string="Đơn vị thụ hưởng"
    )
    ky_hoc_id = fields.Many2one(
        related="dot_dang_ky_tin_chi_id.ky_hoc_id", store=True
    )
    trang_thai_sinh_ma_thanh_toan = fields.Boolean(default=False, string="Trạng thái phê duyệt")
    trang_thai_thanh_toan = fields.Boolean(string="Trạng thái thanh toán",
                                          compute="_compute_trang_thai")
    ngay_nop_tien = fields.Datetime(string="Ngày nộp tiền")
    ma_hoa_ma_thanh_toan = fields.Text("Mã hóa mã thanh toán")
    # don_vi_thu_huong_stk = fields.Char(
    #     related="don_vi_thu_huong.so_tai_khoan",
    #     store=True,
    #     string="Số tài khoản"
    # )
    # don_vi_thu_huong_ten_ngan_hang = fields.Char(
    #     related="don_vi_thu_huong.ten_ngan_hang",
    #     store=True,
    #     string="Tên ngân hàng"
    # )
    # don_vi_thu_huong_chi_nhanh = fields.Char(
    #     related="don_vi_thu_huong.chi_nhanh",
    #     store=True,
    #     string="Chi nhánh"
    # )
    ghi_chu = fields.Char(related="don_vi_thu_huong.ghi_chu",
                          store=True,
                          string="Ghi chú")

    def phe_duyet(self):
        for record in self:
            if not record.trang_thai_sinh_ma_thanh_toan:
                record.trang_thai_sinh_ma_thanh_toan = True
                
    @api.depends("dot_dang_ky_tin_chi_id",
                 "ma_sinh_vien",
                 "name")
    def _compute_ten_phieu_dktc(self):
        for record in self:
            record.ten_phieu_dktc = str(
                record.dot_dang_ky_tin_chi_id.ten_dot_dang_ky_tin_chi
            ) + ' - ' + str(record.ma_sinh_vien) + ' - ' + str(record.name)

    # def _compute_khoan_thu(self):
    #     for record in self:
    #

    def huy_ma_thanh_toan(self, ma_thanh_toan):
        print("Vô hiệu nã thanh toán ", ma_thanh_toan)
        try:
            delete_ma_thanh_toan = requests.delete(
                f"{base_url_hoc_phi}/invoice/{str(ma_thanh_toan)}")
            print("trạng thái xóa mã thanh toán", delete_ma_thanh_toan)
            return True
        except Exception as e:
            _logger.error(e)
            return False

    @api.constrains("trang_thai_sinh_ma_thanh_toan", "tong_hoc_phi")
    def _compute_get_ma_thanh_toan(self):
        for record in self:
            if record.ap_dung_thanh_toan_truc_tuyen:
                if record.trang_thai_sinh_ma_thanh_toan:
                    _logger.info(
                        "Đoạn này cần gọi API hệ thống thanh toán để tạo invoice"
                    )
                    url_invoice = f"{base_url_hoc_phi}/invoice"
                    item_product_price = self.get_product_price(record)
                    customer_info = {
                        "name":
                        record.sinh_vien_id.name,
                        "customerId":
                        record.sinh_vien_id.ma_dinh_danh,
                        "address":
                        record.sinh_vien_id.lop_hanh_chinh_id.
                        ten_lop_hanh_chinh
                    }
                    # tự sinh mã thanh toán theo quy tắc
                    ma_thanh_toan = record.ma_thanh_toan
                    if not record.ma_thanh_toan:
                        ma_thanh_toan = self.get_ma_thanh_toan(do_dai=9,
                                                               prefix="30")
                    else:
                        print("Dã có mã thanh toán nên không gét thêm")
                    _logger.info("ma thanh toan = {}".format(ma_thanh_toan))
                    ma_invoice = str(record._origin.id)
                    json_invoice_data = {
                        "code": ma_invoice,
                        "customerId": record.sinh_vien_id.ma_dinh_danh,
                        "customerInfo": customer_info,
                        "items": [item_product_price],
                        "identityCode": ma_thanh_toan,
                        "metadata":
                        record.get_metadata_hinh_thuc_dao_tao(record),
                    }
                    try:
                        create_invoice = requests.post(url=url_invoice,
                                                       json=json_invoice_data)
                        _logger.info("trạng thái tạo invoice" + \
                                     create_invoice.json().get('data').get('_id') + " : " + \
                                     str(create_invoice.status_code))
                        if create_invoice.status_code == 201:
                            record.ma_thanh_toan = ma_thanh_toan
                            record.ma_hoa_ma_thanh_toan = json_invoice_data
                            # record.ma_khoan_thu = self.env['danh_muc.khoan_thu'].search([('ma_khoan_thu','=','01.02.03.05')]).id
                            _logger.info(
                                "sau khi gửi yêu cầu tạo invoice, mã thanh toán = {}"
                                .format(record.ma_thanh_toan))
                        else:
                            record.ma_thanh_toan = "Tạm thời chưa có mã thanh toán, vui lòng thử lại"
                    except Exception as e:
                        _logger.error(e)
                        record.ma_thanh_toan = "Tạm thời chưa lấy được mã thanh toán, vui lòng thử lại"
                else:
                    _logger.info("Trạng thái sinh mã thanh toán = {}".format(
                        record.trang_thai_sinh_ma_thanh_toan))
                    if record.ma_thanh_toan:
                        record.huy_ma_thanh_toan(record.ma_thanh_toan)
                    record.ma_thanh_toan = False
                    record.ma_hoa_ma_thanh_toan = ''

    def get_ma_thanh_toan(self, do_dai=9, prefix="20"):
        #do có thể mã thanh toán sinh bằng random bị trùng với mã đã tồn tại trên hệ thống nên cần while và check tại đây
        try:
            dem = 10
            while dem > 0:
                dem -= 1
                start_byte = random.randint(0, 24)
                stop_byte = start_byte + do_dai - len(prefix)
                ma_thanh_toan = str(uuid.uuid4().int)[start_byte:stop_byte]
                check_ma_thanh_toan = requests.get(
                    f"{base_url_hoc_phi}/invoice/identity-code/{str(prefix + ma_thanh_toan)}"
                )
                print("Get mã thanh toán")
                if check_ma_thanh_toan.status_code == 200:
                    check_ma_thanh_toan = check_ma_thanh_toan.json()['data']
                    if check_ma_thanh_toan == None:
                        return prefix + ma_thanh_toan
                    else:
                        print("Get lại mã thanh toán nào")
                else:
                    raise ValidationError(
                        f"Lỗi khi sinh mã thanh toán! Vui lòng liên hệ nhóm kỹ thuật để yêu cầu hỗ trợ!"
                    )
            raise ValidationError(
                f"Lỗi khi sinh mã thanh toán! Vui lòng liên hệ nhóm kỹ thuật để yêu cầu hỗ trợ!"
            )
        except Exception as e:
            _logger.error(e)
            raise ValidationError(
                f"Lỗi khi sinh mã thanh toán! Vui lòng liên hệ nhóm kỹ thuật để yêu cầu hỗ trợ!"
            )

    def get_product_price(self, record):
        '''
            TODO:
                - Link phần tạo danh mục học phí -> create product. sau đó return về product ID + name + ...
        '''
        if not base_url_hoc_phi:
            raise ValidationError(
                "Chưa cấu hình base_url_hoc_phi trong hệ thống! Hãy liên hệ với nhóm kỹ thuật!"
            )
        if not record.hoc_phi_ap_dung.ma_hoc_phi:
            raise ValidationError(
                f"Khóa ngành của sinh viên {record.ma_sinh_vien} chưa có mức học phí!"
            )
        item_product = requests.get(
            f"{base_url_hoc_phi}/product/code/{record.hoc_phi_ap_dung.ma_hoc_phi}"
        ).json()['data']
        active_price = {}
        for vl in item_product['prices']:
            if vl['active'] == True:
                active_price = vl
        return {
            "productId": item_product["_id"],
            "productName": item_product["name"],
            "productCode": item_product["code"],
            "priceId": active_price["_id"],
            "unitAmount": active_price["unitAmount"],
            "unitLabel": "VND",
            "quantity": record.tong_so_tin_chi
        }

    def get_metadata_hinh_thuc_dao_tao(self, record):
        if record.lop_hanh_chinh_id.hinh_thuc_dao_tao_id.ten_hinh_thuc_dao_tao:
            return {
                "hinhThucDaoTaoId":
                record.lop_hanh_chinh_id.hinh_thuc_dao_tao_id.id,
                "loai": f'Học phí học kỳ {record.ky_hoc_id.ma_ky_nam_hoc}',
                "phamVi": 'Hình thức đào tạo',
            }
        else:
            return {
                "hinh_thuc_dao_tao": "Chưa xác định"
            }  # đoạn này cần tổng quát hóa thành constants/enums

    # @api.constrains("so_dien_thoai")
    # def validate_phone(self):
    #     if self.so_dien_thoai:
    #         match = re.match("^[0-9]\d{9,10}$", self.so_dien_thoai)
    #         if not match:
    #             raise ValidationError("Số điện thoại không đúng!")

    @api.constrains("sinh_vien_id")
    def unique_phieu_dang_ky_tin_chi(self):
        for record in self:
            phieu_dktc = self.env["phieu_dang_ky_tin_chi"].search([
                ("sinh_vien_id", "=", record.sinh_vien_id.id),
                ("dot_dang_ky_tin_chi_id", "=",
                 record.dot_dang_ky_tin_chi_id.id)
            ])
            if len(phieu_dktc) > 1:
                raise ValidationError(
                    f"Sinh viên {record.sinh_vien_id.ma_dinh_danh} đã có phiếu dktc cho đợt {record.dot_dang_ky_tin_chi_id.ten_dot_dang_ky_tin_chi} trên hệ thống!"
                )

    @api.depends("sv_hp_dktc_id")
    def _compute_tong_so_tin_chi(self):
        for record in self:
            tong_so_tin_chi = 0
            if record.sv_hp_dktc_id:
                for sv_hp_dktc in record.sv_hp_dktc_id:
                    tong_so_tin_chi += sv_hp_dktc.so_tin_chi
            record.tong_so_tin_chi = tong_so_tin_chi

    @api.depends(
        "sv_hp_dktc_id.hoc_phi",
        "tong_so_tin_chi",
    )
    def _compute_tong_hoc_phi(self):
        for record in self:
            try:
                if record.hoc_phi_ap_dung and record.tong_so_tin_chi:
                    record.tong_hoc_phi = float(
                        record.hoc_phi_ap_dung.gia_tin_chi_chung) * float(
                            record.tong_so_tin_chi)
            except Exception as e:
                _logger.error(e)

    @api.model
    def create(self, values):
        '''
        Hàm này có chức năng
        1. kiểm tra xem sinh viên đã có bản ghi công nợ chưa? nếu chưa thì tạo mới
        2. Tao mới phiếu đăng ký tín chỉ
        '''
        cong_no_id = self.check_ban_ghi_cong_no(values['sinh_vien_id'])
        print("Tạo mới công nợ", cong_no_id)
        phieu_dang_ky_tin_chi = super(PhieuDangKyTinChi, self).create(values)
        _logger.info("creating phiếu đăng ký học phần {}".format(values))
        self.tao_hoac_cap_nhat_hoa_don(phieu_dang_ky_tin_chi, cong_no_id)
        return phieu_dang_ky_tin_chi

    def write(self, values):
        for record in self:
            if record.trang_thai_thanh_toan and ('trang_thai_thanh_toan'
                                                 not in values):
                raise ValidationError(
                    f"Không thể chỉnh sửa phiếu đăng ký tín chỉ {record.ten_phieu_dktc} do sinh viên đã hoàn thành đóng học phí!"
                )
            else:
                cong_no_id = record.check_ban_ghi_cong_no(
                    record.sinh_vien_id.id)
                phieu_dang_ky = super(PhieuDangKyTinChi, record).write(values)
                record.tao_hoac_cap_nhat_hoa_don(record, cong_no_id)
                return phieu_dang_ky

    def check_ban_ghi_cong_no(self, sinh_vien_id):
        cong_no_ids = self.env["qldt.cong_no"].search(
            [("sinh_vien_id", "=", sinh_vien_id)], limit=1)
        if len(cong_no_ids) == 0:
            cong_no_id = self.env['qldt.cong_no'].create({
                'sinh_vien_id':
                sinh_vien_id,
            })
            return cong_no_id.id
        else:
            for vl in cong_no_ids:
                return vl.id

    def tao_hoac_cap_nhat_hoa_don(self, phieu_dang_ky_tin_chi, cong_no_id):
        if phieu_dang_ky_tin_chi.trang_thai_sinh_ma_thanh_toan:
            print("Tạo hoặc cập nhật hóa đơn")
            ma_hoa_don = "HDHPHK" + phieu_dang_ky_tin_chi.ky_hoc_id.ma_ky_nam_hoc + phieu_dang_ky_tin_chi.ma_sinh_vien
            hoa_don_ids = self.env["qldt.hoa_don"].search(
                [("ma_hoa_don", "=", ma_hoa_don)], limit=1)
            mo_ta_dich_vu = f"Hóa đơn học phí kỳ {phieu_dang_ky_tin_chi.ky_hoc_id.ma_ky_nam_hoc} của sinh viên {phieu_dang_ky_tin_chi.ma_sinh_vien}\n"
            for vl in phieu_dang_ky_tin_chi.sv_hp_dktc_id:
                mo_ta_dich_vu += f"Học phần:{vl.ten_hoc_phan}, số tín chỉ:{vl.so_tin_chi}, giá tiền:{vl.so_tin_chi * phieu_dang_ky_tin_chi.hoc_phi_mot_tin_chi}\n"
            if len(hoa_don_ids) == 0:
                _logger.info("Tạo hóa đơn nào")
                hoa_don_id = self.env['qldt.hoa_don'].create({
                    'ma_hoa_don':
                    ma_hoa_don,
                    'cong_no_id':
                    cong_no_id,
                    'ap_dung_thanh_toan_truc_tuyen':
                    phieu_dang_ky_tin_chi.ap_dung_thanh_toan_truc_tuyen,
                    'ma_thanh_toan':
                    phieu_dang_ky_tin_chi.ma_thanh_toan,
                    'so_tien_da_nhan':
                    phieu_dang_ky_tin_chi.so_tien_da_nhan,
                    'gia_tien_mot_dich_vu':
                    phieu_dang_ky_tin_chi.hoc_phi_mot_tin_chi,
                    'so_luong_don_vi_dich_vu':
                    phieu_dang_ky_tin_chi.tong_so_tin_chi,
                    'ky_nam_hoc_id':
                    phieu_dang_ky_tin_chi.ky_hoc_id.id,
                    'mo_ta_dich_vu':
                    mo_ta_dich_vu,
                    'ten_hoa_don':
                    ma_hoa_don,
                    'khoan_thu_id':
                    phieu_dang_ky_tin_chi.khoan_thu_id.id,
                    'ngay_nop_tien':
                    phieu_dang_ky_tin_chi.ngay_nop_tien,
                })
            elif len(hoa_don_ids) > 0:
                for vl in hoa_don_ids:
                    vl.ma_hoa_don = ma_hoa_don
                    vl.cong_no_id = cong_no_id
                    vl.ap_dung_thanh_toan_truc_tuyen = phieu_dang_ky_tin_chi.ap_dung_thanh_toan_truc_tuyen
                    vl.ma_thanh_toan = phieu_dang_ky_tin_chi.ma_thanh_toan
                    vl.so_tien_da_nhan = phieu_dang_ky_tin_chi.so_tien_da_nhan
                    vl.gia_tien_mot_dich_vu = phieu_dang_ky_tin_chi.hoc_phi_mot_tin_chi
                    vl.so_luong_don_vi_dich_vu = phieu_dang_ky_tin_chi.tong_so_tin_chi
                    vl.ky_nam_hoc_id = phieu_dang_ky_tin_chi.ky_hoc_id.id
                    vl.mo_ta_dich_vu = mo_ta_dich_vu
                    vl.ten_hoa_don = ma_hoa_don
                    vl.khoan_thu_id = phieu_dang_ky_tin_chi.khoan_thu_id.id
                    vl.ngay_nop_tien = phieu_dang_ky_tin_chi.ngay_nop_tien
                    cong_no_ids = self.env["qldt.cong_no"].search(
                        [("id", "=", cong_no_id)], limit=1)
                    cong_no_ids._compute_tinh_cong_no()

    @api.constrains("trang_thai_sinh_ma_thanh_toan", "so_tien_da_nhan", "tong_so_tien")
    def _compute_trang_thai(self):
        for record in self:
            record.trang_thai_thanh_toan = False
            if record.so_tien_da_nhan and record.tong_hoc_phi:
                if record.so_tien_da_nhan >= record.tong_hoc_phi:
                    record.trang_thai_thanh_toan = True

