from odoo import models, fields
from .constants_of_selection_fields import phuong_thuc_thu_phi_selection
from .constants_of_selection_fields import don_vi_tien_te_selection
from .env_thanh_toan import base_url_hoc_phi
from odoo import fields, models, api
from odoo.exceptions import ValidationError
from odoo.exceptions import ValidationError
import re
import requests

class HocPhi(models.Model):
    _name = "hoc_phi"
    _description = "Học phí"
    _rec_name = "ma_hoc_phi"

    ma_hoc_phi = fields.Char("Mã học phí", size=200, required=True)
    nam_hoc_id = fields.Many2one(
        comodel_name="nam_hoc",
        string="Năm học"
    )
    nam_hoc = fields.Integer(
        string="Năm học",
        related="nam_hoc_id.nam_hoc",
        store=True,
    )
    khoa_nganh_ids = fields.One2many(
        comodel_name="khoa_nganh",
        inverse_name="hoc_phi_ids",
        string="Danh sách khóa-ngành"
    )
    phuong_thuc_thu_phi = fields.Selection(
        selection=phuong_thuc_thu_phi_selection,
        string="Phương thức thu phí",
        required=True
    )
    don_vi_tien_te = fields.Selection(
        selection=don_vi_tien_te_selection,
        string="Đơn vị tiền tệ",
        required=True
    )
    gia_tin_chi_chung = fields.Float(string="Giá tín chỉ chung", required=True)
    gia_tin_chi_ky_thuong_xuyen = fields.Float(
        string="Giá tín chỉ thường xuyên")
    gia_tin_chi_ky_tot_nghiep = fields.Float(string="Giá tín chỉ tốt nghiệp")
    gia_hoc_ky = fields.Float(string="Giá học kỳ")
    gia_nam_hoc = fields.Float(string="Giá năm học")

    khoan_thu_id = fields.Many2one(
        comodel_name="danh_muc.khoan_thu",
        ondelete="set null",
        string="Mã khoản thu (nếu có)"
    )

    def create_product(self, values):
        check_product =  requests.get(f"{base_url_hoc_phi}/product/code/{values['ma_hoc_phi']}").json()['data']
        if not check_product:
            url_create_product = str(f"{base_url_hoc_phi}/product")
            json_create_product = {
                "code": values['ma_hoc_phi'],
                "name": values['ma_hoc_phi'],
                "metaData": {}
            }
            tao_product = requests.post(url=url_create_product, json=json_create_product)
            if tao_product.status_code == 201:
                url_create_price = str(f"{base_url_hoc_phi}/price")
                json_create_price = {
                    "product": tao_product.json()['data']['_id'],
                    "name": "gia tien 1 tin chi",
                    "unitAmount": values['gia_tin_chi_chung'],
                    "currency": "VND",
                    "metaData": {}
                }
                tao_price = requests.post(url=url_create_price, json=json_create_price)
                if not tao_price.status_code == 201:
                    raise ValidationError(
                        f"Tạo mới học phí {values['ma_hoc_phi']} trên hệ thống thanh toán không thành công!")
                else:
                    return True
            else:
                raise ValidationError(f"Tạo mới học phí {values['ma_hoc_phi']} không thành công do status_code = {tao_product.status_code}")
        else:
            raise ValidationError(
                f"Tạo mới học phí {values['ma_hoc_phi']} không thành công do mã học phí đã tồn tại trên hệ thống thanh toán")
        return False


    @api.model
    def create(self, values):
        if values['ma_hoc_phi']:
            vls = self.env["hoc_phi"].search([("ma_hoc_phi", "=", values['ma_hoc_phi'])])
            if vls:
                raise ValidationError(f"Mã học phí {values['ma_hoc_phi']} đã được sử dụng!")
        tao_moi_hoc_phi = self.create_product(values)
        if not tao_moi_hoc_phi:
            raise ValidationError(f"Tạo mới học phí {values['ma_hoc_phi']} không thành công!")
        res = super(HocPhi, self).create(values)
        return res

    def write(self, update_values):
        if 'ma_hoc_phi'in update_values:
            if self.ma_hoc_phi != update_values['ma_hoc_phi']:
                raise ValidationError(f"Để đảm bảo tính minh bạch, Hệ thống không cho phép thay đổi mã học phí!")
        if 'gia_tin_chi_chung' in update_values:
            if (self.gia_tin_chi_chung != update_values['gia_tin_chi_chung']):
                print("OH cập nhật giá tiền một tín nè")
                get_product = requests.get(f"{base_url_hoc_phi}/product/code/{self.ma_hoc_phi}")
                if get_product.status_code == 200:
                    get_product = get_product.json()['data']
                    #đoạn này sẽ archive các price cũ
                    for vl in get_product['prices']:
                        if vl['active'] == True:
                            url_archive_price = str(f"{base_url_hoc_phi}/price/archive/{vl['_id']}")
                            archive_price = requests.put(url=url_archive_price)
                            if not archive_price.status_code == 200:
                                raise ValidationError(f"Cập nhật giá tiền không thành công")
                    #sau khi archive các price cũ thì tạo một cái price mới thôi :V
                    url_update_price = f"{base_url_hoc_phi}/price"
                    json_update_price = {
                        "product": vl['product'],
                        "active": True,
                        "name": "gia tien 1 tin chi",
                        "unitAmount": update_values['gia_tin_chi_chung'],
                        "currency": "VND",
                        "metaData": {}
                    }
                    update_price = requests.post(url=url_update_price, json=json_update_price)
                    if not update_price.status_code == 201:
                        raise ValidationError(f"Cập nhật giá tiền không thành công")

                else:
                    raise ValidationError(f"Không tồn tại mã học phí {self.ma_hoc_phi} trên hệ thống thanh toán")
        res = super(HocPhi, self).write(update_values)
        return res

    def unlink(self):
        """
        Override unlink method :
        """
        raise ValidationError(f"Để đảm bảo tính minh bạch, Hệ thống không cho phép xóa học phí!")
        return super(HocPhi, self).unlink()

