from enum import Enum

BOOK_ID_MAP = {
    "RBI_002": "An Sĩ Toàn Thư",
    "RBI_010": "Kinh Tương Ưng Bộ",
    "RBI_007": "Quan Âm Thị Kính",
    "RBI_008": "Thiền Uyển Tập Anh",
}


class Title(Enum):
    """Enumeration of titles."""

    AN_SI_TOAN_THU = "An Sĩ Toàn Thư"
    KINH_TUONG_UNG_BO = "Kinh Tương Ưng Bộ"
    QUAN_AM_THI_KINH = "Quan Âm Thị Kính"
    THIEN_UYEN_TAP_ANH = "Thiền Uyển Tập Anh"


class Volume(Enum):
    """Enumeration of volumes."""

    AN_SI_TOAN_THU_QUYEN_I = (
        "An Sĩ Toàn Thư - Phần I Âm Chất Văn Quảng Nghĩa - Quyển I"
    )
    AN_SI_TOAN_THU_QUYEN_II = (
        "An Sĩ Toàn Thư - Phần I Âm Chất Văn Quảng Nghĩa - Quyển II"
    )
    AN_SI_TOAN_THU_QUYEN_III = (
        "An Sĩ Toàn Thư - Phần I Âm Chất Văn Quảng Nghĩa - Quyển III"
    )
    AN_SI_TOAN_THU_QUYEN_IV = (
        "An Sĩ Toàn Thư - Phần I Âm Chất Văn Quảng Nghĩa - Quyển IV"
    )
