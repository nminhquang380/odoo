from odoo import fields, models, api
import base64
from pathlib import Path


class TinTuc(models.Model):
    _name = "tin_tuc"
    _description = "Tin tức"
    _rec_name = "mo_ta"

    dict_vai_tro = {
        "sinh_vien": "Sinh Viên",
        "giang_vien": "Giảng viên",
        "quan_tri": "Quản trị viên",
        "mentor": "Mentor",
    }
    avatar = fields.Image("Avatar", max_width=256)
    avatar_path = fields.Char("Avatar URL")
    mo_ta = fields.Text("Mô tả")
    noi_dung = fields.Html("Nội dung")
    ngay_dang = fields.Datetime("Ngày đăng")
    nguoi_dang = fields.Char("Người đăng")

    nguon_tin = fields.Char("Nguồn tin")
    duong_dan = fields.Char("Đường dẫn dành cho quản trị viên")
    #
    # @api.model
    # def create(self, vals):
    #     res = super(TinTuc, self).create(vals)
    #     self = self.with_context(MyModelLoopBreaker=True)
    #     vai_tro = self.env.user.partner_id.vai_tro
    #     name = self.env.user.partner_id.name
    #     if vai_tro:
    #         vai_tro = self.dict_vai_tro[self.env.user.partner_id.vai_tro]
    #         name = (
    #             self.env[self.env.user.partner_id.vai_tro]
    #             .search([("user_id", "=", self.env.user.id)])
    #             .name
    #         )
    #     else:
    #         vai_tro = ""
    #     res.nguoi_dang = vai_tro + " " + name
    #     res.ngay_dang = fields.Datetime.now()
    #     path = Path(__file__)
    #     avatar_path = path.parent.parent.joinpath("static/avatar_tin_tuc")
    #     try:
    #         avatar_path.mkdir()
    #     except:
    #         pass
    #     if res.avatar:
    #         imgdata = base64.b64decode(res.avatar)
    #         filename = avatar_path.joinpath(f"{res.id}.jpg")
    #         with open(filename, "wb") as f:
    #             f.write(imgdata)
    #         self = self.with_context(MyModelLoopBreaker=True)
    #         res.avatar_path = filename.relative_to(filename.parent.parent.parent.parent)
    #     return res
    #
    # def write(self, values):
    #     res = super(TinTuc, self).write(values)
    #     if self.env.context.get("MyModelLoopBreaker"):
    #         return
    #     self = self.with_context(MyModelLoopBreaker=True)
    #     path = Path(__file__)
    #     avatar_path = path.parent.parent.joinpath("static/avatar_tin_tuc")
    #     try:
    #         avatar_path.mkdir()
    #     except:
    #         pass
    #     if self.avatar:
    #         imgdata = base64.b64decode(self.avatar)
    #         filename = avatar_path.joinpath(f"{self.id}.jpg")
    #         with open(filename, "wb") as f:
    #             f.write(imgdata)
    #         self = self.with_context(MyModelLoopBreaker=True)
    #         self.avatar_path = filename.relative_to(
    #             filename.parent.parent.parent.parent
    #         )
    #     return res
    #
    # def unlink(self):
    #     for record in self:
    #         if record.avatar_path:
    #             path = Path(__file__).parent.parent.parent.joinpath(record.avatar_path)
    #             if path.exists():
    #                 path.unlink()
    #     res = super(TinTuc, self).unlink()
    #     return res
