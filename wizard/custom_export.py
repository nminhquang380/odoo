import base64
from multiprocessing.dummy import active_children
import os
import tempfile
from numpy import require
import pandas as pd
from odoo import fields, models
from datetime import datetime

"""
thêm mã sinh viên, ngày tháng năm sinh
fill các dữ liệu ở trên với tất cả các dòng

chia các lớp hành chính thành từng sheet.
Chia 2 options khi export:
 + như trên.
 + có 2 file: lớp hành chính + sinh viên lớp hành chính.
 
"""
class LopHanhChinhExportWizard(models.TransientModel):
    _name = "lop_hanh_chinh.custom_export"
    _description = "Export lớp hành chính"

    lop_hanh_chinh_ids = fields.Many2many(
        "lop_hanh_chinh",
        string="Lớp hành chính"
    )

    _header = {
        "tich_hop": [
            "Tên lớp hành chính", "Hình thức đào tạo", "Khóa sinh viên", "Ngành", "Cán bộ phụ trách",
            "Năm học", "Số thứ tự đợt nhập học", "Tên sinh viên", "Mã sinh viên"
        ],
        "rieng_biet": [
            "Hình thức đào tạo", "Khóa sinh viên", "Ngành", "Cán bộ phụ trách",
            "Năm học", "Số thứ tự đợt nhập học", "Cơ sở đào tạo", "Số thứ tự lớp"
            ]
    }

    export_options = fields.Selection([
        ("rieng_biet", "Danh sách sinh viên và lớp hành chính riêng biệt"),
        ("tich_hop", "Danh sách sinh viên và lớp hành chính tích hợp")
    ],
    string="Biểu mẫu xuất",
    required=True)

    def export_lop_hanh_chinh(self):
        fd, path = tempfile.mkstemp(suffix='.xlsx')
        if self.export_options == "tich_hop":
            df1 = pd.DataFrame(columns=self._header["tich_hop"])
            for record in self.lop_hanh_chinh_ids:
                for sinhvien in record.sinh_vien_ids:
                    df1 = df1.append(
                        {
                            "Tên lớp hành chính" : record.ten_lop_hanh_chinh, 
                            "Hình thức đào tạo" : record.hinh_thuc_dao_tao_id.ten_hinh_thuc_dao_tao, 
                            "Khóa sinh viên" : record.khoa_sinh_vien.so_thu_tu_khoa, 
                            "Ngành" : record.nganh.ten_nganh, 
                            "Cán bộ phụ trách" : record.can_bo_id.ma_dinh_danh,
                            "Năm học" : record.khoa_sinh_vien.nam_hoc.ten_nam_hoc, 
                            "Số thứ tự đợt nhập học" : record.khoi_lop_id.dot_nhap_hoc_id.thu_tu_dot, 
                            "Tên sinh viên" : sinhvien.name, 
                            "Mã sinh viên" : sinhvien.ma_dinh_danh,
                        },
                        ignore_index=True
                    )
            with pd.ExcelWriter(path) as writer:
                df1.to_excel(writer,
                        sheet_name='Danh sách sinh viên lớp hành chính',
                        index=False)
        else:
            df1 = pd.DataFrame(columns=self._header["rieng_biet"])
            for record in self.lop_hanh_chinh_ids:
                df1 = df1.append(
                    {
                        "Hình thức đào tạo" : record.hinh_thuc_dao_tao_id.ten_hinh_thuc_dao_tao, 
                        "Khóa sinh viên" : record.khoa_sinh_vien.so_thu_tu_khoa, 
                        "Ngành" : record.nganh.ten_nganh, 
                        "Cán bộ phụ trách" : record.can_bo_id.ma_dinh_danh,
                        "Năm học" : record.khoa_sinh_vien.nam_hoc.ten_nam_hoc, 
                        "Số thứ tự đợt nhập học" : record.khoi_lop_id.dot_nhap_hoc_id.thu_tu_dot, 
                        "Cơ sở đào tạo" : record.co_so_dao_tao_moi.ten_co_so_dao_tao, 
                        "Số thứ tự lớp" : record.so_thu_tu_lop,
                    },
                    ignore_index=True
                )
            df2 = pd.DataFrame(columns=["Mã sinh viên", "Tên lớp hành chính"])
            for record in self.lop_hanh_chinh_ids:
                for sinhvien in record.sinh_vien_ids:
                    df2 = df2.append(
                        {
                            "Mã sinh viên" : sinhvien.ma_dinh_danh,
                            "Tên lớp hành chính" : sinhvien.lop_hanh_chinh_id.ten_lop_hanh_chinh,
                        },
                        ignore_index=True
                    )
            with pd.ExcelWriter(path) as writer:
                df1.to_excel(writer,
                        sheet_name='Danh sách lớp hành chính',
                        index=False)
                df2.to_excel(writer,
                        sheet_name='Danh sách sinh viên lớp hành chính',
                        index=False)

        result = base64.b64encode(os.fdopen(fd, "rb").read())
        attachment = self.env['ir.attachment'].create({
            'name': "lop_hanh_chinh.xlsx",
            'store_fname': 'thsl.xlsx',
            'datas': result
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % (attachment.id),
            'target': 'self',
        }

class LopTinChiExportWizard(models.TransientModel):
    _name = "lop_tin_chi.custom_export"
    _description = "Export lớp tín chỉ"

    export_template = fields.Selection([
        ("AIS", "AISoft"),
        ("AQ","Anh Quân"),
    ],required=True)

    lop_tin_chi_id = fields.Many2many(
        "lop_tin_chi",
        string="Lớp tín chỉ"
    )

    def export_lop_tin_chi(self):
        #Template của Anh Quân
        if self.export_template == "AQ":
            fd, path = tempfile.mkstemp(suffix='.xlsx')
            df = pd.DataFrame(columns=["GcKQDK",
                "NhomHoc", "ToHoc", "MaMH", "TenMH", "SoTinChi", "MaSV", "HoLotSV", "TenSV", "NgaySinhC", "MaLop",
                "MaKhoa", "TenKhoa", "MaNganh", "TenNganh", "SoTCHP",
            ])
            for record in self.lop_tin_chi_id:
                for sv in record.sinh_vien_ids:
                    ngaysinh = sv.ngay_sinh
                    ngaysinh = ngaysinh.strftime("%d/%m/%Y")
                    df = df.append(
                            {
                                "GcKQDK" : "",
                                "NhomHoc" : record.so_thu_tu_lop,
                                "ToHoc" : "",
                                "MaMH" : record.mon_hoc_ids.ma_hoc_phan_moi,
                                "TenMH" : record.ten_hoc_phan,
                                "SoTinChi" : record.so_tin_chi,
                                "MaSV" : sv.ma_dinh_danh,
                                "HoLotSV" : sv.ho_dem,
                                "TenSV" : sv.ten,
                                "NgaySinhC" : ngaysinh,
                                "MaLop" : sv.lop_hanh_chinh_id.ten_lop_hanh_chinh,
                                "MaKhoa" : record.mon_hoc_ids.khoa_id.ma_khoa,
                                "TenKhoa" : record.mon_hoc_ids.khoa_id.ten_khoa,
                                "MaNganh" :  sv.ma_nganh,
                                "TenNganh" : sv.ten_nganh,
                                "SoTCHP" : record.so_tin_chi,
                            },
                            ignore_index=True
                    )
            df.to_excel(path, index=False, encoding="utf-8-sig")
            result = base64.b64encode(os.fdopen(fd, "rb").read())
            attachment = self.env['ir.attachment'].create({
                    'name': "danh_sach_lop_tin_chi.xlsx",
                    'store_fname': 'dsltc.xlsx',
                    'datas': result
                })
            return {
                'type': 'ir.actions.act_url',
                'url': '/web/content/%s?download=true' % (attachment.id),
                'target': 'self',
            }
        # Template của AIS
        elif self.export_template == "AIS":
            fd, path = tempfile.mkstemp(suffix='.xlsx')
            
            df = pd.DataFrame(columns=[
                "Mã sinh viên", "Mã học phần", "Số thứ tự lớp", "Số thứ tự nhóm lớp"
            ])
            df_ltc = pd.DataFrame(columns=[
                "Mã học phần", "Số thứ tự lớp tín chỉ", "Mã giảng viên", "Số lượng nhóm thực hành"
            ])
            for record in self.lop_tin_chi_id:

                df_ltc = df_ltc.append(
                    {
                        "Mã học phần" : record.mon_hoc_ids.ma_hoc_phan_moi,
                        "Số thứ tự lớp tín chỉ" : record.so_thu_tu_lop,
                        "Mã giảng viên" : record.giang_vien_id.ma_dinh_danh,
                        "Số lượng nhóm thực hành" : len(record.nhom_lop_tin_chi_id),
                    },
                    ignore_index=True
                )
                for sv in record.sinh_vien_ids:
                    # ToHoc = self.env['nhom_lop_tin_chi'].search([
                    #     ("lop_tin_chi_id.id", "=", self.lop_tin_chi_id),
                    #     ("id", "in", sv.nhom_lop_tin_chi_ids)
                    # ])
                    # ToHoc = ToHoc.so_thu_tu_nhom

                    df = df.append(
                            {
                                "Mã sinh viên" : sv.ma_dinh_danh,
                                "Mã học phần" : record.mon_hoc_ids.ma_hoc_phan_moi,
                                "Số thứ tự lớp" : record.so_thu_tu_lop,
                                "Số thứ tự nhóm lớp" : "",
                            },
                            ignore_index=True
                    )
            

            with pd.ExcelWriter(path) as writer:
                df.to_excel(writer,
                        sheet_name='Danh sách sinh viên lớp tín chỉ',
                        index=False)
                df_ltc.to_excel(writer,
                        sheet_name='Danh sách lớp tín chỉ',
                        index=False)
            result = base64.b64encode(os.fdopen(fd, "rb").read())
            attachment = self.env['ir.attachment'].create({
                'name': "danh_sach_lop_tin_chi.xlsx",
                'store_fname': 'dsltc.xlsx',
                'datas': result
            })
            return {
                'type': 'ir.actions.act_url',
                'url': '/web/content/%s?download=true' % (attachment.id),
                'target': 'self',
            }


class TKBExportWizard(models.TransientModel):
    _name = "thoi_khoa_bieu.custom_export"
    _description = "Export thời khóa biểu"

    _header = {
        "AIS": [
            "Mã học phần",
            "Số thứ tự lớp",
            "Số thứ tự nhóm lớp",
            "Từ ngày",
            "Đến ngày",
            "Thứ kiểu số",
            "Tiết bắt đầu",
            "Tiết kết thúc",
            "Tài khoản GV",
            "Mật khẩu GV",
            "ID Zoom",
            "Mật khẩu Zoom",
            "Phòng học",
            "Mã kỳ học",
        ],
        "AQ": [
            "TenMH",
            "MaNV",
            "TenDayDuNV",
            "MaMH",
            "NHHK",
            "NhomTo",
            "ToTH",
            "NgayBDHK",
            "DSTuanHoc",
            "ThuKieuSo",
            "TietBD",
            "SoTiet",
            "MaPH",
            "HinhThucHoc",
            "GioHoc",
        ],
        "PTTC1": [
            "Tên môn học",
            "Mã học phần",
            "Nhóm lớp môn học",
            "Sĩ số từng nhóm",
            "Số tín chỉ",
            "Tổng số tiết học",
            "Hướng dẫn học tập môn học (15%)",
            "Thí nghiệm, thực hành",
            "Thứ",
            "Ngày",
            "Tiết bắt đầu (*)",
            "Số tiết",
            "Giảng viên",
            "Mã giảng viên",
            "Điện thoại",
            "Lớp",
            "Tài khoản",
            "Mật khẩu",
            "ID phòng học",
            "Mật khẩu Zoom",
            "Số thứ tự đợt đăng ký tín chỉ",
        ],
    }

    export_template = fields.Selection(string="Mẫu export",
                                        selection=[("AIS", "A.I.Soft"),
                                                    ("AQ", "Anh Quân"),
                                                    ("PTTC1", "PTTC1")],
                                                    required=True)

    buoi_hoc_id = fields.Many2many(
                "buoi_hoc",
                string="Buổi học"
    )


    def export_buoi_hoc(self):
        fd, path = tempfile.mkstemp(suffix='.xlsx')
        df = pd.DataFrame(columns=self._header[self.export_template])
        if self.export_template == "AIS":
            for record in self.buoi_hoc_id:
                
                df = df.append(
                    {
                        "Mã học phần" : record.hoc_phan_id.ma_hoc_phan_moi,
                        "Số thứ tự lớp" : record.lop_tin_chi_id.so_thu_tu_lop,
                        "Số thứ tự nhóm lớp": record.lop_tin_chi_id.nhom_lop_tin_chi_id.so_thu_tu_nhom, 
                        "Từ ngày" : record.ngay_bd,
                        "Đến ngày" : "", 
                        "Thứ kiểu số": record.thu_kieu_so,
                        "Tiết bắt đầu" : record.tiet_bd.tiet_hoc, 
                        "Tiết kết thúc" : record.tiet_kt.tiet_hoc,
                        "Tài khoản GV" : record.tai_khoan, 
                        "Mật khẩu GV" : record.mat_khau, 
                        "ID Zoom" : record.id_zoom, 
                        "Mật khẩu Zoom" : record.mat_khau_1,
                        "Phòng học" : record.phong_hoc,
                        "Mã kỳ học" : record.ky_nam_hoc_id.ma_ky_nam_hoc,
                    },
                    ignore_index=True
                )
        elif self.export_template == "AQ":
            for record in self.buoi_hoc_id:
                df = df.append(
                    {
                        "TenMH": record.hoc_phan_id.name,
                        "MaNV" : record.giang_vien_id.ma_dinh_danh,
                        "TenDayDuNV": record.ten_giang_vien,
                        "MaMH" : record.hoc_phan_id.ma_hoc_phan_moi,
                        "NHHK" : record.ky_nam_hoc_id.ma_ky_nam_hoc,
                        "NhomTo": record.nhom_lop_tin_chi_id.so_thu_tu_nhom,
                        "ToTH": record.nhom_lop_tin_chi_id.so_thu_tu_nhom,
                        "NgayBDHK" : record.ngay_bd,
                        "DSTuanHoc" : record.tuan_hoc,
                        "ThuKieuSo" : record.thu_kieu_so,
                        "TietBD" : record.tiet_bd.tiet_hoc,
                        "SoTiet": record.so_tiet,
                        "MaPH" : record.hoc_phan_id.ma_hoc_phan_moi,
                        "GioHoc" : record.ngay_gio_hoc, 
                    },
                    ignore_index=True
                )
        else:
            for record in self.buoi_hoc_id:
                df = df.append(
                    {
                        "Tên môn học" : record.hoc_phan_id.name,
                        "Mã học phần" : record.hoc_phan_id.ma_hoc_phan_moi,
                        "Nhóm lớp môn học" : record.nhom_lop_tin_chi_id.so_thu_tu_nhom,
                        "Sĩ số từng nhóm" : "",
                        "Số tín chỉ" : record.lop_tin_chi_id.so_tin_chi,
                        "Tổng số tiết học" : record.so_tiet,
                        "Hướng dẫn học tập môn học (15%)" : "",
                        "Thí nghiệm, thực hành" : "",
                        "Thứ" : record.thu_kieu_so,
                        "Ngày" : record.ngay_bd,
                        "Tiết bắt đầu (*)" : record.tiet_bd.tiet_hoc,
                        "Số tiết" : record.so_tiet,
                        "Giảng viên" : record.ten_giang_vien,
                        "Mã giảng viên" : record.giang_vien_id.ma_dinh_danh,
                        "Điện thoại" : record.dien_thoai,
                        "Lớp" : record.lop_tin_chi_id.ma_lop,
                        "Tài khoản" : record.tai_khoan,
                        "Mật khẩu" : record.mat_khau,
                        "ID phòng học" : record.id_zoom,
                        "Mật khẩu Zoom" : record.mat_khau_1,
                        "Số thứ tự đợt đăng ký tín chỉ" : record.lop_tin_chi_id.dot_dk_tin_chi_id.so_thu_tu_dot,
                    },
                    ignore_index=True
                )
        df.to_excel(path, index=False, encoding="utf-8-sig")
        result = base64.b64encode(os.fdopen(fd, "rb").read())
        attachment = self.env['ir.attachment'].create({
            'name': "danh_sach_buoi_hoc.xlsx",
            'store_fname': 'dsbh.xlsx',
            'datas': result
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % (attachment.id),
            'target': 'self',
        }
"""
domain theo hình thức đào tạo
thêm trường lớp hành chính hiên tại

"""
class SinhVienExportWizard(models.TransientModel):
    _name = "sinh_vien.custom_export"
    _description = "Export danh sách sinh viên"
    _header = [
         "Mã sinh viên","Ngành", "Họ và tên", "Họ đệm", "Tên", "Ngày sinh", "Email",
            "Chứng minh nhân dân/Căn cước công dân", "Số điện thoại"
    ]

    export_options = fields.Selection([
        ("khoa_nganh", "Khóa - Ngành"),
        ("lop_hanh_chinh", "Lớp hành chính"),
        ("tuy_chon", "danh sách sinh viên tự chọn")],
    string="Export theo nhóm",
    required=True)

    hinh_thuc_dao_tao = fields.Many2one("hinh_thuc_dao_tao",
                                        default=lambda self : self.env.user.hinh_thuc_dao_tao_id,
                                        string="Hình thức đào tạo",
                                        required=True)
    sinh_vien_ids = fields.Many2many("sinh_vien",
                                    string="Danh sách sinh viên"
                                    )
    lop_hanh_chinh_ids = fields.Many2many("lop_hanh_chinh",
                                        string="Lớp hành chính",
                                        domain="[('hinh_thuc_dao_tao_id', '=', hinh_thuc_dao_tao)]")
    khoa_nganh_id = fields.Many2one("khoa_nganh",
                                    string="Khóa ngành",
                                    domain="[('hinh_thuc_dao_tao_id', '=', hinh_thuc_dao_tao)]")

    def export_dssv(self):
        fd, path = tempfile.mkstemp(suffix='.xlsx')             
        df = pd.DataFrame(columns=self._header)             
        if self.export_options == "tuy_chon":
            for record in self.sinh_vien_ids:
                df = df.append(
                    {
                        "Mã sinh viên" : record.ma_dinh_danh,
                        "Ngành" : record.nganh_id.ten_nganh,
                        "Họ và tên" : record.name, 
                        "Họ đệm" : record.ho_dem, 
                        "Tên" : record.ten, 
                        "Ngày sinh" : (record.ngay_sinh).strftime("%d/%m/%Y"), 
                        "Email" : record.email,
                        "Chứng minh nhân dân/Căn cước công dân" : record.so_cmnd, 
                        "Số điện thoại" : record.so_dien_thoai,
                    },
                    ignore_index=True
                )
        elif self.export_options == "lop_hanh_chinh":
            for record in self.lop_hanh_chinh_ids:
                for sv in record.sinh_vien_ids:
                    df = df.append(
                        {
                        "Mã sinh viên" : sv.ma_dinh_danh,
                        "Ngành" : sv.nganh_id.ten_nganh,
                        "Họ và tên" : sv.name, 
                        "Họ đệm" : sv.ho_dem, 
                        "Tên" : sv.ten, 
                        "Ngày sinh" : (sv.ngay_sinh).strftime("%d/%m/%Y"), 
                        "Email" : sv.email,
                        "Chứng minh nhân dân/Căn cước công dân" : sv.so_cmnd, 
                        "Số điện thoại" : sv.so_dien_thoai,
                    },
                    ignore_index=True
                    )
        elif self.export_options == "khoa_nganh":
            dssv = self.env["sinh_vien"].search([
                ("khoa_nganh_id", "=", self.khoa_nganh_id.id),
                ("hinh_thuc_dao_tao_id", "=", self.hinh_thuc_dao_tao.id)
            ])
            for record in dssv:
                df = df.append(
                     {
                        "Mã sinh viên" : record.ma_dinh_danh,
                        "Ngành" : record.nganh_id.ten_nganh,
                        "Họ và tên" : record.name, 
                        "Họ đệm" : record.ho_dem, 
                        "Tên" : record.ten, 
                        "Ngày sinh" : (record.ngay_sinh).strftime("%d/%m/%Y"), 
                        "Email" : record.email,
                        "Chứng minh nhân dân/Căn cước công dân" : record.so_cmnd, 
                        "Số điện thoại" : record.so_dien_thoai,
                    },
                    ignore_index=True
                )
        df.to_excel(path, index=False, encoding="utf-8-sig")
        result = base64.b64encode(os.fdopen(fd, "rb").read())
        attachment = self.env['ir.attachment'].create({
            'name': "danh_sach_sinh_vien.xlsx",
            'store_fname': 'dssv.xlsx',
            'datas': result
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % (attachment.id),
            'target': 'self',
        }