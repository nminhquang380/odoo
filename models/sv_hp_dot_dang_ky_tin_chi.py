from odoo import fields, models, api
from odoo.exceptions import ValidationError


class sv_hp_dktc(models.Model):
    _name = "sv_hp_dktc"
    _description = "Sinh viên - Học phần - Đợt đăng ký tín chỉ"

    # muc_hoc_phi_phai_dong = fields.Many2one(
    #     comodel_name="danh_muc.bieu_gia",
    #     string="Mức phí phải đóng",
    #     related="sinh_vien_id.khoa_nganh_id.bieu_gia_id"
    # )
    hoc_phi = fields.Integer(compute="_compute_hoc_phi",
                             store=True,
                             string="Học phí")
    ghi_chu = fields.Text("Ghi chú")
    phieu_dang_ky_tin_chi_id = fields.Many2one(
        comodel_name="phieu_dang_ky_tin_chi",
        ondelete="cascade",
        string="Phiếu đăng ký tín chỉ")
    dot_dk_tin_chi_id = fields.Many2one(
        "dot_dang_ky_tin_chi",
        related="phieu_dang_ky_tin_chi_id.dot_dang_ky_tin_chi_id",
        store=True,
        readonly=False,
    )
    sinh_vien_id = fields.Many2one(
        "sinh_vien",
        related="phieu_dang_ky_tin_chi_id.sinh_vien_id",
        string="Sinh viên",
        readonly=False,
        required=True,
    )
    name = fields.Char("Họ và tên",
                       size=100,
                       related="sinh_vien_id.name",
                       store=True)
    lop_tin_chi_id = fields.Many2one(comodel_name="lop_tin_chi",
                                     string="Lớp tín chỉ",
                                     required=True)
    nhom_lop_tin_chi_id = fields.Many2one(
        comodel_name="nhom_lop_tin_chi",
        string="Nhóm lớp tín chỉ",
    )
    hoc_phan_id = fields.Many2one(related="lop_tin_chi_id.mon_hoc_ids",
                                  string="Học phần",
                                  required=True)
    ten_hoc_phan = fields.Char("Tên học phần",
                               related="hoc_phan_id.ten_hoc_phan",
                               store=True)
    so_tin_chi = fields.Integer(
        "Số tín chỉ",
        related="hoc_phan_id.so_tin_chi",
        store=True,
        group_operator=False,
    )
    ky_hoc_id = fields.Many2one(related="phieu_dang_ky_tin_chi_id.ky_hoc_id",
                                store=True)

    @api.model
    def create(self, values):
        # if len(lop_tin_chi_id.sinh_vien_ids) >= lop_tin_chi_id.si_so:
        #     print("lớp full rồi ae ơi!!")
        #     raise ValidationError(f"Lớp {lop_tin_chi_id.ten_lop_tin_chi} đã có đủ sinh viên!")
        # else:
        #     print("ngon vẫn còn slot thêm vào lớp nào!!")
        #     lop_tin_chi_id.sinh_vien_ids = [(4, values['sinh_vien_id'])]
        res = super(sv_hp_dktc, self).create(values)
        lop_tin_chi_id = self.env['lop_tin_chi'].sudo().search([
            ('id', '=', res.lop_tin_chi_id.id)
        ])
        lop_tin_chi_id.sinh_vien_ids = [(4, res.sinh_vien_id.id)]
        nhom_lop_tin_chi_id = self.env['nhom_lop_tin_chi'].sudo().search([
            ('id', '=', res.nhom_lop_tin_chi_id.id)
        ])
        nhom_lop_tin_chi_id.sinh_vien_ids = [(4, res.sinh_vien_id.id)]
        return res

    def write(self, update_values):
        for record in self:
            if 'lop_tin_chi_id' in update_values and record.lop_tin_chi_id.id != update_values[
                    'lop_tin_chi_id']:
                print("Có một cháu đổi lớp")
                record.lop_tin_chi_id.sinh_vien_ids = [
                    (3, record.sinh_vien_id.id)
                ]
                lop_tin_chi_id_new = self.env['lop_tin_chi'].sudo().search([
                    ('id', '=', update_values['lop_tin_chi_id'])
                ])
                # if len(lop_tin_chi_id_new.sinh_vien_ids) >= lop_tin_chi_id_new.si_so:
                #     print("lớp full rồi ae ơi!!")
                #     raise ValidationError(f"Lớp {lop_tin_chi_id_new.ten_lop_tin_chi} đã có đủ sinh viên!")
                # else:
                #     print("ngon vẫn còn slot thêm vào lớp nào!!")
                #     lop_tin_chi_id_new.sinh_vien_ids = [(4, record.sinh_vien_id.id)]
                lop_tin_chi_id_new.sinh_vien_ids = [(4, record.sinh_vien_id.id)
                                                    ]
            if "nhom_lop_tin_chi_id" in update_values and record.nhom_lop_tin_chi_id.id != update_values[
                    "nhom_lop_tin_chi_id"]:
                record.nhom_lop_tin_chi_id.sinh_vien_ids = [
                    (3, record.sinh_vien_id.id)
                ]
                nhom_lop_tin_chi_id_new = self.env['nhom_lop_tin_chi'].sudo(
                ).search([('id', '=', update_values['nhom_lop_tin_chi_id'])])
                # if len(lop_tin_chi_id_new.sinh_vien_ids) >= lop_tin_chi_id_new.si_so:
                #     print("lớp full rồi ae ơi!!")
                #     raise ValidationError(f"Lớp {lop_tin_chi_id_new.ten_lop_tin_chi} đã có đủ sinh viên!")
                # else:
                #     print("ngon vẫn còn slot thêm vào lớp nào!!")
                #     lop_tin_chi_id_new.sinh_vien_ids = [(4, record.sinh_vien_id.id)]
                nhom_lop_tin_chi_id_new.sinh_vien_ids = [
                    (4, record.sinh_vien_id.id)
                ]
        res = super(sv_hp_dktc, self).write(update_values)
        return res

    def unlink(self):
        for record in self:
            print("check và bỏ sinh viên khỏi lớp nào", self)
            record.lop_tin_chi_id.sinh_vien_ids = [(3, record.sinh_vien_id.id)]
            record.nhom_lop_tin_chi_id.sinh_vien_ids = [
                (3, record.sinh_vien_id.id)
            ]
        res = super(sv_hp_dktc, self).unlink()
        return res

    # ma_khoan_thu = fields.Many2one(
    #     comodel_name="danh_muc.khoan_thu",
    #     related="hoc_phi.khoan_thu_id",
    #     store=True,
    #     string="Mã khoản thu"
    # )

    # @api.depends("ky_hoc_id", "so_tin_chi")
    # def _compute_hoc_phi(self):
    #     for record in self:
    #         thong_tin_hoc_phi = self.env["hoc_phi"].search(
    #             [("khoa_nganh_ids", "in", record.sinh_vien_id.khoa_nganh_id.id)],
    #             limit=1, order="nam_hoc desc"
    #         )
    #         if thong_tin_hoc_phi.phuong_thuc_thu_phi == "0":
    #             record.hoc_phi = thong_tin_hoc_phi.gia_tin_chi_chung * record.so_tin_chi
    #         elif thong_tin_hoc_phi.phuong_thuc_thu_phi == "1":
    #             mon_hoc_dieu_kien = self.env["mon_hoc_dieu_kien"].search(
    #                 [
    #                     (
    #                         "ctk_id",
    #                         "in",
    #                         [record.sinh_vien_id.ctk_nganh_id.id, record.sinh_vien_id.ctk_chuyen_nganh_id.id]
    #                     ),
    #                     (
    #                         "hoc_phan_id", "=", record.hoc_phan_id.id,
    #                     )
    #                 ],
    #                 limit=1,
    #             )
    #             hoc_ky_ctk = self.env["hoc_ky_chuong_trinh_khung"].search(
    #                 [
    #                     (
    #                         "ctk_id",
    #                         "in",
    #                         [record.sinh_vien_id.ctk_nganh_id.id, record.sinh_vien_id.ctk_chuyen_nganh_id.id]
    #                     ),
    #                 ]
    #             )
    #             map_hoc_ky = dict(zip(hoc_ky_ctk.mapped("hoc_ky"), hoc_ky_ctk.mapped("loai_ky")))
    #             if mon_hoc_dieu_kien.hoc_ky in map_hoc_ky:
    #                 if map_hoc_ky[mon_hoc_dieu_kien.hoc_ky] == "0":
    #                     record.hoc_phi = thong_tin_hoc_phi.gia_tin_chi_ky_thuong_xuyen * record.so_tin_chi
    #                 else:
    #                     record.hoc_phi = thong_tin_hoc_phi.gia_tin_chi_ky_tot_nghiep * record.so_tin_chi
    #             else:
    #                 record.hoc_phi = record.hoc_phi
    #         else:
    #             record.hoc_phi = record.hoc_phi
    #
