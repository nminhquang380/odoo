import logging

from odoo import models, api, fields

_logger = logging.getLogger(__name__)


class QuyCheDaoTaoNamHoc(models.Model):
    """
        Class này dùng để khởi tạọ các quy chế đào tạo năm học
        Mỗi quy chế gồm các thông tin:
            -
    """

    _name = "qldt.quy_che_dao_tao_nam_hoc"
    _description = "Quản lý quy chế đào tạo năm học"

    ten_quy_che = fields.Char(string="Tên quy chế")
    ma_quy_che = fields.Char(string="Mã quy chế")
    danh_sach_van_ban_quy_dinh = fields.Many2many(
        comodel_name="danh_muc.van_ban_quy_dinh", string="Danh sách băn bản-quy định"
    )
    dot_nhap_hoc_ids = fields.Many2many(
        comodel_name="dot_nhap_hoc", string="Danh sách đợt nhập học áp dụng"
    )
    khoa_sinh_vien_ids = fields.Many2one(
        comodel_name="khoa_sinh_vien",
        ondelete="cascade",
        string="Khóa sinh viên áp dụng",
    )
    chuong_trinh_khung_id = fields.Many2one(
        comodel_name="chuong_trinh_khung",
        ondelete="cascade",
        string="Chương trình khung",
    )
    phuong_phap_danh_gia_id = fields.Many2one(
        comodel_name="danh_muc.phuong_phap_danh_gia_hoc_phan",
        ondelete="set null",
        string="Phương pháp đánh gía",
    )
    dau_diem_ids = fields.Many2many(
        comodel_name='danh_muc.dau_diem',
        related='phuong_phap_danh_gia_id.dau_diem_ids',
        string='Danh sách đầu điểm sử dụng'
    )
    # hoc_phan_ap_dung_ids = fields.One2many(
    #     comodel_name='mon_hoc_dieu_kien',
    #     related='chuong_trinh_khung_ids.mon_hoc_dieu_kien_ids',
    #     store=True,
    #     string='Danh sách môn học áp dụng'
    # )
    chuong_trinh_khung_ids = fields.Many2many(
        comodel_name="chuong_trinh_khung",
        compute='_compute_chuong_trinh_khung_ids',
        store=True,
        string="Chương trình khung áp dụng",
    )

    _sql_constraints = [('ma_quy_che_unique', 'unique(ma_quy_che)', 'Mã quy chế đào tạo năm học đã tồn tại.')]

    @api.depends('dot_nhap_hoc_ids','dot_nhap_hoc_ids.khoa_nganh_ids')
    def _compute_chuong_trinh_khung_ids(self):
        for record in self:
            if record.dot_nhap_hoc_ids.khoa_nganh_ids:
                list_ctk = []
                for each_khoa_nganh in record.dot_nhap_hoc_ids.khoa_nganh_ids:
                    ctk = self.env['chuong_trinh_khung'].search([(
                        'ten_chuong_trinh_khung','=',each_khoa_nganh.ctk_id.ten_chuong_trinh_khung
                    )]) #cần thêm logic để chắc chắn chỉ có 1 bản ghi ctk - nếu không sẽ lỗi singleton
                    if len(ctk) == 1:
                        list_ctk.append(ctk.id)
                    elif len(ctk) > 1:
                        list_ctk.append(x for x in ctk.ids)
                record.chuong_trinh_khung_ids = list_ctk
            _logger.info("\n\n danh sach CTK hien tai: {}".format(record.chuong_trinh_khung_ids))


    @api.onchange("phuong_phap_danh_gia_id", "dot_nhap_hoc_ids","chuong_trinh_khung_ids")
    def tu_dong_cap_nhat_phuong_phap_danh_gia_trong_hoc_phan(self):
        """
            Sau khi thiết lập quy chế thì tự động lấy bộ đầu điểm tương ứng và khởi tạo trong các học phần thuộc
            chương trình khung được chọn theo trình tự:
                1. xác định chương trình khung
                2. xác định danh sách đầu điểm tương ứng với phương pháp đánh giá được chọn
                3. với mỗi học phần thuộc chương trình khung:
                    3.1 nếu đã tồn tại phương pháp đánh giá (bao gồm các đầu điểm + trọng số) thì bỏ qua
                    3.2 nếu chưa tồn tại phương pháp đánh giá thì thêm mới (mặc định sẽ khởi tạo giá trị các trọng số = 0)

            TODO:
                1.xử lý trường hợp nhiều khối lớp - nhiều chương trình khung
                2. chuyển logic này về hàm create(), chỉ khởi tạo các đầu điểm + trọng số cho từng môn học sau khi tạo
                    quy chế thành công (hiện tại đang khỏi tạo trước khi ấn nút Save)
        """
        for record in self:
            if record.phuong_phap_danh_gia_id and record.dot_nhap_hoc_ids:
                # lấy danh sách đầu điểm của phương pháp đánh giá hiện tại
                danh_sach_dau_diem = record.phuong_phap_danh_gia_id.dau_diem_ids
                hinh_thuc_dao_tao = (
                    record.phuong_phap_danh_gia_id.hinh_thuc_dao_tao_ap_dung
                )
                _logger.info("Danh sach dau diem: {}".format(danh_sach_dau_diem))
                # xác định các chương trình khung áp dụng thông qua đợt nhập học -> khóa ngành -> CTK của khóa - ngành
                # ở đây có thể có nhiều CTK do quy chế áp dụng cho nhiều đợt nhập học, mỗi đợt nhập học gồm nhiều khóa ngành
                for ctk in record.chuong_trinh_khung_ids:
                    danh_sach_hoc_phan = ctk.mon_hoc_dieu_kien_ids.hoc_phan_id
                    _logger.info(
                        "Danh sach hoc phan cua ctk {} : {}".format(
                            ctk.ten_chuong_trinh_khung, danh_sach_hoc_phan
                        )
                    )
                    _logger.info("\n\nCTK đang xét : {}".format(ctk))
                    # khởi tạo danh sách đầu điểm + trọng số (nếu có) cho các học phần trong ctk
                    for hoc_phan in danh_sach_hoc_phan:
                        for dau_diem in danh_sach_dau_diem:
                            pp_danh_gia_da_co = self.env[
                                "qldt.trong_so_diem_hoc_phan"
                            ].search(
                                [
                                    ("hoc_phan_ap_dung_id", "=", hoc_phan.id),
                                    ("dau_diem_id", "=", dau_diem.id),
                                    ("chuong_trinh_khung_id", "=", ctk._origin.id)
                                ]
                            )
                            # nếu chưa có thì tạo mới - TODO: xử lý trường hợp đã có + ghi đè
                            if not pp_danh_gia_da_co:
                                pp_danh_gia = self.env[
                                    "qldt.trong_so_diem_hoc_phan"
                                ].create(
                                    {
                                        "dot_nhap_hoc_ids": record.dot_nhap_hoc_ids.ids,
                                        "hinh_thuc_dao_tao_id": hinh_thuc_dao_tao.id,
                                        "phuong_phap_danh_gia_id": record.phuong_phap_danh_gia_id.id,
                                        "hoc_phan_ap_dung_id": hoc_phan.id,
                                        "dau_diem_id": dau_diem.id,
                                        "gia_tri_trong_so": 0.0,
                                        "chuong_trinh_khung_id": ctk._origin.id
                                    }
                                )
                            else:
                                _logger.info("trọng số điểm đã tồn tại: {} {}".format(ctk.id,pp_danh_gia_da_co.id))
                            #     if not pp_danh_gia_da_co.chuong_trinh_khung_id:
                            #         pp_danh_gia_da_co.write({
                            #             "chuong_trinh_khung_id": ctk._origin.id
                            #         })
                _logger.info(
                    "đã cập nhật trọng số + đầu điểm cho các học phần thuộc ctk"
                )

    def tu_dong_cap_nhat_phuong_phap_danh_gia_trong_hoc_phan_old(self):
        """
            Sau khi thiết lập quy chế thì tự động lấy bộ đầu điểm tương ứng và khởi tạo trong các học phần thuộc
            chương trình khung được chọn theo trình tự:
                1. xác định chương trình khung
                2. xác định danh sách đầu điểm tương ứng với phương pháp đánh giá được chọn
                3. với mỗi học phần thuộc chương trình khung:
                    3.1 nếu đã tồn tại phương pháp đánh giá (bao gồm các đầu điểm + trọng số) thì bỏ qua
                    3.2 nếu chưa tồn tại phương pháp đánh giá thì thêm mới (mặc định sẽ khởi tạo giá trị các trọng số = 0)

            TODO:
                1.xử lý trường hợp nhiều khối lớp - nhiều chương trình khung
                2. chuyển logic này về hàm create(), chỉ khởi tạo các đầu điểm + trọng số cho từng môn học sau khi tạo
                    quy chế thành công (hiện tại đang khỏi tạo trước khi ấn nút Save)
        """
        for record in self:
            if record.phuong_phap_danh_gia_id and record.dot_nhap_hoc_ids:
                # lấy danh sách đầu điểm của phương pháp đánh giá hiện tại
                danh_sach_dau_diem = record.phuong_phap_danh_gia_id.dau_diem_ids
                hinh_thuc_dao_tao = (
                    record.phuong_phap_danh_gia_id.hinh_thuc_dao_tao_ap_dung
                )
                _logger.info("Danh sach dau diem: {}".format(danh_sach_dau_diem))
                # xác định các chương trình khung áp dụng thông qua đợt nhập học -> khóa ngành -> CTK của khóa - ngành
                # ở đây có thể có nhiều CTK do quy chế áp dụng cho nhiều đợt nhập học, mỗi đợt nhập học gồm nhiều khóa ngành
                for ctk in record.dot_nhap_hoc_ids.khoa_nganh_ids.ctk_id:
                    danh_sach_hoc_phan = ctk.mon_hoc_dieu_kien_ids.hoc_phan_id
                    _logger.info(
                        "Danh sach hoc phan cua ctk {} : {}".format(
                            ctk.ten_chuong_trinh_khung, danh_sach_hoc_phan
                        )
                    )
                    _logger.info("\n\nCTK đang xét : {}".format(record.dot_nhap_hoc_ids.khoa_nganh_ids.ctk_id.ten_chuong_trinh_khung))
                    # khởi tạo danh sách đầu điểm + trọng số (nếu có) cho các học phần trong ctk
                    for hoc_phan in danh_sach_hoc_phan:
                        for dau_diem in danh_sach_dau_diem:
                            pp_danh_gia_da_co = self.env[
                                "qldt.trong_so_diem_hoc_phan"
                            ].search(
                                [
                                    ("hoc_phan_ap_dung_id", "=", hoc_phan.id),
                                    ("dau_diem_id", "=", dau_diem.id)

                                ]
                            )
                            # nếu chưa có thì tạo mới - TODO: xử lý trường hợp đã có + ghi đè
                            if not pp_danh_gia_da_co:
                                pp_danh_gia = self.env[
                                    "qldt.trong_so_diem_hoc_phan"
                                ].create(
                                    {
                                        "dot_nhap_hoc_ids": record.dot_nhap_hoc_ids.ids,
                                        "hinh_thuc_dao_tao_id": hinh_thuc_dao_tao.id,
                                        "phuong_phap_danh_gia_id": record.phuong_phap_danh_gia_id.id,
                                        "hoc_phan_ap_dung_id": hoc_phan.id,
                                        "dau_diem_id": dau_diem.id,
                                        "gia_tri_trong_so": 0.0,
                                        "chuong_trinh_khung_id":ctk.id
                                    }
                                )
                            else:
                                _logger.info("\n\nPhương pháp đánh giá đã có : {} {}"
                                             .format(pp_danh_gia_da_co, pp_danh_gia_da_co.chuong_trinh_khung_id))
                                # pp_danh_gia_da_co.write({
                                #     "chuong_trinh_khung_id": ctk.id
                                # })
                _logger.info(
                    "đã cập nhật trọng số + đầu điểm cho các học phần thuộc ctk"
                )
