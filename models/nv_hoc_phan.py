from odoo import fields, models, api


class NguyenVongHocPhan(models.Model):
    _name = "nv_hoc_phan"
    _description = "Danh sách nguyện vọng học phần"

    hoc_phan_id = fields.Many2one("slide.channel",
                                  string="Học phần",
                                  required=True)
    so_tin_chi = fields.Integer(
        "Số tín chỉ",
        related="hoc_phan_id.so_tin_chi",
        store=True,
        group_operator=False,
    )
    muc_hoc_phi_phai_dong = fields.Many2one(
        comodel_name="danh_muc.bieu_gia",
        string="Mức phí phải đóng",
        related="sinh_vien_id.khoa_nganh_id.bieu_gia_id")
    hoc_phi = fields.Integer(compute="_compute_hoc_phi",
                             store=True,
                             string="Học phí")
    ten_hoc_phan = fields.Char("Tên học phần",
                               related="hoc_phan_id.ten_hoc_phan",
                               store=True)
    ghi_chu = fields.Text("Ghi chú")
    phieu_dang_ky_hoc_phan_id = fields.Many2one(
        comodel_name="phieu_dang_ky_hoc_phan",
        ondelete="cascade",
        string="Phiếu đăng ký học phần")
    dot_dk_nhu_cau_id = fields.Many2one(
        "dot_dang_ky_nhu_cau",
        related="phieu_dang_ky_hoc_phan_id.dot_dang_ky_id",
        store=True,
    )
    ky_hoc_id = fields.Many2one(
        "ky_nam_hoc",
        related="phieu_dang_ky_hoc_phan_id.ky_hoc_id",
        store=True,
        string="Kỳ năm học",
    )
    sinh_vien_id = fields.Many2one(
        "sinh_vien",
        related="phieu_dang_ky_hoc_phan_id.sinh_vien_id",
        store=True,
        string="Sinh viên",
    )
    trang_thai = fields.Selection([
        ("0", "Không chọn"),
        ("1", "Chọn"),
    ])
    # ma_khoan_thu = fields.Many2one(
    #     comodel_name="danh_muc.khoan_thu",
    #     related="hoc_phi.khoan_thu_id",
    #     store=True,
    #     string="Mã khoản thu"
    # )

    @api.depends("ky_hoc_id", "so_tin_chi")
    def _compute_hoc_phi(self):
        for record in self:
            thong_tin_hoc_phi = self.env["hoc_phi"].search(
                [("khoa_nganh_ids", "in", record.sinh_vien_id.khoa_nganh_id.id)
                 ],
                limit=1,
                order="nam_hoc desc")
            if thong_tin_hoc_phi.phuong_thuc_thu_phi == "0":
                record.hoc_phi = thong_tin_hoc_phi.gia_tin_chi_chung * record.so_tin_chi
            elif thong_tin_hoc_phi.phuong_thuc_thu_phi == "1":
                mon_hoc_dieu_kien = self.env["mon_hoc_dieu_kien"].search(
                    [("ctk_id", "in", [
                        record.sinh_vien_id.ctk_nganh_id.id,
                        record.sinh_vien_id.ctk_chuyen_nganh_id.id
                    ]), (
                        "hoc_phan_id",
                        "=",
                        record.hoc_phan_id.id,
                    )],
                    limit=1,
                )
                hoc_ky_ctk = self.env["hoc_ky_chuong_trinh_khung"].search([
                    ("ctk_id", "in", [
                        record.sinh_vien_id.ctk_nganh_id.id,
                        record.sinh_vien_id.ctk_chuyen_nganh_id.id
                    ]),
                ])
                map_hoc_ky = dict(
                    zip(hoc_ky_ctk.mapped("hoc_ky"),
                        hoc_ky_ctk.mapped("loai_ky")))
                if mon_hoc_dieu_kien.hoc_ky in map_hoc_ky:
                    if map_hoc_ky[mon_hoc_dieu_kien.hoc_ky] == "0":
                        record.hoc_phi = thong_tin_hoc_phi.gia_tin_chi_ky_thuong_xuyen * record.so_tin_chi
                    else:
                        record.hoc_phi = thong_tin_hoc_phi.gia_tin_chi_ky_tot_nghiep * record.so_tin_chi
                else:
                    record.hoc_phi = record.hoc_phi
            else:
                record.hoc_phi = record.hoc_phi
