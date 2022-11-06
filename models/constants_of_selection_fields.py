"""
    File này lưu các constant cho selection fields
"""
cap_don_vi = [
    ("Bộ môn", "Bộ môn"),
    ("Phòng", "Phòng"),
    ("Khoa", "Khoa"),
    ("Trung tâm", "Trung tâm"),
    ("Trung tâm nhỏ", "Trung tâm nhỏ"),
    ("Viện", "Viện"),
    ("Học viện", "Học viện"),
    ("Hội đồng trường", "Hội đồng trường"),
]

hoc_ky_selection = [
    ("1", "Kỳ 1"),
    ("2", "Kỳ 2"),
    ("3", "Kỳ 3"),
    ("4", "Kỳ 4"),
    ("5", "Kỳ 5"),
    ("6", "Kỳ 6"),
    ("7", "Kỳ 7"),
    ("8", "Kỳ 8"),
    ("9", "Kỳ 9"),
    ("10", "Kỳ 10"),
    ("11", "Kỳ 11"),
    ("12", "Kỳ 12"),
    ("13", "Kỳ 13"),
    ("14", "Kỳ 14"),
    ("15", "Kỳ 15"),
    ("16", "Kỳ 16"),
    ("17", "Kỳ 17"),
    ("18", "Kỳ 18"),
    ("19", "Kỳ 19"),
    ("20", "Kỳ 20"),
]

loai_ky_selection = [
    ("0", "Thường xuyên"),
    ("1", "Tốt nghiệp"),
]

# phuong_thuc_thu_phi_selection = [
#     ("0", "Giá tín chỉ theo kỳ"),
#     ("1", "Giá tín chỉ theo kỳ thường xuyên và kỳ tốt nghiệp"),
#     ("2", "Giá theo kỳ học"),
#     ("3", "Giá theo năm học"),
# ]
# Tạm thời fix cứng chỉ có Giá tín chỉ theo kỳ để vận hành ở tt1
phuong_thuc_thu_phi_selection = [
    ("0", "Giá tín chỉ theo kỳ"),
]

loai_don_vi = [
    ("Đơn vị cứng", "Đơn vị cứng"),
    ("Đơn vị mềm", "Đơn vị mềm"),
]

vai_tro_don_vi_selection = [('Trưởng', 'Cấp trưởng'), ('Phó', 'Cấp phó'),
                            ('Cán bộ', 'Cán bộ')]

vai_tro_selection = [("nhan_vien", "Nhân viên"), ("sinh_vien", "Sinh viên"),
                     ("quan_tri", "Quản trị viên"),
                     ("qtv_tx", "Quản trị viên từ xa"),
                     ("qtv_cq", "Quản trị viên chính quy"),
                     ("qtv_vhvl", "Quản trị viên vừa học vừa làm"),
                     ("ke_toan", "Kế toán"),
                     ("tro_giang", "Trợ giảng"),
                     ("can_bo_qlkh", "Cán bộ quản lý khoa học"),
                     ("lanh_dao", "Lãnh đạo")]

trang_thai_sinh_vien = [("Đang học", "Đang học"),
                        ("Bị buộc thôi học", "Bị buộc thôi học"),
                        ("Thôi học", "Thôi học"), ("Tốt nghiệp", "Tốt nghiệp")]

trang_thai_sinh_vien_hoc_ky = [("Đang học", "Đang học"),
                               ("Học xong", "Học xong")]

trang_thai_ky_nam_hoc = [("Đang diễn ra", "Đang diễn ra"),
                         ("Hoàn thành", "Hoàn thành")]

quy_tac_xu_ly_ket_qua_hoc_tap_theo_tin_chi = [("Học lại", "Học lại"),
                                              ("Cảnh cáo", "Cảnh cáo"),
                                              ("Buộc thôi học",
                                               "Buộc thôi học")]

hoc_ham_hoc_vi = [("ThS", "Thạc sĩ"), ("GVC", "Giảng viên chính"),
                  ("TS", "Tiến sĩ"), ("PGS.TS", "Phó giáo sư tiến sĩ"),
                  ("GS", "Giáo sư")]
hoc_ham_selection = [
    ("GS", "Giáo sư"),
    ("PGS", "Phó giáo sư"),
]

hoc_vi_selection = [
    ("Cử nhân", "Cử nhân"),
    ("Kỹ sư", "Kỹ sư"),
    ("Thạc sỹ", "Thạc sỹ"),
    ("Tiến sỹ", "Tiến sỹ"),
    ("Giảng viên chính", "Giảng viên chính")
]

trang_thai_phieu_yeu_cau_cong_nhan_kqht = [("Đang duyệt", "Đang duyệt"),
                                           ("Đã duyệt", "Đã duyệt")]

don_vi_tien_te_selection = [("VND", "VNĐ"), ("USD", "Đô-la Mỹ")]

diem_thi_selection = [
    #     V: Vắng thi
    # - H: Hoãn thi
    # - C: Cấm thi
    # - DC: Đình chỉ thi
    ("V", "Vắng thi"),
    ("H", "Hoãn thi"),
    ("C", "Cấm thi"),
    ("DC", "Đình chỉ thi")
]

# trang_thai_ket_qua_mon_hoc liên quan đến cả logic trong sv_ltc_ds
trang_thai_ket_qua_mon_hoc = [
    ("da_dat", "Đã đạt"),
    ("chua_dat", "Chưa đạt"),
    ("chua_du_dau_diem", "Chưa đủ đầu điểm"),
    ("hoan_thi", "Hoãn thi"),
]
