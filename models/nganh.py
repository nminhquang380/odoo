# -*- coding: utf-8 -*-

import uuid
import logging

from odoo import models, fields, api, tools, _

_logger = logging.getLogger(__name__)


class Nganh(models.Model):
    """
        - Lưu thông tin ngành học

    """

    _name = "quan_ly_nganh_hoc.nganh"
    _description = "quan_ly_nganh_hoc.nganh"
    _inherit = ["image.mixin"]
    _rec_name = 'ten_nganh_viet_tat'

    def _default_access_token(self):
        return str(uuid.uuid4())

    def _get_default_enroll_msg(self):
        return _("Liên hệ với người có thẩm quyền")

    # thông tin cơ bản
    banner = fields.Binary(
        string="Banner của ngành"
    )
    image_1024 = fields.Image(
        string="Image 1024",
        related="banner",
        max_width=1024,
        max_height=1024,
        store=True
    )
    image_512 = fields.Image(
        "Image 512",
        related="banner",
        max_width=512,
        max_height=512,
        store=True
    )
    image_256 = fields.Image(
        "Image 256",
        related="banner",
        max_width=256,
        max_height=256,
        store=True
    )
    image_128 = fields.Image(
        string="Image 128",
        related="banner",
        max_width=128,
        max_height=128,
        store=True
    )
    second_id = fields.NewId()
    ten_nganh = fields.Char(
        related="name.ten_nganh_hoc",
        store=True,
        string="Tên ngành"
    )
    ten_nganh_viet_tat = fields.Char(
        required=True,
        string="Tên ngành viết tắt")
    ma_nganh = fields.Char(
        related="name.ma_nganh_hoc",
        store=True,
        string="Mã ngành"
    )  # đổi cách nhập tên mã ngành: lấy trong danh mục tạo sẵn thay vì nhập tay
    name = fields.Many2one(
        comodel_name="danh_muc.nganh_hoc",
        ondelete="cascade",
        string="Tên ngành"
    )
    active = fields.Boolean(
        string="Trạng thái",
        default=True)
    thoi_gian_dao_tao = fields.Float(
        string="Thời gian đào tạo (năm)"
    )
    mo_ta = fields.Text(
        string="Mô tả ngành",
        help="Mô tả về ngành")
    mo_ta_ngan = fields.Text(
        string="Mô tả ngắn về ngành",
        help="Mô tả ngắn về ngành"
    )
    mo_ta_html = fields.Html(
        string="Giới thiệu về ngành",
        translate=tools.html_translate,
        sanitize_attributes=False,
        sanitize_form=False,
    )
    chuan_dau_ra = fields.Html(
        string="Thông tin về chuẩn đầu ra"
    )
    hoc_phi = fields.Html(
        string="Thông tin về học phí"
    )
    thong_tin_tuyen_sinh = fields.Html(
        string="Thông tin tuyển sinh"
    )

    # Các trường này liên quan đến quán lý chuyên ngành + môn học
    # Một ngành có thể gồm nhiều chuyên ngành
    chuyen_nganh_ids = fields.One2many(
        comodel_name="quan_ly_nganh_hoc.chuyen_nganh",
        inverse_name="nganh_id",
        string="Chuyên ngành",
    )
    so_luong_chuyen_nganh = fields.Integer(
        string="Số lượng chuyên ngành",
        compute="_compute_so_luong_chuyen_nganh",
        store=True
    )

    # security
    access_token = fields.Char(
        "Security Token",
        copy=False,
        default=_default_access_token
    )

    # Thông tin giống trên cổng thông tin
    # dưới đây là các trường được tạo tương ứng với các thông tin của 1 ngành học trên cổng thông tin daotao PTIT
    hinh_thuc_dao_tao = fields.Many2many(
        comodel_name="hinh_thuc_dao_tao",
        string="Hình thức đào tạo"
    )
    thoi_gian_hoc = fields.Float(
        string="Thời gian học - tính bằng năm"
    )
    ky_nhap_hoc = fields.Char(
        string="Kỳ nhập học"
    )  # có thể tạo 1 bảng riêng - kỳ học
    han_nop_ho_so = fields.Datetime(
        string="Hạn nộp hồ sơ"
    )
    # các trường dưới đây đang được xem xét để xem có tạo bảng/model mới không
    co_so_dao_tao = fields.Char("Cơ sở đào tạo")
    chi_tieu_tuyen_sinh = fields.Integer("Chỉ tiêu tuyển sinh")
    diem_trung_tuyen_cu = fields.Float(compute="_compute_diem_trung_truyen_cu")
    diem_trung_tuyen_moi = fields.Float(
        compute="_compute_diem_trung_tuyen_moi")

    nghe_nghiep = fields.Html(
        "Thông tin về cơ hội việc làm - cơ hội nghề nghiệp")

    quy_trinh_nhap_hoc = fields.Html("Quy trình nhập học")

    allow_comment = fields.Boolean()

    # các trường dưới đây không liên quan đến thông tin ngành học, chỉ hiển thị trên giao diện
    sequence = fields.Integer(default=10, help="Thứ tự hiển thị")
    color = fields.Integer("Chọn màu", default=0, help="")
    description = fields.Text()

    # quan hệ với bảng môn học điều kiện
    mon_hoc_dieu_kien_id = fields.Many2many(comodel_name="mon_hoc_dieu_kien")

    # COMPUTE Function
    # các hàm này dùng để tính toán giá trị các trường của model 1 cách tự động
    # các hàm _compute chưa có api.depends() tạm thời chưa dùng

    def _compute_sinhvien_nganh(self):
        self.sinh_vien_count = 1

    def _compute_sinhvien_nganh_totnghiep(self):
        self.sinh_vien_tot_nghiep_count = 1

    def _compute_diem_trung_truyen_cu(self):
        self.diem_trung_tuyen_cu = 22

    def _compute_diem_trung_tuyen_moi(self):
        self.diem_trung_tuyen_moi = 23

    @api.depends("chuyen_nganh_ids")
    def _compute_so_luong_chuyen_nganh(self):
        _logger.info("....... self.id = %r" % (self))
        for record in self:
            chuyen_nganh_count = (
                self.env["quan_ly_nganh_hoc.chuyen_nganh"]
                    .sudo()
                    .search_count([("nganh_id", "=", record.id), ])
            )
            _logger.info("...... số lượng chuyên ngành %r" %
                         (chuyen_nganh_count))
            record.so_luong_chuyen_nganh = chuyen_nganh_count

    # list of compute functions  END ##

    # ONCHANGE functions
    # không nên thực hiện thao tác Create/update các bản ghi trong db khi gọi hàm onchange

    @api.depends("value")
    def _value_pc(self):
        for record in self:
            record.value2 = float(record.value) / 100

    # ACTIONS
    # một số hàm mặc định tương tư bên slide_channel,
    # nếu xóa thì cần xóa phần tương ứng trong nganh_hoc.xml
    def action_view_sinh_vien(self):
        return 1

    def action_redirect_to_done_members(self):
        pass

    def action_redirect_to_members(self):
        pass

    def action_view_ratings(self):
        pass

    # @api.model
    # def create(self,vals):
    #     thong_tin_nganh_hoc_da_ton_tai = self.env['quan_ly_nganh_hoc.nganh'].search([
    #         ('ten_nganh', '=', vals['name']),
    #         ('ten_nganh_viet_tat', '=', vals['ten_nganh_viet_tat'])
    #     ])
    #     if thong_tin_nganh_hoc_da_ton_tai:
    #         _logger.info("thông tin ngành học đã tồn tại")
    #         res = thong_tin_nganh_hoc_da_ton_tai.write(vals)
    #         return res
    #     else:
    #         res = super(Nganh,self).create(vals)
    #         return res
