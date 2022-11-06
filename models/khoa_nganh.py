from odoo import fields, models, api
from odoo.exceptions import ValidationError


class KhoaNganh(models.Model):
    _name = "khoa_nganh"
    _description = "Khóa-ngành"
    _rec_name = "ten_khoa_nganh"

    # Tên khóa - ngành = Tên khóa + Tên ngành viết tắt + mã ngành (theo thông tư XX của bộ)
    # VD: D20-CNTT-78623232: khóa D20 ngành công nghệ thông tin - mã ngành ...
    ten_khoa_nganh = fields.Char("Tên khóa ngành",
                                 size=200,
                                 compute="_compute_ten_khoa_nganh",
                                 store=True)
    hinh_thuc_dao_tao_id = fields.Many2one(comodel_name="hinh_thuc_dao_tao",
                                           string="Hình thức đào tạo")
    khoa_sinh_vien_id = fields.Many2one(comodel_name="khoa_sinh_vien",
                                        ondelete="cascade",
                                        string="Khóa sinh viên")
    nganh_id = fields.Many2one("quan_ly_nganh_hoc.nganh", string="Ngành học")
    ten_nganh = fields.Many2one(
        related="nganh_id.name",
        store=True,
        string="Tên ngành"
    )
    ctk_id = fields.Many2one(
        comodel_name="chuong_trinh_khung",
        # column2='khoa_nganh_id',
        string="Chương trình khung đang sử dụng",
    )
    hinh_thuc_dao_tao_id = fields.Many2one(
        comodel_name='hinh_thuc_dao_tao',
        compute='_compute_hinh_thuc_dao_tao',
        store=True,
        ondelete='set null',
        string='Hình thức đào tạo')
    bieu_gia_id = fields.Many2one(
        "danh_muc.bieu_gia",
        "Giá tiền 1 tín chỉ",
    )
    hoc_phi_ids = fields.Many2one(
        comodel_name="hoc_phi",
        string="Danh sách mức học phí",
    )
    gia_tien = fields.Integer(
        "Giá tiền",
        related="bieu_gia_id.gia_tien",
        store=True,
    )

    @api.depends("khoa_sinh_vien_id.hinh_thuc_dao_tao_id")
    def _compute_hinh_thuc_dao_tao(self):
        """
            đoạn này cần chốt lại với BA xem hình thức đào tạo của khóa ngành được kế thừa từ khóa sinh viên hay cho
            chọn bằng tay
        """
        for record in self:
            if record.khoa_sinh_vien_id.hinh_thuc_dao_tao_id.ten_hinh_thuc_dao_tao_viet_tat:
                record.hinh_thuc_dao_tao_id = record.khoa_sinh_vien_id.hinh_thuc_dao_tao_id
            else:
                record.hinh_thuc_dao_tao_id = False

    @api.depends("khoa_sinh_vien_id.ten_hien_thi", "nganh_id.ma_nganh")
    def _compute_ten_khoa_nganh(self):
        for record in self:
            if record.khoa_sinh_vien_id.ten_hien_thi and record.nganh_id.ma_nganh:
                # ten_nganh_viet_tat = self._compute_ten_viet_tat_nganh(
                #     record.nganh_id.ten_nganh
                # )
                record.ten_khoa_nganh = (
                    # record.khoa_sinh_vien_id.ten_hien_thi + "-" + ten_nganh_viet_tat
                    record.khoa_sinh_vien_id.ten_hien_thi +\
                    "-" + record.nganh_id.ten_nganh_viet_tat
                )
                # + record.nganh_id.ma_nganh.ma_nganh_hoc
                # sau khi thêm phần quản lý danh mục ngành học thì cần thay đổi tham chiếu này để lấy được đúng tên ngành trong danh mục
            else:
                record.ten_khoa_nganh = record.ten_khoa_nganh

    def _compute_ten_viet_tat_nganh(self, ten_nganh_day_du):
        """
        lấy tên viết tắt của 1 ngành,
            ví dụ: Công nghệ thông tin -> CNTT
                    Fintech -> Fintech
        """
        ten_nganh_day_du = ten_nganh_day_du.replace("-", "").strip()
        if " " in ten_nganh_day_du:
            ten_nganh_splitted = ten_nganh_day_du.split(" ")
            ten_nganh_viet_tat = []
            for each_element in ten_nganh_splitted:
                if each_element != "" and each_element != " ":
                    ten_nganh_viet_tat.append(each_element[0].upper())
            return "".join(ten_nganh_viet_tat)
        else:
            return ten_nganh_day_du

    @api.constrains("ctk_id")
    def _constraint_ctk(self):
        for record in self:
            if record.ctk_id and record.ctk_id.nganh_id != record.nganh_id:
                raise ValidationError(
                    "Chương trình khung không khớp với ngành")


class KhoaChuyenNganh(models.Model):
    _name = "khoa_chuyen_nganh"
    _description = "Khóa-chuyên ngành"
    _rec_name = "ten_khoa_chuyen_nganh"

    chuyen_nganh_id = fields.Many2one("quan_ly_nganh_hoc.chuyen_nganh",
                                      "Chuyên ngành")
    khoi_lop_id = fields.Many2one("khoi_lop", "Khối lớp",
                                  domain="[('khoa_nganh_id.nganh_id.chuyen_nganh_ids', 'in', chuyen_nganh_id)]")
    khoa_nganh_id = fields.Many2one("khoa_nganh",
                                    string="Khóa ngành",
                                    related="khoi_lop_id.khoa_nganh_id")
    ctk_id = fields.Many2one("chuong_trinh_khung",
                             string="Chương trình khung chuyên ngành",
                             domain="[('chuyen_nganh_id', '=', chuyen_nganh_id)]")
    ten_khoa_chuyen_nganh = fields.Char(
        string="Tên khóa chuyên ngành",
        compute="_compute_ten_khoa_chuyen_nganh",
        store=True,
    )

    @api.depends("khoi_lop_id", "chuyen_nganh_id")
    def _compute_ten_khoa_chuyen_nganh(self):
        for record in self:
            if record.khoi_lop_id and record.chuyen_nganh_id:
                record.ten_khoa_chuyen_nganh = f"{record.khoi_lop_id.khoa_nganh_id.ten_khoa_nganh}-{record.chuyen_nganh_id.name}"
            else:
                record.ten_khoa_chuyen_nganh = False

    # @api.constrains("chuyen_nganh_id","khoi_lop_id")
    # def _constraint_chuyen_nganh_id(self):
    #     for record in self:
    #         if record.chuyen_nganh_id not in record.khoi_lop_id.khoa_nganh_id.nganh_id.chuyen_nganh_ids:
    #             raise ValidationError("Chuyên ngành không thuộc ngành!")

    # @api.constrains("chuyen_nganh_id","ctk_id")
    # def _constraint_ctk(self):
    #     for record in self:
    #         if record.ctk_id.chuyen_nganh_id != record.chuyen_nganh_id:
    #             raise ValidationError(
    #                 "Chương trình khung không khớp với chuyên ngành!")
