from odoo import fields, models
import tempfile
import os
import base64
import pandas as pd
import time
import datetime


class ReportDangKyNhuCau(models.TransientModel):
    _name = "report_dang_ky_nhu_cau"
    _description = "Report đăng ký nhu cầu"

    dot_dang_ky_nhu_cau_id = fields.Many2one(
        comodel_name="dot_dang_ky_nhu_cau", string="Đợt đăng ký nhu cầu")

    def export_report(self):
        export_data = {}
        danh_sach_nhu_cau_theo_dot = self.env["nv_hoc_phan"].search([
            ("dot_dk_nhu_cau_id", "=", self.dot_dang_ky_nhu_cau_id.id)
        ])
        for record in danh_sach_nhu_cau_theo_dot:
            key_hoc_phan = (record.ten_hoc_phan,
                            record.hoc_phan_id.ma_hoc_phan_moi)
            if key_hoc_phan not in export_data:
                export_data[key_hoc_phan] = {
                    "tongSoSinhVien": 1,
                    "tongHocPhi": record.hoc_phi,
                }
            else:
                export_data[key_hoc_phan]["tongSoSinhVien"] += 1
                export_data[key_hoc_phan]["tongHocPhi"] += record.hoc_phi
        fd, path = tempfile.mkstemp()
        df = pd.DataFrame(columns=[
            "tenHocPhan", "maHocPhan", "tongSoSinhVien", "tongHocPhi"
        ])
        phieu_dk_nhu_cau = self.env["phieu_dang_ky_hoc_phan"].search([
            ("dot_dang_ky_id", "=", self.dot_dang_ky_nhu_cau_id.id),
            ("nv_hoc_phan_id", "!=", False),
        ])
        tongSinhVienDangKy = len(phieu_dk_nhu_cau)
        tongSinhVienToanKhoa = 0
        for khoi_lop in self.dot_dang_ky_nhu_cau_id.khoi_lop_ids:
            for lop_hanh_chinh in khoi_lop.lop_hanh_chinh_ids:
                tongSinhVienToanKhoa += len(lop_hanh_chinh.sinh_vien_ids)
        for hp in export_data:
            tongSoSinhVien = export_data[hp]["tongSoSinhVien"]
            tongHocPhi = export_data[hp]["tongHocPhi"]
            df = df.append(
                {
                    "tenHocPhan": hp[0],
                    "maHocPhan": hp[1],
                    "tongSoSinhVien": tongSoSinhVien,
                    "tongHocPhi": tongHocPhi,
                },
                ignore_index=True)
        df = df.append(
            {
                "tenHocPhan":
                f"Tổng số sinh viên đã đăng ký: {tongSinhVienDangKy}",
                "maHocPhan": "",
                "tongSoSinhVien": "",
                "tongHocPhi": "",
            },
            ignore_index=True)
        df = df.append(
            {
                "tenHocPhan":
                f"Tổng số sinh viên toàn đợt đăng ký: {tongSinhVienToanKhoa}",
                "maHocPhan": "",
                "tongSoSinhVien": "",
                "tongHocPhi": "",
            },
            ignore_index=True)
        df.to_csv(path, index=False, encoding="utf-8-sig")
        result = base64.b64encode(os.fdopen(fd, "rb").read())
        attachment = self.env['ir.attachment'].create({
            'name': "tong_hop_so_lieu_nhu_cau.csv",
            'store_fname': 'thsl.csv',
            'datas': result
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % (attachment.id),
            'target': 'self',
        }


class ExportTemplate(models.TransientModel):
    _name = "export_template"
    _description = "Export templates"

    hinh_thuc_dao_tao = fields.Many2one(comodel_name="hinh_thuc_dao_tao",
                                        string="Hình thức đào tạo",
                                        default=lambda self: self.env.user.hinh_thuc_dao_tao_id)
    
    co_masv = fields.Boolean("Đã có mã sinh viên")

    def export_mau_import_sv_nv(self):
        fd, path = tempfile.mkstemp(suffix='.xlsx')
        
        import_template = pd.DataFrame()
        if self.co_masv:
            import_template = pd.DataFrame(columns=["Mã sinh viên",
            "Ngành học", "Họ và tên", "Họ đệm", "Tên", "Ngày sinh", "Email",
            "Chứng minh nhân dân/Căn cước công dân", "Số điện thoại"
        ])
        elif not self.co_masv:
            import_template = pd.DataFrame(columns=[
            "Ngành học", "Họ và tên", "Họ đệm", "Tên", "Ngày sinh", "Email",
            "Chứng minh nhân dân/Căn cước công dân", "Số điện thoại"
        ])
        
        import_template.to_excel(path, index=False)
        result = base64.b64encode(os.fdopen(fd, "rb").read())
        attachment = self.env['ir.attachment'].create({
            'name': "mau_import_sv_nv.xlsx",
            'store_fname': 'test.xlsx',
            'datas': result
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % (attachment.id),
            'target': 'self',
        }

class ExportHoaDon(models.TransientModel):
    _name = "export_hoa_don"
    _description = "Export Hóa Đơn"

    hinh_thuc_dao_tao_id = fields.Many2one(
        comodel_name="hinh_thuc_dao_tao",
        ondelete="set null",
        string="Hình thức đào tạo",
    )
    ngay_bat_dau = fields.Datetime("Từ ngày")
    ngay_ket_thuc = fields.Datetime("Đến ngày")
    khoa_nganh_ids = fields.Many2one(comodel_name="khoa_nganh",
                                     string="Danh sách khóa ngành")
    trang_thai_thanh_toan = fields.Selection([("chua_thanh_toan", "Hóa đơn chưa thanh toán"),
                           ("da_thanh_toan", "Hóa đơn đã thanh toán"),
                           ("tat_ca", "Tất cả hóa đơn")], string="Trạng thái hóa đơn", required=True)

    def action_export_bao_cao_hoa_don(self):
        fd, path = tempfile.mkstemp(suffix='.xlsx')

        df2 = pd.DataFrame(columns=["Ngày ghi sổ", "Số chứng từ", "Số hóa đơn", "Hình thức thanh toán", "Mã đối tượng", "Tên đối tượng",
                                    "Mã lớp", "Tên lớp", "Mã khoản thu", "Tên khoản thu", "Nội dung", "Đơn vị tính", "Số lượng",
                                    "Đơn giá", "Số tiền", "Số tiền Nợ", "Số tiền thực Nợ", "Kỳ thu phí", "Mã loại, TĐ ĐT", "Tên loại hình đào tạo", "Đối tượng TK Nợ",
                                    "Tên đối tượng TK Nợ", "Đối tượng TK Có", "Tên đối tượng TK Có", "Địa chỉ", "Mã thanh toán"])

        domain = []
        if self.hinh_thuc_dao_tao_id:
            domain.append(("hinh_thuc_dao_tao_id", "=", self.hinh_thuc_dao_tao_id.id))
        if self.ngay_bat_dau:
            # ngay_bat_dau = self.ngay_bat_dau - datetime.timedelta(hours=7, minutes=0)
            ngay_bat_dau = self.ngay_bat_dau
            domain.append(("write_date", ">=", ngay_bat_dau))
            if self.trang_thai_thanh_toan == "da_thanh_toan":
                domain.append(("ngay_nop_tien", ">=", ngay_bat_dau))
        if self.ngay_ket_thuc:
            # ngay_ket_thuc = self.ngay_ket_thuc - datetime.timedelta(hours=7, minutes=0)
            ngay_ket_thuc = self.ngay_ket_thuc
            domain.append(("write_date", "<=", ngay_ket_thuc))
            if self.trang_thai_thanh_toan == "da_thanh_toan":
                domain.append(("ngay_nop_tien", "<=", ngay_ket_thuc))
        print(self.ngay_bat_dau, self.ngay_ket_thuc)
        danh_sach_hoa_don = self.env["qldt.hoa_don"].search(domain)
        print(danh_sach_hoa_don)
        for vl in danh_sach_hoa_don:
            if self.trang_thai_thanh_toan == "da_thanh_toan":
                if vl.so_tien_da_nhan > 0 or vl.trang_thai == '0' or vl.trang_thai == '1' or vl.trang_thai == '2':
                    df2 = df2.append(
                        {
                            "Ngày ghi sổ": vl.ngay_nop_tien + datetime.timedelta(hours=7, minutes=0),
                            "Số chứng từ": "",
                            "Số hóa đơn": "",
                            "Hình thức thanh toán": "CK2",
                            "Mã đối tượng": vl.sinh_vien_id.ma_dinh_danh,
                            "Tên đối tượng": vl.sinh_vien_id.name,
                            "Mã lớp": vl.sinh_vien_id.lop_hanh_chinh_id.ten_lop_hanh_chinh,
                            "Tên lớp": vl.sinh_vien_id.lop_hanh_chinh_id.ten_lop_hanh_chinh,
                            "Mã khoản thu": vl.khoan_thu_id.ma_khoan_thu,
                            "Tên khoản thu": vl.khoan_thu_id.ten_khoan_thu,
                            "Nội dung": vl.ma_hoa_don,
                            "Đơn vị tính": "",
                            "Số lượng": vl.so_luong_don_vi_dich_vu,
                            "Đơn giá": vl.gia_tien_mot_dich_vu,
                            "Số tiền": vl.tong_so_tien,
                            "Số tiền Nợ": -(vl.cong_no_hoa_don),
                            "Số tiền thực Nợ": -(vl.cong_no_hoa_don),
                            "Kỳ thu phí": str(vl.ky_nam_hoc_id.ten_ky_nam_hoc + '/'+vl.ky_nam_hoc_id.nam_hoc_id.ten_nam_hoc),
                            "Mã loại, TĐ ĐT": vl.hinh_thuc_dao_tao_id.ten_hinh_thuc_dao_tao,
                            "Tên loại hình đào tạo": vl.hinh_thuc_dao_tao_id.ten_hinh_thuc_dao_tao,
                            "Đối tượng TK Nợ": "",
                            "Tên đối tượng TK Nợ": "",
                            "Đối tượng TK Có": "",
                            "Tên đối tượng TK Có": "",
                            "Địa chỉ": vl.sinh_vien_id.lop_hanh_chinh_id.ten_lop_hanh_chinh,
                            "Mã thanh toán": vl.ma_thanh_toan,
                        },
                        ignore_index=True)
            elif self.trang_thai_thanh_toan == "chua_thanh_toan":
                if vl.so_tien_da_nhan == 0 or vl.trang_thai == '-1':
                    df2 = df2.append(
                        {
                            "Ngày ghi sổ": vl.write_date + datetime.timedelta(hours=7, minutes=0),
                            "Số chứng từ": "",
                            "Số hóa đơn": "",
                            "Hình thức thanh toán": "CK2",
                            "Mã đối tượng": vl.sinh_vien_id.ma_dinh_danh,
                            "Tên đối tượng": vl.sinh_vien_id.name,
                            "Mã lớp": vl.sinh_vien_id.lop_hanh_chinh_id.ten_lop_hanh_chinh,
                            "Tên lớp": vl.sinh_vien_id.lop_hanh_chinh_id.ten_lop_hanh_chinh,
                            "Mã khoản thu": vl.khoan_thu_id.ma_khoan_thu,
                            "Tên khoản thu": vl.khoan_thu_id.ten_khoan_thu,
                            "Nội dung": vl.ma_hoa_don,
                            "Đơn vị tính": "",
                            "Số lượng": vl.so_luong_don_vi_dich_vu,
                            "Đơn giá": vl.gia_tien_mot_dich_vu,
                            "Số tiền": vl.tong_so_tien,
                            "Số tiền Nợ": -(vl.cong_no_hoa_don),
                            "Số tiền thực Nợ": -(vl.cong_no_hoa_don),
                            "Kỳ thu phí": str(vl.ky_nam_hoc_id.ten_ky_nam_hoc + '/'+vl.ky_nam_hoc_id.nam_hoc_id.ten_nam_hoc),
                            "Mã loại, TĐ ĐT": vl.hinh_thuc_dao_tao_id.ten_hinh_thuc_dao_tao,
                            "Tên loại hình đào tạo": vl.hinh_thuc_dao_tao_id.ten_hinh_thuc_dao_tao,
                            "Đối tượng TK Nợ": "",
                            "Tên đối tượng TK Nợ": "",
                            "Đối tượng TK Có": "",
                            "Tên đối tượng TK Có": "",
                            "Địa chỉ": vl.sinh_vien_id.lop_hanh_chinh_id.ten_lop_hanh_chinh,
                            "Mã thanh toán": vl.ma_thanh_toan,
                        },
                        ignore_index=True)
            elif self.trang_thai_thanh_toan == "tat_ca":
                df2 = df2.append(
                    {
                        "Ngày ghi sổ": vl.ngay_nop_tien + datetime.timedelta(hours=7, minutes=0),
                        "Số chứng từ": "",
                        "Số hóa đơn": "",
                        "Hình thức thanh toán": "CK2",
                        "Mã đối tượng": vl.sinh_vien_id.ma_dinh_danh,
                        "Tên đối tượng": vl.sinh_vien_id.name,
                        "Mã lớp": vl.sinh_vien_id.lop_hanh_chinh_id.ten_lop_hanh_chinh,
                        "Tên lớp": vl.sinh_vien_id.lop_hanh_chinh_id.ten_lop_hanh_chinh,
                        "Mã khoản thu": vl.khoan_thu_id.ma_khoan_thu,
                        "Tên khoản thu": vl.khoan_thu_id.ten_khoan_thu,
                        "Nội dung": vl.ma_hoa_don,
                        "Đơn vị tính": "",
                        "Số lượng": vl.so_luong_don_vi_dich_vu,
                        "Đơn giá": vl.gia_tien_mot_dich_vu,
                        "Số tiền": vl.tong_so_tien,
                        "Số tiền Nợ": -(vl.cong_no_hoa_don),
                        "Số tiền thực Nợ": -(vl.cong_no_hoa_don),
                        "Kỳ thu phí": str(
                            vl.ky_nam_hoc_id.ten_ky_nam_hoc + '/' + vl.ky_nam_hoc_id.nam_hoc_id.ten_nam_hoc),
                        "Mã loại, TĐ ĐT": vl.hinh_thuc_dao_tao_id.ten_hinh_thuc_dao_tao,
                        "Tên loại hình đào tạo": vl.hinh_thuc_dao_tao_id.ten_hinh_thuc_dao_tao,
                        "Đối tượng TK Nợ": "",
                        "Tên đối tượng TK Nợ": "",
                        "Đối tượng TK Có": "",
                        "Tên đối tượng TK Có": "",
                        "Địa chỉ": vl.sinh_vien_id.lop_hanh_chinh_id.ten_lop_hanh_chinh,
                        "Mã thanh toán": vl.ma_thanh_toan,
                    },
                    ignore_index=True)
        with pd.ExcelWriter(path) as writer:
            df2.to_excel(writer,
                         sheet_name='Báo cáo hóa đơn',
                         index=False)
        result = base64.b64encode(os.fdopen(fd, "rb").read())
        attachment = self.env['ir.attachment'].create({
            'name': "bao_cao_hoa_don.xlsx",
            'store_fname': 'thsl.xlsx',
            'datas': result
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % (attachment.id),
            'target': 'self',
        }






