from email.policy import default
from re import M
import uuid
import logging

from odoo import models, fields, api, tools, _

_logger = logging.getLogger(__name__)


class LopHanhChinh(models.Model):
    _name = "lop_hanh_chinh"
    _description = "lop_hanh_chinh"
    _rec_name = "ten_lop_hanh_chinh"

    ten_lop_hanh_chinh = fields.Char(compute="_compute_ten_lop_hanh_chinh",
                                     store=True,
                                     string="Tên lớp hành chính",
                                     readonly=False)
    
    trang_thai_ten = fields.Char(compute="_compute_ten_lop_hanh_chinh",
                                     store=True,
                                     string="Trạng thái tên lớp hành chính")

    khoi_lop_id = fields.Many2one(comodel_name="khoi_lop",
                                  ondelete="cascade",
                                  string="Khối lớp")
    khoa_nganh_id = fields.Many2one(
        comodel_name="khoa_nganh",
        related="khoi_lop_id.khoa_nganh_id",
        string="Khóa ngành",
    )
    khoa_sinh_vien = fields.Many2one(
        comodel_name="khoa_sinh_vien",
        string="Khóa sinh viên",
    )
    nganh = fields.Many2one(
        comodel_name="quan_ly_nganh_hoc.nganh",
        string="Ngành",
    )
    khoa_chuyen_nganh_id = fields.Many2one("khoa_chuyen_nganh",
                                           string="Khóa-chuyên ngành")
    chuyen_nganh = fields.Many2one("quan_ly_nganh_hoc.chuyen_nganh",
                                   string="Chuyên ngành")
    can_bo_id = fields.Many2one(comodel_name="nhan_vien",
                                ondelete="set null",
                                string="Cán bộ phụ trách")
    ten_can_bo = fields.Char(related="can_bo_id.name",
                             store=True,
                             string="Tên cán bộ phụ trách")
    
    si_so = fields.Integer("Sĩ số", compute="_compute_si_so", store=True)
    don_vi_id = fields.Many2one(comodel_name="danh_muc.don_vi",
                                string="Đơn vị")
    sinh_vien_ids = fields.Many2many(
        comodel_name="sinh_vien",
        string="Danh sách sinh viên",
    )
    hinh_thuc_dao_tao_id = fields.Many2one(
        comodel_name='hinh_thuc_dao_tao',
        related='khoa_sinh_vien.hinh_thuc_dao_tao_id',
        store=True,
        # inverse='_inverse_hinh_thuc_dao_tao',
        ondelete='set null',
        string='Hình thức đào tạo')

    co_so_dao_tao_moi = fields.Many2one(
        comodel_name="danh_muc.co_so_dao_tao",
        ondelete="set null",
        string="Cơ sở đào tạo",
    )
    so_thu_tu_lop = fields.Integer(string="Số thứ tự lớp",
                                    default=None)
    # co_so_dao_tao = fields.Selection([
    #         ('1','Cơ sở phía Bắc'),
    #         ('2', 'Cơ sở phía Nam'),
    #         ('3', 'Trạm đào tạo Hải Dương')
    #     ],
    #     string="Cơ sở đào tạo"
    # )
    chuong_trinh_khung_nganh_id = fields.Many2one(
        comodel_name="chuong_trinh_khung",
        compute="_compute_chuong_trinh_khung_nganh",
        store=True,
        string="Chương trình khung ngành",
    )
    chuong_trinh_khung_chuyen_nganh_id = fields.Many2one(
        comodel_name="chuong_trinh_khung",
        compute="_compute_chuong_trinh_khung_chuyen_nganh",
        store=True,
        string="Chương trình khung chuyên ngành",
    )

    _sql_constraints = [('unique_lop_hanh_chinh', 'unique(ten_lop_hanh_chinh)',
                         "Lớp hành chính đã tồn tại")]

    color = fields.Integer()

    @api.depends("khoa_sinh_vien", "nganh")
    def _compute_chuong_trinh_khung_nganh(self):
        ctk_list = self.env["chuong_trinh_khung"].search([])
        for record in self:
            record.chuong_trinh_khung_nganh_id = ctk_list.filtered(
                lambda x: record.khoa_sinh_vien in x.khoa_sinh_vien_ids and x.
                chuyen_nganh_id.id == False and record.nganh == x.nganh_id and
                record.hinh_thuc_dao_tao_id == x.hinh_thuc_dao_tao_id)

    @api.depends("khoa_sinh_vien", "nganh", "chuyen_nganh")
    def _compute_chuong_trinh_khung_chuyen_nganh(self):
        ctk_list = self.env["chuong_trinh_khung"].search([])
        for record in self:
            record.chuong_trinh_khung_chuyen_nganh_id = ctk_list.filtered(
                lambda x: record.khoa_sinh_vien in x.khoa_sinh_vien_ids and x.
                chuyen_nganh_id.id != False and record.chuyen_nganh == x.
                chuyen_nganh_id and record.nganh == x.nganh_id and record.
                hinh_thuc_dao_tao_id in x.hinh_thuc_dao_tao_id)

    #
    # @api.constrains('si_so')
    # def _kiem_tra_si_so(self):
    #     for record in self:
    #         if record.si_so == 0:
    #             raise models.ValidationError('Sĩ số phải lớn hơn 0')

    def trang_thai_ten(self):
        for record in self:
            rs = self.venv['lop_hanh_chinh'].sudo().search([
                ('ten_lop_hanh_chinh', '=', record.ten_lop_hanh_chinh)
            ])
            # if rs:
            #     return False
        return False
    
        
    def _inverse_hinh_thuc_dao_tao(self):
        pass

    @api.onchange("nganh")
    def _onchange_filter_chuyen_nganh(self):
        res = {}
        res["domain"] = {"chuyen_nganh": [("nganh_id", "=", self.nganh.id)]}
        return res

    @api.depends(
        "co_so_dao_tao_moi",
        "khoi_lop_id",
        "khoa_sinh_vien",
        "nganh",
        "hinh_thuc_dao_tao_id",
        "so_thu_tu_lop",
        "nganh.ten_nganh_viet_tat",
    )
    def _compute_ten_lop_hanh_chinh(self):
        """
            tên lớp hành chính = khóa sinh viên + hình thức đào tạo + tên ngành viết tắt (2 chữ cái) + thứ tự đợt nhập học + cơ sở đào tạo
            tên ngành viết tắt đã được quy định trong văn bản của PTIT
        """
        for record in self:
            ten_lop_hanh_chinh = []
            # khóa sinh viên
            if record.khoa_sinh_vien.ten_hien_thi:
                ten_lop_hanh_chinh.append(record.khoa_sinh_vien.ten_hien_thi)
            # hình thức đào tạo
            # if (record.hinh_thuc_dao_tao_id.ten_hinh_thuc_dao_tao_viet_tat
            #     ):  # đoạn này cần thay đổi =
            #     # ten_lop_hanh_chinh.append('TX')
            #     ten_lop_hanh_chinh.append(
            #         record.hinh_thuc_dao_tao_id.ten_hinh_thuc_dao_tao_viet_tat)
            # tên ngành viết tắt
            if record.khoi_lop_id.khoa_nganh_id.nganh_id.ten_nganh_viet_tat:
                ten_lop_hanh_chinh.append(record.khoi_lop_id.khoa_nganh_id.
                                          nganh_id.ten_nganh_viet_tat)
            # thứ tự đợt nhập học
            # if record.khoi_lop_id.dot_nhap_hoc_id.thu_tu_dot:
            #     ten_lop_hanh_chinh.append(
            #         str(record.khoi_lop_id.dot_nhap_hoc_id.thu_tu_dot))
            # số thứ tự lớp

            # if record.so_thu_tu_lop != record.khoi_lop_id.dot_nhap_hoc_id.thu_tu_dot:
            if record.so_thu_tu_lop > 0:
                try:
                    ten_lop_hanh_chinh.append(
                        str(record.so_thu_tu_lop).zfill(2))
                except IndexError:
                    pass

            # cơ sở đào tạo
            if record.co_so_dao_tao_moi.ky_hieu_co_so_dao_tao:
                ten_lop_hanh_chinh.append(
                    "-" + record.co_so_dao_tao_moi.ky_hieu_co_so_dao_tao)
            temp = "".join(ten_lop_hanh_chinh)
            _logger.info(ten_lop_hanh_chinh)
            record.ten_lop_hanh_chinh = temp

    @api.depends("sinh_vien_ids")
    def _compute_si_so(self):
        for record in self:
            if record.sinh_vien_ids:
                sv = self.env["sinh_vien"].search([("lop_hanh_chinh_id", "=",
                                                    record.id)])
                record.si_so = len(sv)
            else:
                record.si_so = 0
