import base64
from email.policy import default
import os
import tempfile
from datetime import datetime, timedelta
import json
import pandas as pd
from odoo import fields, models, api
from odoo.exceptions import ValidationError


class LopTinChiImportWizard(models.TransientModel):
    _name = 'lop_tin_chi.import_wizard'
    _description = "Import lớp tín chỉ"

    _header = {
        "AIS": {
            "lop": [
                "Mã học phần", "Số thứ tự lớp tín chỉ", "Mã giảng viên",
                "Số lượng nhóm thực hành"
            ],
            "sv": [
                "Mã sinh viên", "Mã học phần", "Số thứ tự lớp",
                "Số thứ tự nhóm lớp"
            ]
        },
        "AQ": [
            "NhomHoc",
            "ToHoc",
            "MaMH",
            "TenMH",
            "SoTinChi",
            "MaSV",
            "HoLotSV",
            "TenSV",
            "NgaySinhC",
            "MaLop",
        ]
    }

    import_template = fields.Selection([
        ("AIS", "AISoft"),
        ("AQ", "Anh Quân"),
    ],
                                       "Mẫu template import",
                                       required=True)

    dot_dang_ky_tin_chi_id = fields.Many2one("dot_dang_ky_tin_chi",
                                             "Đợt đăng ký tín chỉ",
                                             compute="_compute_dot_dk")
    ky_nam_hoc_id = fields.Many2one("ky_nam_hoc", "Kỳ học")
    so_tt_dk = fields.Integer("Số thứ tự đợt đăng ký tín chỉ", default=1)
    file_import = fields.Binary("File excel import (danh sách lớp)")
    file_import_sv = fields.Binary(
        "File excel import (danh sách sinh viên trong lớp)")
    file_import_aq = fields.Binary("File excel import Anh Quân")
    batch_limit = fields.Integer("Giới hạn dòng trong một đợt", default=0)
    noti_html = fields.Text()
    @api.depends("ky_nam_hoc_id", "so_tt_dk")
    def _compute_dot_dk(self):
        for record in self:
            if record.ky_nam_hoc_id and record.so_tt_dk:
                record.dot_dang_ky_tin_chi_id = self.env[
                    "dot_dang_ky_tin_chi"].search([
                        ("ky_hoc_id", "=", record.ky_nam_hoc_id.id),
                        ("so_thu_tu_dot", "=", record.so_tt_dk),
                    ]).id
            else:
                record.dot_dang_ky_tin_chi_id = False,

    def process_sv(self, data):
        map_lop = {}
        for _, record in enumerate(data):
            maSv = record.get("Mã sinh viên")
            maHocPhan = record.get("Mã học phần")
            soThuTuLop = record.get("Số thứ tự lớp")
            soThuTuNhom = record.get("Số thứ tự nhóm lớp")
            print("HIHIHIHi", maSv, maHocPhan, soThuTuLop, soThuTuNhom)
            if map_lop.get(maHocPhan) == None:
                map_lop[maHocPhan] = {}
            if map_lop[maHocPhan].get(soThuTuLop) == None:
                map_lop[maHocPhan][soThuTuLop] = {
                    "nhom_lop": {},
                    "dssv": [],
                }
            if maSv != None:
                map_lop[maHocPhan][soThuTuLop]["dssv"].append(maSv)

            if soThuTuNhom != "":
                soThuTuNhom = int(soThuTuNhom)
                if map_lop[maHocPhan][soThuTuLop]["nhom_lop"].get(
                        soThuTuNhom) == None:
                    map_lop[maHocPhan][soThuTuLop]["nhom_lop"][
                        soThuTuNhom] = []
                if maSv != None:
                    map_lop[maHocPhan][soThuTuLop]["nhom_lop"][
                        soThuTuNhom].append(maSv)
        print("HOHOHO", map_lop)
        for hp in map_lop:
            hoc_phan = self.env["slide.channel"].search([("ma_hoc_phan_moi",
                                                          "=", hp)])
            for so_thu_tu_lop in map_lop[hp]:
                lop_tin_chi = self.env["lop_tin_chi"].search([
                    ("mon_hoc_ids", "=", hoc_phan.id),
                    ("so_thu_tu_lop", "=", so_thu_tu_lop),
                    ("dot_dk_tin_chi_id", "=", self.dot_dang_ky_tin_chi_id.id)
                ])
                if len(lop_tin_chi) > 1:
                    raise ValidationError("Lớp tin chỉ %s đã tồn tại" %
                                          lop_tin_chi[1].ma_lop)
                sinh_vien_ids = self.env["sinh_vien"].search([
                    ("ma_dinh_danh", "in", map_lop[hp][so_thu_tu_lop]["dssv"])
                ])
                lop_tin_chi.write(
                    {"sinh_vien_ids": sinh_vien_ids.mapped("id")})
                for nl in map_lop[hp][so_thu_tu_lop]["nhom_lop"]:
                    nhom = self.env["nhom_lop_tin_chi"].search([
                        ("ma_lop_tin_chi_id", "=", lop_tin_chi.id),
                        ("loai_nhom_lop", "=", "TH"),
                        ("so_thu_tu_nhom", "=", nl)
                    ])
                    sinh_vien_ids_ = self.env["sinh_vien"].search([
                        ("ma_dinh_danh", "in",
                         map_lop[hp][so_thu_tu_lop]["nhom_lop"][nl])
                    ])
                    print("HEHEHE", map_lop[hp][so_thu_tu_lop]["nhom_lop"][nl])
                    nhom.write({"sinh_vien_ids": sinh_vien_ids_.mapped("id")})
                print("created lop", lop_tin_chi, "nhom lop:",
                      list(map_lop[hp][so_thu_tu_lop]["nhom_lop"].keys()))

    def process(self, data):
        if self.import_template == "AIS":
            for i, record in enumerate(data):
                if record["Số thứ tự lớp tín chỉ"] is False:
                    raise ValidationError(
                        f"Số thứ tự học phần rỗng, tại dòng thứ {i+1}")
                mhp = record["Mã học phần"]
                mgv = record["Mã giảng viên"]
                hoc_phan = self.env["slide.channel"].search(
                    [["ma_hoc_phan_moi", "=", mhp]])
                giang_vien = self.env["nhan_vien"].search(
                    [["ma_dinh_danh", "=", mgv]])
                if hoc_phan.id is False:
                    raise ValidationError(
                        f"Không tìm thấy môn học mã {mhp}, tại dòng thứ {i+1}")
                data_lop_tin_chi = {
                    "mon_hoc_ids": hoc_phan.id,
                    "giang_vien_id": giang_vien.id,
                    "giang_vien_ids": [giang_vien.id],
                    "so_thu_tu_lop": record["Số thứ tự lớp tín chỉ"],
                    "dot_dk_tin_chi_id": self.dot_dang_ky_tin_chi_id.id,
                }
                id_lop_tin_chi = self.env["lop_tin_chi"].create(
                    data_lop_tin_chi)
                list_data_nhom_lop_tin_chi = []
                for i in range(int(record["Số lượng nhóm thực hành"])):
                    data_nhom_lop_tin_chi = {
                        "ma_lop_tin_chi_id": id_lop_tin_chi.id,
                        "loai_nhom_lop": "TH",
                        "so_thu_tu_nhom": i + 1,
                    }
                    list_data_nhom_lop_tin_chi.append(data_nhom_lop_tin_chi)
                self.env["nhom_lop_tin_chi"].create(list_data_nhom_lop_tin_chi)
        elif self.import_template == "AQ":
            hp = self.env["slide.channel"].search([])
            map_hp = {x.ma_hoc_phan_moi: x.id for x in hp}
            sv = self.env["sinh_vien"].search([])
            map_sv = {x.ma_dinh_danh: x.id for x in sv}
            dictLop = {}
            dictNhom = {}
            report_string = ""
            noti = ""
            for i, record in enumerate(data):
                sttLop = str(record["NhomHoc"])
                if (sttLop) == 0:
                    report_string += f"Số thứ tự lớp sai (rỗng/bằng 0) ở dòng {i+1}\n"
                sttNhom = int(record["ToHoc"])
                maHp = map_hp.get(str(record["MaMH"]))
                tenHocPhan = record["TenMH"]
                if maHp == None:
                    hoc_phan = self.env["slide.channel"].create({
                        "ma_hoc_phan_moi":
                            str(record["MaMH"]),
                        "ten_hoc_phan":
                            tenHocPhan,
                        "hinh_thuc_dao_tao_id":
                            self.ky_nam_hoc_id.hinh_thuc_dao_tao_id.id
                    })
                    maHp = hoc_phan.id
                    print("Tạo HP", maHp)
                    # maHp = str(record["MaMH"])
                    map_hp[str(record["MaMH"])] = hoc_phan.id
                    noti += f"Hệ thống đã tạo mới học phần {tenHocPhan}, mã {record['MaMH']} ở dòng {i + 1}, vui lòng kiểm tra lại thông tin học phần này."
                    noti += "</br>"
                str_lop = f"{maHp}|{sttLop}|{self.dot_dang_ky_tin_chi_id.ky_hoc_id.ma_ky_nam_hoc}"
                if str_lop not in dictLop:
                    dictLop[str_lop] = []
                idSv = map_sv.get(str(record["MaSV"]))
                if idSv == None:
                    sinh_vien = self.env["sinh_vien"].create({
                        "name": str(str(record["HoLotSV"]) + str(record["TenSV"])) ,
                        "ma_dinh_danh": str(record["MaSV"]),
                        "hinh_thuc_dao_tao_id":
                            self.ky_nam_hoc_id.hinh_thuc_dao_tao_id.id,

                    })
                    ho_va_ten =  print(str(str(record["HoLotSV"]) + str(record["TenSV"])))
                    # maHp = str(record["MaMH"])
                    map_sv[str(record["MaSV"])] = sinh_vien.id
                    idSv = sinh_vien.id
                    noti += f"Hệ thống đã tạo mới sinh viên {ho_va_ten}, mã {record['MaSV']} ở dòng {i + 1}, vui lòng kiểm tra lại thông tin sinh viên này."
                    noti += "</br>"


                dictLop[str_lop].append(idSv)
                if sttNhom != 0:
                    str_nhom = f"{str_lop}|{sttNhom}"
                    if str_nhom not in dictNhom:
                        dictNhom[str_nhom] = []
                    dictNhom[str_nhom].append(idSv)
                print("PROC", i, len(data))
            for i, lop in enumerate(dictLop):
                lopArr = lop.split("|")
                print(lopArr)
                ltc = self.env["lop_tin_chi"].search([
                    ("mon_hoc_ids", "=", int(lopArr[0])),
                    ("so_thu_tu_lop", "=", int(lopArr[1])),
                    ("dot_dk_tin_chi_id", "=", self.dot_dang_ky_tin_chi_id.id)
                ])
                svList = dictLop[lop]
                if len(ltc) == 0:
                    ltc = self.env["lop_tin_chi"].create({
                        "mon_hoc_ids":
                        int(lopArr[0]),
                        "so_thu_tu_lop":
                        int(lopArr[1]),
                        "dot_dk_tin_chi_id":
                        self.dot_dang_ky_tin_chi_id.id,
                        "sinh_vien_ids":
                        svList
                    })
                else:
                    ltc.write({"sinh_vien_ids": svList})
                print("LOP", i, len(dictLop))
            print("các cháu dictNhom", dictNhom)
            for j, nhom in enumerate(dictNhom):
                nhomArr = nhom.split("|")
                if int(nhomArr[3]) != 0:
                    svList = dictNhom[nhom]
                    print("các cháu", dictNhom[nhom],svList)
                    ltc = self.env["lop_tin_chi"].search([
                        ("mon_hoc_ids", "=", int(nhomArr[0])),
                        ("so_thu_tu_lop", "=", int(nhomArr[1])),
                        ("dot_dk_tin_chi_id", "=",
                         self.dot_dang_ky_tin_chi_id.id)
                    ])
                    if len(ltc) == 0:
                        ltc = self.env["lop_tin_chi"].create({
                            "mon_hoc_ids":
                            int(lopArr[0]),
                            "so_thu_tu_lop":
                            int(lopArr[1]),
                            "dot_dk_tin_chi_id":
                            self.dot_dang_ky_tin_chi_id.id,
                            "sinh_vien_ids":
                            svList
                        })
                    nhomLtc = self.env["nhom_lop_tin_chi"].search([
                        ("ma_lop_tin_chi_id", "=", ltc.id),
                        ("loai_nhom_lop", "=", "TH"),
                        ("so_thu_tu_nhom", "=", int(nhomArr[3])),
                    ])
                    if len(nhomLtc) == 0:
                        nhomLtc = self.env["nhom_lop_tin_chi"].create({
                            "ma_lop_tin_chi_id":
                            ltc.id,
                            "so_thu_tu_nhom":
                            int(nhomArr[3]),
                            "loai_nhom_lop":
                            "TH",
                            "sinh_vien_ids":
                            svList
                        })
                    else:
                        nhomLtc.write({"sinh_vien_ids": svList})
                print("NHOM", i, len(dictNhom))
            self.noti_html = noti
            return report_string

    def import_lop_tin_chi(self):
        if self.ky_nam_hoc_id is False:
            raise ValidationError("Chưa nhập kỳ học.")
        if self.so_tt_dk == 0:
            raise ValidationError(
                "Số thứ tự đợt đăng ký tín chỉ phải lớn hơn 0.")
        if self.dot_dang_ky_tin_chi_id.id is False:
            raise ValidationError("Chưa có đợt đăng ký tín chỉ.")

        if self.import_template == "AIS":
            if self.file_import and self.file_import_sv:
                fd, path = tempfile.mkstemp()
                with os.fdopen(fd, "wb") as tmp:
                    tmp.write(base64.decodebytes(self.file_import))
                try:
                    df = pd.read_excel(path, dtype=str)
                except:
                    raise ValidationError("Lỗi file excel.")
                df.fillna(0, inplace=True)
                if set(self._header["AIS"]["lop"]) != set(df.columns):
                    raise ValidationError("Không khớp header")
                data = df.to_dict("records")
                self.process(data)

                fd, path = tempfile.mkstemp()
                with os.fdopen(fd, "wb") as tmp:
                    tmp.write(base64.decodebytes(self.file_import_sv))
                try:
                    df = pd.read_excel(path, dtype=str)
                except:
                    raise ValidationError("Lỗi file excel.")
                df.fillna("", inplace=True)
                if set(self._header["AIS"]["sv"]) != set(df.columns):
                    raise ValidationError("Không khớp header")
                data = df.to_dict("records")
                self.process_sv(data)
            else:
                raise ValidationError("Chưa có file excel.")
            res = {'type': 'ir.actions.client', 'tag': 'reload'}
            return res
        elif self.import_template == "AQ":
            if self.file_import_aq:
                fd, path = tempfile.mkstemp()
                with os.fdopen(fd, "wb") as tmp:
                    tmp.write(base64.decodebytes(self.file_import_aq))
                try:
                    df = pd.read_excel(path, dtype=str)
                except:
                    raise ValidationError("Lỗi file excel.")
                df.fillna(0, inplace=True)
                if set(self._header["AQ"]) != set(df.columns):
                    raise ValidationError("Không khớp header")
                data = df.to_dict("records")
                report = self.process(data)
                so_dong = len(data)
                if report:
                    raise ValidationError(report)
                vls = f"<H4><B>Hệ thống đã import thành công {so_dong} dòng dữ liệu bản ghi sinh viên lớp tín chỉ.</br></B></H4>"
                if self.noti_html:
                    vls += "<I>Lưu ý các chú ý dưới đây</br></I>"
                    vls += str(self.noti_html)
                id_thong_bao = self.env["custom_noti"].create({
                    "noti_html": vls,
                })

                return {
                    'name': 'Thông báo hệ thống',
                    'type': 'ir.actions.act_window',
                    'res_model': 'custom_noti',
                    'view_mode': 'form',
                    'res_id': id_thong_bao.id,
                    'view_type': 'form',
                    'target': 'new',
                }
            else:
                raise ValidationError("Chưa có file excel.")
            res = {'type': 'ir.actions.client', 'tag': 'reload'}
            return res

    def get_header(self):
        fd, path = tempfile.mkstemp(suffix='.xlsx')
        if self.import_template == "AIS":
            columns = self._header["AIS"]["lop"]
        elif self.import_template == "AQ":
            columns = self._header["AQ"]
        import_template = pd.DataFrame(columns=columns)
        import_template.to_excel(path, index=False)
        result = base64.b64encode(os.fdopen(fd, "rb").read())
        attachment = self.env['ir.attachment'].create({
            'name': "mau_import_lop_tin_chi.xlsx",
            'store_fname': 'test.xlsx',
            'datas': result
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % (attachment.id),
            'target': 'self',
        }

    def get_header_sv(self):
        fd, path = tempfile.mkstemp(suffix='.xlsx')
        import_template = pd.DataFrame(columns=self._header["AIS"]["sv"])
        import_template.to_excel(path, index=False)
        result = base64.b64encode(os.fdopen(fd, "rb").read())
        attachment = self.env['ir.attachment'].create({
            'name': "mau_import_sinh_vien_lop_tin_chi.xlsx",
            'store_fname': 'test.xlsx',
            'datas': result
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % (attachment.id),
            'target': 'self',
        }


class TKBImportWizard(models.TransientModel):
    _name = "tkb.import_wizard"
    _description = "Import thời khóa biểu"

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
            # "Hình thức học",
        ],
        "AQ": [
            # "MaMH",
            "TenMH",
            # "NhomTo",
            # "ToTH",
            # "TenLop",
            # "TongSoSV",
            # "ThuKieuSo",
            # "TietBD",
            # "SoTiet",
            # "MaPH",
            # "DSTuanHoc",
            # "TuanBD",
            "MaNV",
            "TenDayDuNV",
            # "IsTKBDaXep",
            # "MaDV",
            # "TenDV",
            # "TenDVEg",
            # "TenPH",
            # "MaTCPhong",
            # "NgayBD",
            # "NgayKT",
            # "TuanKT",
            # "TenToHop",
            # "DSTiet",
            # "HasToTH",
            # "SucChuaPH",
            # "SiSoCPDK",
            # "SiSoDDK",
            # "SoTinChi",
            # "MaLop",
            # "TenNV",
            # "TongTC",
            # "GhiChu",
            # "GioHoc",
            # "ThuTuTG",
            # "GioBD",
            # "SoPhut",
            # "MaUser",
            # "NHHK",
            # "PhutBD",
            # "NgayBDHK",
            # "TuanBDHK",
            # "TuanHoc",
            # "NgayBatDau",
            # "NgayKetThuc",
            # "HinhThucHoc",
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
    _optional = {
        "AIS": ["Số thứ tự nhóm lớp"],
        "AQ": ["HinhThucHoc"],
        "PTTC1": ["HinhThucHoc"],
    }
    hinh_thuc_dao_tao_id = fields.Many2one(
        comodel_name="hinh_thuc_dao_tao",
        string="Hình thức đào tạo",
        default= lambda self: self.env.user.hinh_thuc_dao_tao_id
    )
    import_template = fields.Selection(
        string="Mẫu import",
        selection=[("AQ", "Anh Quân"), ("AIS", "A.I.Soft"),
                   ("PTTC1", "Trung tâm đào tạo bưu chính viễn thông 1")],
        required=True,
        default="AQ")
    file_import = fields.Binary("File csv import")
    batch_limit = fields.Integer("Giới hạn dòng trong một đợt", default=0)
    su_dung_template_tiet_hoc = fields.Boolean("Sử dụng template tiết học?",
                                               default=False)
    #### của PTTC1
    start_line = fields.Integer("Dòng bắt đầu nhập", default=0)
    template_tiet_hoc_id = fields.Many2one(
        comodel_name="danh_muc.template_tiet_hoc",
        string="Nhóm thời gian tiết học",
    )
    ky_nam_hoc_id = fields.Many2one(
        comodel_name="ky_nam_hoc",
        string="Kỳ năm học",
    )
    ######
    start_day = fields.Date("Ngày bắt đầu")
    end_day = fields.Date("Ngày kết thúc")
    noti_html = fields.Text()
    so_ban_ghi_import = fields.Integer()

    def createNgay(self, tuan, ngayBd, thuKieuSo):
        week = timedelta(weeks=tuan)
        dateBD = ngayBd + week
        weekday = timedelta(days=thuKieuSo - dateBD.weekday() - 2)
        dateBD = dateBD + weekday
        return dateBD

    def procNgay(self, dsTuan, ngayBd, thuKieuSo):
        res = [
            self.createNgay(i, ngayBd, thuKieuSo)
            for i, tuan in enumerate(dsTuan) if tuan != "-"
        ]
        return res

    def createNgay2(self, tuan, ngayBd, thuKieuSo, gioBd, gioKt):
        week = timedelta(weeks=tuan)
        dateBD = ngayBd + week
        weekday = timedelta(days=thuKieuSo - dateBD.weekday() - 2)
        dateBD = dateBD + weekday
        gio = gioBd.split(":")
        gioBD = dateBD + timedelta(hours=int(gio[0])) + timedelta(
            minutes=int(gio[1]))
        gio = gioKt.split(":")
        gioKT = dateBD + timedelta(hours=int(gio[0])) + timedelta(
            minutes=int(gio[1]))
        return (dateBD, gioBD, gioKT)

    def procNgay2(self, dsTuan, ngayBd, thuKieuSo, gioBd, gioKt):
        res = [
            self.createNgay2(i, ngayBd, thuKieuSo, gioBd, gioKt)
            for i, tuan in enumerate(dsTuan) if tuan != "-"
        ]
        return res

    def process(self, data):
        selected_header = self._header[self.import_template]
        hinhThuc = "" \
            if (self.hinh_thuc_dao_tao_id.ten_hinh_thuc_dao_tao_viet_tat == "CQ") \
            else "-" + self.hinh_thuc_dao_tao_id.ten_hinh_thuc_dao_tao_viet_tat
        selected_header_optional = self._optional[self.import_template]
        report_string = ""
        noti = ""
        if self.import_template == "AIS":
            for i, record in enumerate(data):
                for h in list(
                        set(selected_header) - set(selected_header_optional)):
                    if h not in record:
                        report_string += f"Thiếu trường {h} ở dòng {i+1}\n"
                        continue
                lopTinChi = ""
                nhomLopTinChi = ""
                maHocPhan = record["Mã học phần"]
                maKyHoc = record["Mã kỳ học"]
                soThuTuLop = str(record["Số thứ tự lớp"]).zfill(2)
                lopTinChi = f"{maHocPhan}-{maKyHoc}-{soThuTuLop}"
                soThuTuNhomLop = str(record["Số thứ tự nhóm lớp"]).zfill(2)
                nhomLopTinChi = f"{lopTinChi}-{soThuTuNhomLop}-TH"
                ngayBatDau = pd.to_datetime(record["Từ ngày"])
                ngayKetThuc = pd.to_datetime(record["Đến ngày"])
                thuKieuSo = int(record["Thứ kiểu số"])
                if thuKieuSo > 8 or thuKieuSo < 2:
                    report_string += f"Thứ kiểu số không nằm trong ngưỡng 2 - 8 ({thuKieuSo}) ở dòng {i+1}\n"
                tietBatDau = int(record["Tiết bắt đầu"])
                tietKetThuc = int(record["Tiết kết thúc"])
                taiKhoanGV = record["Tài khoản GV"]
                matKhauGV = record["Mật khẩu GV"]
                idZoom = record["ID Zoom"]
                phongHoc = str(record["Phòng học"])
                if len(phongHoc) == 0:
                    phongHoc = idZoom
                matKhauZoom = record["Mật khẩu Zoom"]

                lop_tin_chi_id = self.env["lop_tin_chi"].search(
                    [("ma_lop", "=", lopTinChi)], limit=1)
                if len(lop_tin_chi_id) == 0:
                    report_string += f"Không có lớp tín chỉ {lopTinChi} ở dòng {i+1}\n"
                nhom_lop_tin_chi_id = self.env["nhom_lop_tin_chi"].search(
                    [("ma_nhom_lop_tin_chi", "=", nhomLopTinChi)], limit=1)
                print(nhom_lop_tin_chi_id, nhomLopTinChi)
                tiet_bat_dau_id = self.env["danh_muc.tiet_hoc"].search([
                    ("tiet_hoc", "=", tietBatDau),
                    ("hinh_thuc_dao_tao_id", "=", self.hinh_thuc_dao_tao_id.id)
                ])
                if len(tiet_bat_dau_id) == 0:
                    report_string += f"Không có tiết học {tietBatDau}-{self.hinh_thuc_dao_tao_id.ten_hinh_thuc_dao_tao} ở dòng {i+1}\n"
                tiet_ket_thuc_id = self.env["danh_muc.tiet_hoc"].search(
                    [("tiet_hoc", "=", tietKetThuc),
                     ("hinh_thuc_dao_tao_id", "=",
                      self.hinh_thuc_dao_tao_id.id)],
                    limit=1,
                )
                if len(tiet_ket_thuc_id) == 0:
                    report_string += f"Không có tiết học {tietKetThuc}-{self.hinh_thuc_dao_tao_id.ten_hinh_thuc_dao_tao} ở dòng {i+1}\n"
                dayUntil = thuKieuSo - 2 - ngayBatDau.weekday()
                if dayUntil < 0:
                    dayUntil += 7
                dayList = []
                ngayBatDau += timedelta(days=dayUntil)
                while ngayBatDau <= ngayKetThuc:
                    dayList.append(ngayBatDau)
                    ngayBatDau += timedelta(days=7)
                buoiHoc = [{
                    "lop_tin_chi_id": lop_tin_chi_id.id,
                    "nhom_lop_tin_chi_id": nhom_lop_tin_chi_id.id,
                    "ngay_bd": ngayHoc,
                    "tiet_bd": tiet_bat_dau_id.id,
                    "tiet_kt": tiet_ket_thuc_id.id,
                    "tai_khoan": taiKhoanGV,
                    "mat_khau": matKhauGV,
                    "phong_hoc": phongHoc,
                    "id_zoom": idZoom,
                    "mat_khau_1": matKhauZoom,
                } for ngayHoc in dayList]
                self.env["buoi_hoc"].create(buoiHoc)
            return report_string
        elif self.import_template == 'AQ':
            template_tiet_hoc = self.env["danh_muc.template_tiet_hoc"].search(
                [])
            map_template_tiet_hoc = {
                x.ma_template_tiet_hoc:
                {y.tiet_hoc: y.id
                 for y in x.tiethoc_id}
                for x in template_tiet_hoc
            }
            nv = self.env["nhan_vien"].search([])
            ma_gv_moi = open(os.path.dirname(__file__) + "/magvmoi.json", encoding="utf-8")
            ma_gv_moi_Json = json.load(ma_gv_moi)
            print(ma_gv_moi_Json)
            map_ma_gv_moi = {}
            for x in ma_gv_moi_Json:
                if x.get('maSv') and x.get('maCanBo'):
                    map_ma_gv_moi[str(x.get('maSv'))] = str(x.get('maCanBo'))
            print(map_ma_gv_moi)
            map_nhan_vien = {x.ma_dinh_danh: x.id for x in nv}
            dot_dk_all = self.env["dot_dang_ky_tin_chi"].search([])
            map_dot_dang_ky = {
                f"{x.ky_hoc_id.ma_ky_nam_hoc}|{x.so_thu_tu_dot}": x.id
                for x in dot_dk_all
            }
            hoc_phan_all = self.env["slide.channel"].search([])
            map_hoc_phan = {x.ma_hoc_phan_moi: x.id for x in hoc_phan_all}
            lop_tin_chi_set = set()
            buoi_hoc_list = []
            for i, record in enumerate(data):
                for h in list(
                        set(selected_header) - set(selected_header_optional)):
                    if h not in record:
                        report_string += f"Thiếu trường {h} ở dòng {i+1}\n"
                        continue
                lopTinChi = ""
                nhomLopTinChi = ""
                maHocPhan = record["MaMH"]
                tenHocPhan = str(record["TenMH"])
                maKyHoc = record["NHHK"]
                soThuTuLop = str(record["NhomTo"]).zfill(2)

                lopTinChi = f"{maHocPhan}-{maKyHoc}{hinhThuc}-{soThuTuLop}"
                lop_tin_chi_set.add(lopTinChi)
                soThuTuNhomLop = str(record["ToTH"]).zfill(2)
                nhomLopTinChi = f"{lopTinChi}-{soThuTuNhomLop}-TH"
                ngayBd = pd.to_datetime(record["NgayBDHK"])
                ngayBd.replace(hour=0, minute=0, microsecond=0)
                dsTuan = record["DSTuanHoc"]
                maGv = str(record["MaNV"])
                tenNv = str(record["TenDayDuNV"])
                gv = map_nhan_vien.get(map_ma_gv_moi.get(maGv))
                if gv == None:
                    gv = map_nhan_vien.get(maGv)
                if gv == None:
                    gv = self.env["nhan_vien"].create({
                        "name": tenNv,
                        "ma_dinh_danh": maGv
                    })
                    gv = gv.id
                    map_ma_gv_moi[maGv] = maGv
                    map_nhan_vien[maGv] = gv
                    noti += f"Hệ thống đã tạo mới giảng viên {tenNv}, mã {maGv} ở dòng {i+1}, vui lòng kiểm tra lại thông tin giảng viên này."
                    noti += "</br>"
                thuKieuSo = int(record["ThuKieuSo"])
                if thuKieuSo > 8 or thuKieuSo < 2:
                    report_string += f"Thứ kiểu số không nằm trong ngưỡng 2 - 8 ({thuKieuSo}) ở dòng {i+1}\n"
                tietBatDau = int(record["TietBD"])
                tietKetThuc = int(record["TietBD"]) + int(record["SoTiet"]) - 1
                phongHoc = str(record["MaPH"])
                idZoom = phongHoc
                lop_tin_chi_id = self.env["lop_tin_chi"].search(
                    [("ma_lop", "=", lopTinChi)], limit=1)
                try:
                    hoc_phan = map_hoc_phan.get(str(maHocPhan))
                    if hoc_phan == None:
                        hoc_phan = self.env["slide.channel"].create({
                            "ma_hoc_phan_moi":
                            str(maHocPhan),
                            "ten_hoc_phan":
                            tenHocPhan,
                            "hinh_thuc_dao_tao_id":
                            self.hinh_thuc_dao_tao_id.id
                        })
                        print(len(lop_tin_chi_id))
                        hoc_phan = hoc_phan.id
                        map_hoc_phan[str(maHocPhan)] = hoc_phan
                        noti += f"Hệ thống đã tạo mới học phần {tenHocPhan}, mã {maHocPhan} ở dòng {i+1}, vui lòng kiểm tra lại thông tin học phần này."
                        noti += "</br>"
                    if len(lop_tin_chi_id) == 0:
                        lop_tin_chi_id = self.env["lop_tin_chi"].create({
                            "dot_dk_tin_chi_id":
                            map_dot_dang_ky[f"{maKyHoc}|1"],
                            "mon_hoc_ids":
                            hoc_phan,
                            "so_thu_tu_lop":
                            soThuTuLop,
                            "giang_vien_id":
                            gv,
                            "giang_vien_ids": [gv],
                        })
                        # print(f"Tạo lớp {map_hoc_phan[str(maHocPhan}")
                        noti += f"Hệ thống đã tạo mới lớp tín chỉ {lopTinChi} ở dòng {i+1}, vui lòng import danh sách sinh viên cho lớp tín chỉ này."
                        noti += "</br>"
                except Exception as e:
                    print(e)
                    try:
                        print(map_hoc_phan[str(maHocPhan)])
                    except:
                        report_string += f"[!] Hệ thống tự động tạo lớp tín chỉ {lopTinChi} ở dòng {i+1} không thành công do môn học {str(maHocPhan)} chưa tồn tại trên hệ thống!\n"
                    try:
                        print(map_dot_dang_ky[f"{maKyHoc}|1"])
                    except:
                        report_string += f"[!] Không có kỳ học {maKyHoc} trong hệ thống ở dòng {i+1} hoặc chưa có đợt đăng ký cho kỳ {maKyHoc} !\n"
                nhom_lop_tin_chi_id = self.env["nhom_lop_tin_chi"].search(
                    [("ma_nhom_lop_tin_chi", "=", nhomLopTinChi)], limit=1)
                if soThuTuNhomLop != "00" and len(nhom_lop_tin_chi_id) == 0:
                    nhom_lop_tin_chi_id = self.env["nhom_lop_tin_chi"].create({
                        "ma_lop_tin_chi_id":
                        lop_tin_chi_id.id,
                        "so_thu_tu_nhom":
                        int(soThuTuNhomLop),
                        "loai_nhom_lop":
                        "TH",
                    })
                    print(
                        f"Tạo nhóm lớp {map_hoc_phan[str(maHocPhan)]} - {int(soThuTuNhomLop)}"
                    )
                if self.su_dung_template_tiet_hoc == True:
                    tiet_bat_dau_id = map_template_tiet_hoc.get(
                        str(record.get("HinhThucHoc"))).get(tietBatDau)

                    if tiet_bat_dau_id == None:
                        report_string += f"Không có tiết học {tietBatDau}-{self.hinh_thuc_dao_tao_id.ten_hinh_thuc_dao_tao} ở dòng {i+1}\n"
                    tiet_ket_thuc_id = map_template_tiet_hoc.get(
                        str(record.get("HinhThucHoc"))).get(tietKetThuc)
                    if tiet_ket_thuc_id == None:
                        report_string += f"Không có tiết học {tietKetThuc}-{self.hinh_thuc_dao_tao_id.ten_hinh_thuc_dao_tao} ở dòng {i+1}\n"
                    dayList = self.procNgay(dsTuan, ngayBd, thuKieuSo)
                    if self.start_day:
                        dayList = [x for x in dayList if x >= self.start_day]
                    if self.end_day:
                        dayList = [x for x in dayList if x <= self.end_day]
                    buoiHoc = [{
                        "lop_tin_chi_id": lop_tin_chi_id.id,
                        "nhom_lop_tin_chi_id": nhom_lop_tin_chi_id.id,
                        "ngay_bd": ngayHoc,
                        "tiet_bd": tiet_bat_dau_id,
                        "tiet_kt": tiet_ket_thuc_id,
                        "phong_hoc": phongHoc,
                        "id_zoom": idZoom,
                    } for ngayHoc in dayList]

                    buoi_hoc_list += buoiHoc
                else:
                    gioBd = str(record["GioHoc"]).split(" - ")[0]
                    gio_bat_dau = gioBd.split(":")[0]
                    phut_bat_dau = gioBd.split(":")[1]
                    quy_ra_phut_khi_ket_thuc = int(gio_bat_dau)*60 + int(phut_bat_dau) + (int(record["SoTiet"])*60)
                    gioKt = str(str(((quy_ra_phut_khi_ket_thuc)//60)%24) + ":" + str((quy_ra_phut_khi_ket_thuc)%60))
                    # gioKt = str(record["GioHoc"]).split(" - ")[1]
                    dayList = self.procNgay2(dsTuan, ngayBd, thuKieuSo, gioBd,
                                             gioKt)
                    if (self.start_day):
                        dayList = [
                            x for x in dayList if x[0] >= self.start_day
                        ]
                    if (self.end_day):
                        dayList = [x for x in dayList if x[0] <= self.end_day]
                    buoiHoc = [{
                        "lop_tin_chi_id": lop_tin_chi_id.id,
                        "nhom_lop_tin_chi_id": nhom_lop_tin_chi_id.id,
                        "ngay_bd": ngayHoc[0],
                        "tiet_bd_so": tietBatDau,
                        "tiet_kt_so": tietKetThuc,
                        "ngay_gio_hoc": ngayHoc[1],
                        "ngay_gio_ket_thuc": ngayHoc[2],
                        "phong_hoc": phongHoc,
                        "id_zoom": idZoom,
                    } for ngayHoc in dayList]
                    buoi_hoc_list += buoiHoc
            lop_tin_chi_ids = self.env["lop_tin_chi"].search([
                ("ma_lop", "in", list(lop_tin_chi_set))
            ]).mapped("id")
            domain = [("lop_tin_chi_id", "in", lop_tin_chi_ids)]
            if self.start_day:
                domain.append(("ngay_bd", ">=", self.start_day))
            if self.end_day:
                domain.append(("ngay_bd", "<=", self.end_day))
            lich_hoc_lop_delete = self.env["buoi_hoc"].search(domain)
            print("so luong lich hoc phai xoa: ",
                  len(lich_hoc_lop_delete.mapped("id")), i, len(data))
            lich_hoc_lop_delete.unlink()
            # self.env["buoi_hoc"].create(buoi_hoc_list)
            tmp = len(buoi_hoc_list)
            if len(report_string) > 0:
                raise ValidationError(report_string)
            self.so_ban_ghi_import = len(buoi_hoc_list)
            self.env["buoi_hoc"].create(buoi_hoc_list)
            # for i, bh in enumerate(buoi_hoc_list):
            #     print(i, tmp)
            #     self.env["buoi_hoc"].create(bh)
            self.noti_html = noti
            return report_string
        elif self.import_template == "PTTC1":
            nv = self.env["nhan_vien"].search([])
            map_nhan_vien = {x.ma_dinh_danh: x.id for x in nv}
            hoc_phan_all = self.env["slide.channel"].search([])
            map_hoc_phan = {x.ma_hoc_phan_moi: x.id for x in hoc_phan_all}
            for i, record in enumerate(data):
                for h in list(
                        set(selected_header) - set(selected_header_optional)):
                    if h not in record:
                        report_string += f"Thiếu trường {h} ở dòng {i+1}\n"
                        continue
                lopTinChi = ""
                nhomLopTinChi = ""
                siSo = record["Sĩ số từng nhóm"]
                tenHocPhan = record["Tên môn học"]
                maHocPhan = record["Mã học phần"]
                STTDKTC = record["Số thứ tự đợt đăng ký tín chỉ"]
                maGv = record["Mã giảng viên"]
                tenGv = record["Giảng viên"]
                soThuTuLop = str(record["Nhóm lớp môn học"]).zfill(2)
                lopTinChi = f"{maHocPhan}-{self.ky_nam_hoc_id.ma_ky_nam_hoc}-{soThuTuLop}"
                soThuTuNhomLop = 1  # đoạn này mình đang để default cho họ là 1
                nhomLopTinChi = f"{lopTinChi}-{soThuTuNhomLop}-TH"
                ngayBatDau = pd.to_datetime(record["Ngày"])
                thuKieuSo = int(record["Thứ"])
                if thuKieuSo > 8 or thuKieuSo < 2:
                    report_string += f"Thứ kiểu số không nằm trong ngưỡng 2 - 8 ({thuKieuSo}) ở dòng {i+1}\n"
                tietBatDau = int(record["Tiết bắt đầu (*)"])
                soTiet = int(record["Số tiết"])
                tietKetThuc = int(tietBatDau + soTiet - 1)
                taiKhoanGV = record["Tài khoản"]
                matKhauGV = record["Mật khẩu"]
                idZoom = record["ID phòng học"]
                tongSoTietHoc = int(record["Tổng số tiết học"])
                phongHoc = idZoom
                if len(phongHoc) == 0:
                    phongHoc = idZoom
                matKhauZoom = record["Mật khẩu Zoom"]

                hoc_phan = map_hoc_phan.get(maHocPhan)
                if hoc_phan == None:
                    hoc_phan = self.env["slide.channel"].create({
                        "ma_hoc_phan_moi":
                            str(maHocPhan),
                        "ten_hoc_phan":
                            tenHocPhan,
                        "hinh_thuc_dao_tao_id":
                            self.hinh_thuc_dao_tao_id.id
                    })
                    hoc_phan = hoc_phan.id
                    map_hoc_phan[str(maHocPhan)] = hoc_phan
                    noti += f"Hệ thống đã tạo mới học phần {tenHocPhan}, mã {maHocPhan} ở dòng {i + 1}, vui lòng kiểm tra lại thông tin học phần này."
                    noti += "</br>"
                gv = map_nhan_vien.get(maGv)
                if gv == None:
                    gv = self.env["nhan_vien"].create({
                        "name": tenGv,
                        "ma_dinh_danh": maGv
                    })
                    gv = gv.id
                    map_nhan_vien[maGv] = gv
                    noti += f"Hệ thống đã tạo mới giảng viên {tenGv}, mã {maGv} ở dòng {i + 1}, vui lòng kiểm tra lại thông tin giảng viên này."
                    noti += "</br>"
                lop_tin_chi_id = self.env["lop_tin_chi"].search(
                    [("ma_lop", "=", lopTinChi)], limit=1)
                dot_dk = self.env["dot_dang_ky_tin_chi"].search([('ky_hoc_id', '=', self.ky_nam_hoc_id.id), ('so_thu_tu_dot', '=', int(STTDKTC))])
                if len(lop_tin_chi_id) == 0:
                    lop_tin_chi_id = self.env["lop_tin_chi"].create({
                        "dot_dk_tin_chi_id":
                            dot_dk.id,
                        "mon_hoc_ids":
                            hoc_phan,
                        "so_thu_tu_lop":
                            soThuTuLop,
                        "si_so":
                            siSo,
                        "giang_vien_id":
                            gv,
                        "giang_vien_ids": [gv],
                    })
                    noti += f"Hệ thống đã tạo mới lớp tín chỉ {lopTinChi} ở dòng {i + 1}, vui lòng import danh sách sinh viên cho lớp tín chỉ này."
                    noti += "</br>"
                nhom_lop_tin_chi_id = self.env["nhom_lop_tin_chi"].search(
                    [("ma_nhom_lop_tin_chi", "=", nhomLopTinChi)], limit=1)

                if len(nhom_lop_tin_chi_id) == 0:
                    nhom_lop_tin_chi_id = self.env["nhom_lop_tin_chi"].create({
                        "ma_lop_tin_chi_id":
                        lop_tin_chi_id.id,
                        "so_thu_tu_nhom":
                        int(soThuTuNhomLop),
                        "loai_nhom_lop":
                        "TH",
                        "si_so":
                            siSo,
                    })
                print(nhom_lop_tin_chi_id, nhomLopTinChi)
                tiet_bat_dau_id = self.env["danh_muc.tiet_hoc"].search([
                    ("tiet_hoc", "=", tietBatDau),
                    ("hinh_thuc_dao_tao_id", "=",
                     self.hinh_thuc_dao_tao_id.id),
                    ("template_tiet_hoc_id", "=",
                     self.template_tiet_hoc_id.id),
                ])
                if len(tiet_bat_dau_id) == 0:
                    report_string += f"Không có tiết học {tietBatDau}-{self.hinh_thuc_dao_tao_id.ten_hinh_thuc_dao_tao} ở dòng {i+1}\n"
                    raise ValidationError(
                        f"Không có tiết học {tietBatDau}-{self.hinh_thuc_dao_tao_id.ten_hinh_thuc_dao_tao} ở dòng {i+1}\n"
                    )
                tiet_ket_thuc_id = self.env["danh_muc.tiet_hoc"].search(
                    [("tiet_hoc", "=", tietKetThuc),
                     ("hinh_thuc_dao_tao_id", "=",
                      self.hinh_thuc_dao_tao_id.id)],
                    limit=1,
                )
                if len(tiet_ket_thuc_id) == 0:
                    report_string += f"Không có tiết học {tietKetThuc}-{self.hinh_thuc_dao_tao_id.ten_hinh_thuc_dao_tao} ở dòng {i+1}\n"
                    raise ValidationError(
                        f"Không có tiết học {tietKetThuc}-{self.hinh_thuc_dao_tao_id.ten_hinh_thuc_dao_tao} ở dòng {i+1}"
                    )

                self.env["buoi_hoc"].create({
                    "lop_tin_chi_id":
                    lop_tin_chi_id.id,
                    # "nhom_lop_tin_chi_id":
                    # nhom_lop_tin_chi_id.id,
                    "ngay_bd":
                    ngayBatDau,
                    "tiet_bd":
                    tiet_bat_dau_id.id,
                    "tiet_kt":
                    tiet_ket_thuc_id.id,
                    "tiet_bd_so":
                    tietBatDau,
                    "tiet_kt_so":
                    tietKetThuc,
                    "tai_khoan":
                    taiKhoanGV,
                    "mat_khau":
                    matKhauGV,
                    "phong_hoc":
                    phongHoc,
                    "id_zoom":
                    idZoom,
                    "mat_khau_1":
                    matKhauZoom,
                    "template_tiet_hoc_id":
                    self.template_tiet_hoc_id.id,
                })
            self.noti_html = noti
            return report_string

    def import_tkb(self):
        selected_header = self._header[self.import_template]
        optional_header = self._optional[self.import_template]
        report_string = ""
        so_dong = 0
        if self.hinh_thuc_dao_tao_id.id is False:
            raise ValidationError("Chưa nhập hình thức đào tạo.")
        if self.file_import:
            fd, path = tempfile.mkstemp()
            with os.fdopen(fd, "wb") as tmp:
                tmp.write(base64.decodebytes(self.file_import))
            try:
                df = pd.read_excel(path, dtype=str)
            except:
                raise ValidationError("Lỗi file excel.")
            print(set(df.columns), set(selected_header) - set(optional_header))
            df.fillna(0, inplace=True)
            if set(df.columns) < set(selected_header) - set(optional_header):
                raise ValidationError(
                    f"Không khớp header\n\nHeader gốc: {selected_header}\n\nHeader: {list(df.columns)}"
                )
            data = df.to_dict("records")
            self.so_ban_ghi_import = len(data)
            report_string += self.process(data)
            so_dong = len(data)
        else:
            raise ValidationError("Chưa có file excel.")
        if len(report_string) > 0:
            raise ValidationError(report_string)
        else:
            print(self.noti_html)
            vls = f"<H4><B>Hệ thống đã import thành công {so_dong} dòng dữ liệu ứng với {self.so_ban_ghi_import} bản ghi buổi học.</br></B></H4>"
            if self.noti_html:
                vls += "<I>Lưu ý các chú ý dưới đây</br></I>"
                vls += str(self.noti_html)
            id_thong_bao = self.env["custom_noti"].create({
                "noti_html": vls,
            })

            return {
                'name': 'Thông báo hệ thống',
                'type': 'ir.actions.act_window',
                'res_model': 'custom_noti',
                'view_mode': 'form',
                'res_id': id_thong_bao.id,
                'view_type': 'form',
                'target': 'new',
            }

    def get_header(self):
        fd, path = tempfile.mkstemp(suffix='.xlsx')
        import_template = pd.DataFrame(
            columns=self._header[self.import_template])
        import_template.to_excel(path, index=False)
        result = base64.b64encode(os.fdopen(fd, "rb").read())
        attachment = self.env['ir.attachment'].create({
            'name': "mau_import_tkb.xlsx",
            'store_fname': 'tkb.xlsx',
            'datas': result
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % (attachment.id),
            'target': 'self',
        }


class DiemHocPhanImportWizard(models.TransientModel):
    _name = 'diem_hoc_phan.import_wizard'
    _description = "Import điểm học phần"

    _header = {
        "PTIT": [
            "Mã SV", "Điểm CC", 'Điểm TBKT', 'Điểm TN-TH', 'Điểm BTTL',
            'Điểm\nTHI', 'Điểm\nKTHP', "Học phần"
        ],
    }
    ky_hoc_id = fields.Many2one("ky_nam_hoc", "Kỳ học")
    file_import = fields.Binary("File .xlsx import")
    import_template = fields.Selection(
        [("PTIT", "Học viện Bưu chính Viễn thông")], required=True)

    def switch_diem(self, diem: str):
        try:
            diem = float(diem)
            assert (0 <= diem <= 10)
            if (9 <= diem <= 10):
                return ("4", "A+")
            if (8.5 <= diem <= 8.9):
                return ("3.7", "A")
            if (8 <= diem <= 8.4):
                return ("3.5", "B+")
            if (7 <= diem <= 7.9):
                return ("3", "B")
            if (6.5 <= diem <= 6.9):
                return ("2.5", "C+")
            if (5.5 <= diem <= 6.4):
                return ("2", "C")
            if (5 <= diem <= 5.4):
                return ("1.5", "D+")
            if (4 <= diem <= 4.9):
                return ("1", "D")
            if (diem < 4):
                return ("0", "F")
        except Exception as e:
            return (False, False)

    def process(self, df):
        if (self.import_template == "PTIT"):
            for i, row in df.iterrows():
                maSv = row["Mã SV"]
                if maSv == "":
                    break
                diemChuyenCan = row["Điểm CC"]
                diemTrungBinhKiemTra = row["Điểm TBKT"]
                diemTNTH = row["Điểm TN-TH"]
                diemBTTL = row["Điểm BTTL"]
                diemThi = row["Điểm\nTHI"]
                diemTK = row["Điểm\nKTHP"]
                hocPhan = str(row["Học phần"])
                diemThang4, diemChu = self.switch_diem(str(diemTK))

                sv = self.env["sinh_vien"].search([("ma_dinh_danh", "=",
                                                    str(maSv))])
                if len(sv) == 0:
                    raise ValidationError(
                        f"Không có sinh viên mã {maSv} ở dòng {i+9}")
                hoc_phan = self.env["slide.channel"].search([
                    ("ma_hoc_phan_moi", "=", str(hocPhan))
                ])
                if len(hoc_phan) == 0:
                    raise ValidationError(
                        f"Không có học phần mã {hocPhan} ở dòng {i+9}")
                lop_tin_chi = self.env["lop_tin_chi"].search([
                    ("sinh_vien_ids", "in", sv.id),
                    ("mon_hoc_ids", "=", hoc_phan.id),
                    ("ky_nam_hoc_id", "=", self.ky_hoc_id.id)
                ])
                # if len(lop_tin_chi) == 0:
                #     raise ValidationError(f"Không có lớp môn {hocPhan} cho sinh viên {maSv} ở dòng {i+9}")
                diemHp = False
                if len(lop_tin_chi) != 0:
                    diemHp = self.env["sv_ltc_ds"].search([
                        ("sinh_vien_id", "=", sv.id),
                        ("lop_tin_chi_id", "=", lop_tin_chi.id)
                    ])
                create_diem = {
                    "sinh_vien_id": sv.id,
                    "diem_tong_ket_thang_4": diemThang4,
                    "diem_tong_ket_dang_chu": diemChu,
                }
                if len(lop_tin_chi) == 0:
                    create_diem["hoc_phan_id"] = hoc_phan.id
                    create_diem["ky_hoc_id"] = self.ky_hoc_id.id
                else:
                    create_diem["lop_tin_chi_id"] = lop_tin_chi.id
                if diemChuyenCan != "":
                    create_diem["diem_attendance"] = float(diemChuyenCan)
                if diemTrungBinhKiemTra != "":
                    create_diem["diem_trung_binh_kiem_tra_tren_lop"] = float(
                        diemTrungBinhKiemTra)
                if diemBTTL != "":
                    create_diem["diem_bai_tap"] = float(diemBTTL)
                if diemTNTH != "":
                    create_diem["diem_thi_nghiem"] = float(diemTNTH)
                if diemThi != "":
                    create_diem["diem_cuoi_ky"] = str(diemThi)
                if diemTK != "":
                    create_diem["diem_tong_ket"] = str(diemTK)
                if diemHp == False or len(diemHp) == 0:
                    self.env["sv_ltc_ds"].create(create_diem)
                else:
                    raise ValidationError(
                        f"Lỗi dòng {i+9}, sv {maSv}, mon {hocPhan}")

    def import_diem_hoc_phan(self):
        if self.file_import:
            fd, path = tempfile.mkstemp()
            with os.fdopen(fd, "wb") as tmp:
                tmp.write(base64.decodebytes(self.file_import))
            df = pd.read_excel(path, dtype=str)
            self.process(df)
        else:
            raise ValidationError("Chưa có file excel.")
        res = {'type': 'ir.actions.client', 'tag': 'reload'}
        return res

    def get_header(self):
        fd, path = tempfile.mkstemp(suffix='.xlsx')
        import_template = pd.DataFrame(
            columns=self._header[self.import_template])
        import_template.to_excel(path, index=False)
        result = base64.b64encode(os.fdopen(fd, "rb").read())
        attachment = self.env['ir.attachment'].create({
            'name': "mau_import_diem_hoc_phan.xlsx",
            'store_fname': 'tkb.xlsx',
            'datas': result
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % (attachment.id),
            'target': 'self',
        }


class LopHanhChinhImportWizard(models.TransientModel):
    _name = "lop_hanh_chinh.import_wizard"
    _description = "Import lớp hành chính"
    _header_lop = [
        "Hình thức đào tạo", "Khoá sinh viên", "Ngành", "Cán bộ phụ trách",
        "Năm học", "Số thứ tự đợt nhập học", "Cơ sở đào tạo", "Số thứ tự lớp"
    ]
    _header_dssv = ["Mã sinh viên", "Tên lớp hành chính"]
    file_import_lop_hc = fields.Binary("File import lớp hành chính")
    file_import_sv = fields.Binary("File import sinh viên lớp hành chính")

    def process_lop(self, df: pd.DataFrame, df_sv: pd.DataFrame):
        report_string = []
        map_lop_sv = {}
        for _, row in df_sv.iterrows():
            sv = str(row["Mã sinh viên"])
            lop = str(row["Hình thức đào tạo"])
            + "|" + str(row["Khoá sinh viên"])
            + "|" + str(row["Ngành"])
            + "|" + str(row["Cơ sở đào tạo"])
            + "|" + str(row["Số thứ tự lớp"])
            if lop not in map_lop_sv:
                map_lop_sv[lop] = []
            map_lop_sv[lop].append(sv)
        for lop in map_lop_sv:
            sv_real = self.env["sinh_vien"].search([("ma_dinh_danh", "in",
                                                     map_lop_sv[lop])])
            map_lop_sv[lop] = [sv.id for sv in sv_real]
        data_lop = []
        for i, row in df.iterrows():
            print(str(row["Khoá sinh viên"]))
            lop = str(row["Hình thức đào tạo"]) + "|" + str(
                row["Khoá sinh viên"]) + "|" + str(row["Ngành"]) + "|" + str(
                    row["Cơ sở đào tạo"]) + "|" + str(row["Số thứ tự lớp"])
            ht = self.env["hinh_thuc_dao_tao"].search([
                ("ten_hinh_thuc_dao_tao", "=", str(row["Hình thức đào tạo"]))
            ])
            if len(ht) == 0:
                report_string.append(
                    f"Không có hình thức đào tạo {str(row['Hình thức đào tạo'])} ở dòng {i+1}"
                )
            co_so_dt = self.env["danh_muc.co_so_dao_tao"].search([
                ("ten_co_so_dao_tao", "=", str(row["Cơ sở đào tạo"]))
            ])
            if len(co_so_dt) == 0:
                report_string.append(
                    f"Không có cơ sở đào tạo {str(row['Cơ sở đào tạo'])} ở dòng {i+1}"
                )
            khoa_sv = self.env["khoa_sinh_vien"].search([
                ("so_thu_tu_khoa", "=", int(row["Khoá sinh viên"])),
                ("hinh_thuc_dao_tao_id", "=", ht.id),
            ])
            if len(khoa_sv) == 0:
                report_string.append(
                    f"Không có khoá sinh viên {int(row['Khoá sinh viên'])} của hình thức đào tạo {str(row['Hình thức đào tạo'])} ở dòng {i+1}"
                )
            nganh = self.env["quan_ly_nganh_hoc.nganh"].search([
                ("ten_nganh", "=", str(row["Ngành"])),
            ])
            if len(nganh) == 0:
                report_string.append(
                    f"Không có khoá sinh viên {int(row['Khoá sinh viên'])} của hình thức đào tạo {str(row['Hình thức đào tạo'])} ở dòng {i+1}"
                )
            khoa_nganh = self.env["khoa_nganh"].search([
                ("khoa_sinh_vien_id", "=", khoa_sv.id),
                ("nganh_id", "=", nganh.id),
            ])
            if len(khoa_nganh) == 0:
                khoa_nganh = self.env["khoa_nganh"].create({
                    "khoa_sinh_vien_id":
                    khoa_sv.id,
                    "nganh_id":
                    nganh.id
                })
            can_bo = self.env["nhan_vien"].search([
                ("ma_dinh_danh", "=", str(row["Cán bộ phụ trách"]))
            ])
            if len(can_bo) == 0:
                report_string.append(
                    f"Không có cán bộ với mã {str(row['Cán bộ phụ trách'])} ở dòng {i+1}"
                )
            nam_hoc = self.env["nam_hoc"].search([("ten_nam_hoc", "=",
                                                   str(row["Năm học"]))])
            if len(nam_hoc) == 0:
                report_string.append(
                    f"Không có năm học {str(row['Năm học'])} ở dòng {i+1}")
            dot_nhap_hoc = self.env["dot_nhap_hoc"].search([
                ("nam_hoc_id", "=", nam_hoc.id),
                ("thu_tu_dot", "=", int(row["Số thứ tự đợt nhập học"]))
            ])
            if len(dot_nhap_hoc) == 0:
                dot_nhap_hoc = self.env["dot_nhap_hoc"].create({
                    "ten_dot":
                    f'{nam_hoc.nam_hoc}-{int(row["Số thứ tự đợt nhập học"])}',
                    "nam_hoc_id":
                    nam_hoc.id,
                    "khoa_sinh_vien_id":
                    khoa_sv.id,
                    "thu_tu_dot":
                    int(row["Số thứ tự đợt nhập học"])
                })
            khoi_lop = self.env["khoi_lop"].search([
                ("khoa_nganh_id", "=", khoa_nganh.id),
                ("dot_nhap_hoc_id", "=", dot_nhap_hoc.id)
            ])
            if len(khoi_lop) == 0:
                khoi_lop = self.env["khoi_lop"].create({
                    "khoa_nganh_id":
                    khoa_nganh.id,
                    "dot_nhap_hoc_id":
                    dot_nhap_hoc.id
                })
            data_lop.append({
                "khoi_lop_id": khoi_lop.id,
                "can_bo_id": can_bo.id,
                "so_thu_tu_lop": int(row["Số thứ tự lớp"]),
                "co_so_dao_tao_moi": co_so_dt.id,
                "sinh_vien_ids": map_lop_sv.get(lop)
            })
        if len(report_string) > 0:
            report_string = "\n".join(report_string)
            raise ValidationError(report_string)
        self.env["lop_hanh_chinh"].create(data_lop)

    def import_lop(self):
        if self.file_import_lop_hc and self.file_import_sv:
            fd, path = tempfile.mkstemp()
            with os.fdopen(fd, "wb") as tmp:
                tmp.write(base64.decodebytes(self.file_import_lop_hc))
            df = pd.read_excel(path, dtype=str)
            if set(self._header_lop) != set(df.columns):
                raise ValidationError(
                    f"Không khớp header file import lớp\n\nHeader gốc: {self._header_lop}\n\nHeader: {list(df.columns)}"
                )
            fd1, path1 = tempfile.mkstemp()
            with os.fdopen(fd1, "wb") as tmp:
                tmp.write(base64.decodebytes(self.file_import_sv))
            df_sv = pd.read_excel(path1, dtype=str)
            if set(self._header_dssv) != set(df_sv.columns):
                raise ValidationError(
                    f"Không khớp header file import lớp\n\nHeader gốc: {self._header_dssv}\n\nHeader: {list(df_sv.columns)}"
                )
            self.process_lop(df, df_sv)
        else:
            raise ValidationError("Chưa có file excel.")
        res = {'type': 'ir.actions.client', 'tag': 'reload'}
        return res

    def get_header_lop(self):
        fd, path = tempfile.mkstemp(suffix='.xlsx')
        import_template = pd.DataFrame(columns=self._header_lop)
        import_template.to_excel(path, index=False)
        result = base64.b64encode(os.fdopen(fd, "rb").read())
        attachment = self.env['ir.attachment'].create({
            'name': "mau_import_lop_hanh_chinh.xlsx",
            'store_fname': 'test.xlsx',
            'datas': result
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % (attachment.id),
            'target': 'self',
        }

    def get_header_sv(self):
        fd, path = tempfile.mkstemp(suffix='.xlsx')
        import_template = pd.DataFrame(columns=self._header_dssv)
        import_template.to_excel(path, index=False)
        result = base64.b64encode(os.fdopen(fd, "rb").read())
        attachment = self.env['ir.attachment'].create({
            'name': "mau_import_sinh_vien_lop_hanh_chinh.xlsx",
            'store_fname': 'test.xlsx',
            'datas': result
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % (attachment.id),
            'target': 'self',
        }
class SinhVienImportWizard(models.TransientModel):
    _name = "dssv.import_wizard"
    _description = "Import danh sách sinh viên"
    _header = {
           False :  ["Mã sinh viên","Ngành", "Họ và tên", "Họ đệm", "Tên", "Ngày sinh", "Email",
            "Chứng minh nhân dân/Căn cước công dân", "Số điện thoại"],
            True : ["Ngành", "Họ và tên", "Họ đệm", "Tên", "Ngày sinh", "Email",
            "Chứng minh nhân dân/Căn cước công dân", "Số điện thoại"]
    }

    # hinh_thuc_dao_tao = fields.Many2one(comodel_name="hinh_thuc_dao_tao",
    #                                     string="Hình thức đào tạo",
    #                                     default= lambda self: self.env.user.hinh_thuc_dao_tao_id)
    hinh_thuc_dao_tao = fields.Many2one("hinh_thuc_dao_tao",
                                        string="Hình thức đào tạo của bạn",
                                        default= lambda self : self.env.user.hinh_thuc_dao_tao_id)
    file_import_sv = fields.Binary("File danh sách sinh viên")
    khong_masv = fields.Boolean("Chưa có mã sinh viên")
    #nếu không có mã sinh viên thì những trường sau sẽ hiển thị
    nam_hoc = fields.Many2one(comodel_name="nam_hoc",
                            string="Năm nhập học")
    # nganh_hoc = fields.Many2one(comodel_name="quan_ly_nganh_hoc.nganh",
    #                                 string="Ngành học"
    #                                 )
    co_so_dao_tao = fields.Selection([
        ("B", "Phía Bắc"),
        ("N", "Phía Nam"),
        ("K", "Cơ sở khác")
    ],
    string="Cơ sở đào tạo")

    co_so = fields.Many2one(comodel_name="danh_muc.co_so_dao_tao",
                            string="Cơ sở")
    trinh_hinh = fields.Many2one(comodel_name="danh_muc.trinh_do_hinh_dao_tao",
                                string="Trình độ, hình thức đào tạo")
    
    trinh_do_hinh_dao_tao = fields.Selection([
        ("CH", "Cao học"),
        ("DC", "Đại học chính quy"),
        ("LD", "Liên thông Cao đẳng lên ĐH chính quy"),
        ("BC", "Đại học chính quy bằng 2"),
        ("DV", "Đại học vừa làm vừa học"),
        ("LV", "Liên thông Cao đẳng vừa làm vừa học"),
        ("BV", "Đại học bằng 2 vừa làm vừa học"),
        ("DT", "Đại học từ xa"),
        ("LT", "Liên thông cao đẳng lên đại học từ xa"),
        ("DE", "Đại học chính quy chất lượng cao")
    ],
    string="Trình độ, hình đào tạo")
    """
    Cần tạo 2 function:
    - Tự động tạo mã sinh viên:
     + Sort tên của sinh viên.
     + 
    - Tự động tạo tên lớp hành chính.
    """
    def process_sv(self, data : pd.DataFrame):

        for _, row in data.iterrows():
            maSV = row["Mã sinh viên"]
            hoTen = row["Họ và tên"]
            hoDem = row["Họ đệm"]
            ten = row["Tên"]
            ngaySinh = datetime.strptime(row["Ngày sinh"], '%d/%m/%Y')
            email = row["Email"]
            CCCD = row["Chứng minh nhân dân/Căn cước công dân"]
            sdt = row["Số điện thoại"]
            nganh = self.env["quan_ly_nganh_hoc.nganh"].search([("ten_nganh", "=", row["Ngành"])])
            khoaSinhVien = self.env["khoa_sinh_vien"].search([
                ("hinh_thuc_dao_tao_id", "=", self.hinh_thuc_dao_tao.id),
                ("nam_hoc", "=", self.nam_hoc.id)
            ])
            khoaNganh = self.env["khoa_nganh"].search([
                ("khoa_sinh_vien_id", "=", khoaSinhVien.id),
                ("nganh_id", "=", nganh.id)
            ])
            data_sv = {
                "ma_dinh_danh" : maSV,
                "name" : hoTen,
                "ho_dem" : hoDem,
                "ten" : ten,
                "ngay_sinh" : ngaySinh,
                "email" : email,
                "so_cmnd" : CCCD,
                "so_dien_thoai" : sdt,
                "hinh_thuc_dao_tao_id" : self.hinh_thuc_dao_tao.id,
                "nganh_id" : nganh.id,
                "khoa_sinh_vien_id" : khoaSinhVien[0].id,
                "khoa_nganh_id" : khoaNganh.id,
                "trinh_hinh_id" : self.trinh_hinh.id,
            }
            sv_trung = self.env["sinh_vien"].search([("ma_dinh_danh", "=", maSV)])
            if sv_trung:
                raise ValidationError(
                    "Đã có mã sinh viên bị trùng!\nĐó là sinh viên {}, mã định danh: {}".format(sv_trung.name, sv_trung.ma_dinh_danh))
            else:
                self.env["sinh_vien"].create(data_sv)


    def compute_ma_sinh_vien(self, data: pd.DataFrame):
        #sắp xếp tên theo alphabet
        data = data.sort_values(by=['Ngành','Tên', 'Họ đệm'])
        #Tìm mã sinh viên lớn nhất
        # sv = self.env['sinh_vien'].search([
        #     ("nganh_id", "=", self.nganh_hoc.id),
        #     ("hinh_thuc_dao_tao_id", "=", self.hinh_thuc_dao_tao.id)
        # ])
        # mdd = sv[-1].ma_dinh_danh
        # stt = int(mdd[-3:])

        """
        Tạo mã sinh viên:
        MSV = Cơ sở đào tạo (B, N ,K) + Năm nhập trường + Trình độ Hình thức đào tạo (CH, DC, DT,...)
        + Ngành đào tạo + xxx (001-999)
        """
        pre_nganh = ""
        stt = 0
        msv_list = []
        for _, record in data.iterrows():
            
            
            if record["Ngành"] != pre_nganh:   
                nganh = self.env["quan_ly_nganh_hoc.nganh"].search([("ten_nganh", "=", record["Ngành"])])
                khoaSinhVien = self.env["khoa_sinh_vien"].search([
                    ("hinh_thuc_dao_tao_id", "=", self.hinh_thuc_dao_tao.id),
                    ("nam_hoc", "=", self.nam_hoc.id)
                ])
                khoaNganh = self.env["khoa_nganh"].search([
                    ("khoa_sinh_vien_id", "=", khoaSinhVien[0].id),
                    ("nganh_id", "=", nganh[0].id)
                ])
    
                sv = self.env['sinh_vien'].search([
                    ("khoa_nganh_id", "=", khoaNganh[0].id)
                ])
                if sv:
                    stt = 0
                    for svv in sv:
                        stt_sv = int(svv.ma_dinh_danh[-3:])
                        if stt_sv > stt:
                            stt = stt_sv
                else:
                    stt = 0
            pre_nganh = record["Ngành"]
            stt += 1
            str_stt = ""
            if stt < 10:
                str_stt = "00" + str(stt)
            elif stt <100:
                str_stt = "0" + str(stt)
            else:
                str_stt = str(stt)
            msv = ""
            msv = self.co_so.ky_hieu_co_so_dao_tao+self.nam_hoc.nam_hoc_char[-2:]+self.trinh_hinh.ky_hieu_trinh_do_hinh_dao_tao+str(nganh[0].ten_nganh_viet_tat)+str_stt
            msv_list.append(msv)
            print(str_stt, stt)
        data["Mã sinh viên"] = msv_list
        return data

    def import_dssv(self):
        if self.file_import_sv:
            fd, path = tempfile.mkstemp()
            with os.fdopen(fd, "wb") as tmp:
                tmp.write(base64.decodebytes(self.file_import_sv))
            df = pd.read_excel(path, dtype=str)
            if self.khong_masv:
                df = self.compute_ma_sinh_vien(df)
            if set(self._header[False]) != set(df.columns):
                raise ValidationError(
                    "Không khớp với header import!"
                )
                
            self.process_sv(df)
        else:
            raise ValidationError("Chưa có file excel.")
        res = {'type': 'ir.actions.client', 'tag': 'reload'}
        return res

    def get_header(self):
        fd, path = tempfile.mkstemp(suffix='.xlsx')
        import_template = pd.DataFrame(columns=self._header[self.khong_masv])
        import_template.to_excel(path, index= False)
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

class HoaDonPhieuDangKyTinChiImportWizard(models.TransientModel):
    _name = "hoa_don_phieu_dang_ky_tin_chi.import_wizard"
    _description = "Import hóa đơn phiếu đăng ký tín chỉ"
    _header = [
        "Mã sinh viên", "Mã lớp hành chính", "Số TC", "Đơn giá","Số thu học phí"]
    file_import = fields.Binary("File import hóa đơn phiếu đăng ký tín chỉ")
    noti = fields.Text(default='')
    dot_dang_ky_tin_chi_id = fields.Many2one("dot_dang_ky_tin_chi", string="Đợt đăng ký tín chỉ", required=True)
    phe_duyet_ngay = fields.Boolean(string="Phê duyệt hóa đơn ngay khi import", default=False)
    kiem_tra_don_gia = fields.Boolean(string="Kiểm tra đơn giá và số thu học phí (khuyến nghị)", default=True)
    kiem_tra_lop_hanh_chinh = fields.Boolean(string="Kiểm tra lớp hành chính của sinh viên (khuyến nghị)", default=True)


    def import_hoa_don_phieu_dang_ky_tin_chi(self):
        if self.file_import:
            fd, path = tempfile.mkstemp()
            with os.fdopen(fd, "wb") as tmp:
                tmp.write(base64.decodebytes(self.file_import))
            df = pd.read_excel(path, dtype=str)
            report_string = self.process(df)
            so_dong = len(df)
            if report_string:
                raise ValidationError(report_string)
            else:
                vls = f"<H4><B>Hệ thống đã import thành công {so_dong} dòng dữ liệu hóa đơn phiếu đăng ký tín chỉ.</br></B></H4>"
                if self.noti:
                    vls += "<I>Lưu ý các chú ý dưới đây</br></I>"
                    vls += str(self.noti)
                id_thong_bao = self.env["custom_noti"].create({
                    "noti_html": vls,
                })

                return {
                    'name': 'Thông báo hệ thống',
                    'type': 'ir.actions.act_window',
                    'res_model': 'custom_noti',
                    'view_mode': 'form',
                    'res_id': id_thong_bao.id,
                    'view_type': 'form',
                    'target': 'new',
                }
        else:
            raise ValidationError("Chưa có file excel.")
        res = {'type': 'ir.actions.client', 'tag': 'reload'}
        return res

    def process(self, df):
        report_string = []
        datas = []
        for i, row in df.iterrows():
            maSv = row["Mã sinh viên"]
            if maSv == "":
                break
            noti=''
            maLopHanhChinh = row["Mã lớp hành chính"]
            soTC = row["Số TC"]
            donGia = row["Đơn giá"]
            hocPhi = row["Số thu học phí"]
            sv = self.env["sinh_vien"].search([("ma_dinh_danh", "=", str(maSv))], limit=1)
            if len(sv) == 0:
                report_string.append(f"Không có sinh viên mã {maSv} ở dòng {i+2} trên hệ thống.")
            elif soTC == 0 or soTC == None:
                report_string.append(f"Dòng {i + 2} không có dữ liệu số tín chỉ")
            else:
                # phieu_dang_ky_tin_chi = self.env["phieu_dang_ky_tin_chi"].create({
                #     "sinh_vien_id" : sv.id,
                #     "tong_so_tin_chi" : int(soTC),
                #     "dot_dang_ky_tin_chi_id" : self.dot_dang_ky_tin_chi_id.id,
                #     "trang_thai_sinh_ma_thanh_toan" : self.phe_duyet_ngay,
                # })
                sv_phieu_dktc = self.env["phieu_dang_ky_tin_chi"].search(
                    [("sinh_vien_id", "=", sv.id), ("dot_dang_ky_tin_chi_id", "=", self.dot_dang_ky_tin_chi_id.id)],
                    limit=1)
                if len(sv_phieu_dktc) > 0:
                    report_string.append(
                        f"[!] Sinh viên {sv.ma_dinh_danh} tại dòng {i + 2} đã có phiếu cho đợt đăng ký này.")
                datas.append({
                    "sinh_vien_id" : sv.id,
                    "tong_so_tin_chi" : int(soTC),
                    "dot_dang_ky_tin_chi_id" : self.dot_dang_ky_tin_chi_id.id,
                    "trang_thai_sinh_ma_thanh_toan" : self.phe_duyet_ngay,
                })
                if maLopHanhChinh != None and sv.lop_hanh_chinh_id.ten_lop_hanh_chinh != maLopHanhChinh and self.kiem_tra_lop_hanh_chinh:
                    print(i + 2)
                    report_string.append(f"[!] Lớp hành chính của sinh viên {sv.ma_dinh_danh} tại dòng {i + 2} không khớp với trên hệ thống.")
                if hocPhi != None and (int(soTC) * sv.khoa_nganh_id.hoc_phi_ids.gia_tin_chi_chung) != float(hocPhi) and self.kiem_tra_don_gia:
                    print(i + 2)
                    report_string.append(f"[!] Số tiền Số thu học phí của sinh viên {sv.ma_dinh_danh} tại dòng {i + 2} trong file import không khớp với số tiền được tính trên hệ thống.\n{int(soTC) * sv.khoa_nganh_id.hoc_phi_ids.gia_tin_chi_chung} != {float(hocPhi)}")
                if donGia != None and sv.khoa_nganh_id.hoc_phi_ids.gia_tin_chi_chung != float(donGia) and self.kiem_tra_don_gia:
                    print(i + 2)
                    report_string.append(f"[!] Số tiền một tín chỉ của sinh viên {sv.ma_dinh_danh} tại dòng {i + 2} trong file import không khớp với số tiền được tính trên hệ thống.\n{sv.khoa_nganh_id.hoc_phi_ids.gia_tin_chi_chung} != {float(donGia)}")
            # if donGia != '' or donGia != None:
            #     try:
            #         if int(donGia) and int(donGia) != sv.khoa_nganh_id.hoc_phi_ids.gia_tin_chi_chung:
            #             print(i)
            #             report_string.append(f"[!] Số tiền một tín chỉ tại dòng {i + 2} trong file import không khớp với trên hệ thống.")
            #     except Exception as e:
            #         print(e)
        if report_string:
            return "\n".join(report_string)
        else:
            self.env["phieu_dang_ky_tin_chi"].create(datas)

    def get_header(self):
        fd, path = tempfile.mkstemp(suffix='.xlsx')
        import_template = pd.DataFrame(columns=self._header)
        import_template.to_excel(path, index=False)
        result = base64.b64encode(os.fdopen(fd, "rb").read())
        attachment = self.env['ir.attachment'].create({
            'name': "mau_import_hoa_don_phieu_dang_ky_tin_chi.xlsx",
            'store_fname': 'test.xlsx',
            'datas': result
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % (attachment.id),
            'target': 'self',
        }