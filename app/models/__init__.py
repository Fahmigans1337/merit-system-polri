# Import semua model agar Alembic dan create_all bisa mendeteksi seluruh tabel
from app.models.satker import Satker          # noqa: F401
from app.models.user import User, UserRole    # noqa: F401
from app.models.personel import Personel      # noqa: F401
from app.models.riwayat_jabatan import RiwayatJabatan, StatusJabatan  # noqa: F401
