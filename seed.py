"""
Seed Script - Merit System Personel Polri
Mengisi database dengan data awal untuk demo dan testing.

Cara menjalankan:
  python seed.py
  
Atau via Docker:
  docker compose run --rm seed
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app.database import Base
import app.models  # register all models

from app.models.user import User, UserRole
from app.models.satker import Satker
from app.models.personel import Personel
from app.models.riwayat_jabatan import RiwayatJabatan, StatusJabatan
from app.core.security import hash_password
from datetime import date
import uuid

# Buat semua tabel
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    if db.query(User).count() > 0:
        print("ℹ️  Database sudah memiliki data. Skip seeding.")
        sys.exit(0)

    print("🌱 Memulai proses seeding database...")
    print("=" * 60)

    # ── Satker ───────────────────────────────────────────────────
    print("\n[1/4] Membuat Satuan Kerja...")
    satker_ssdm = Satker(
        id=str(uuid.uuid4()), nama="SSDM POLRI", kode="SSDM",
        deskripsi="Staf Sumber Daya Manusia Kepolisian Negara RI"
    )
    satker_metro = Satker(
        id=str(uuid.uuid4()), nama="POLDA METRO JAYA", kode="POLDAMETRO",
        deskripsi="Kepolisian Daerah Metro Jaya"
    )
    satker_jabar = Satker(
        id=str(uuid.uuid4()), nama="POLDA JAWA BARAT", kode="POLDAJABAR",
        deskripsi="Kepolisian Daerah Jawa Barat"
    )
    satker_jatim = Satker(
        id=str(uuid.uuid4()), nama="POLDA JAWA TIMUR", kode="POLDAJATIM",
        deskripsi="Kepolisian Daerah Jawa Timur"
    )
    db.add_all([satker_ssdm, satker_metro, satker_jabar, satker_jatim])
    db.commit()
    db.refresh(satker_ssdm); db.refresh(satker_metro)
    db.refresh(satker_jabar); db.refresh(satker_jatim)
    print(f"   ✅ {satker_ssdm.kode}, {satker_metro.kode}, {satker_jabar.kode}, {satker_jatim.kode}")

    # ── Users ─────────────────────────────────────────────────────
    print("\n[2/4] Membuat Akun Pengguna...")
    admin = User(
        id=str(uuid.uuid4()), username="admin.ssdm",
        email="admin@ssdm.polri.go.id",
        password_hash=hash_password("Admin@12345"),
        role=UserRole.ADMIN_SSDM, satker_id=satker_ssdm.id, is_active=True
    )
    op_metro = User(
        id=str(uuid.uuid4()), username="operator.metro",
        email="operator@poldametro.polri.go.id",
        password_hash=hash_password("Operator@123"),
        role=UserRole.OPERATOR_SATKER, satker_id=satker_metro.id, is_active=True
    )
    op_jabar = User(
        id=str(uuid.uuid4()), username="operator.jabar",
        email="operator@poldajabar.polri.go.id",
        password_hash=hash_password("Operator@123"),
        role=UserRole.OPERATOR_SATKER, satker_id=satker_jabar.id, is_active=True
    )
    op_jatim = User(
        id=str(uuid.uuid4()), username="operator.jatim",
        email="operator@poldajatim.polri.go.id",
        password_hash=hash_password("Operator@123"),
        role=UserRole.OPERATOR_SATKER, satker_id=satker_jatim.id, is_active=True
    )
    db.add_all([admin, op_metro, op_jabar, op_jatim])
    db.commit()
    print(f"   ✅ admin.ssdm (ADMIN) | operator.metro, operator.jabar, operator.jatim (OPERATOR)")

    # ── Personel ──────────────────────────────────────────────────
    print("\n[3/4] Membuat Data Personel...")
    p = [
        Personel(id=str(uuid.uuid4()), nama="BRIGADIR JENDERAL POLISI ANDI WIJAYA, S.H., M.H.", nrp_nip="72040217", pangkat="BRIGJEN POL", tempat_lahir="Jakarta", tanggal_lahir=date(1971, 3, 15), satker_id=satker_ssdm.id),
        Personel(id=str(uuid.uuid4()), nama="KOMISARIS BESAR POLISI BUDI SANTOSO, S.I.K.", nrp_nip="82050318", pangkat="KOMBES POL", tempat_lahir="Surabaya", tanggal_lahir=date(1978, 6, 22), satker_id=satker_metro.id),
        Personel(id=str(uuid.uuid4()), nama="AJUN KOMISARIS BESAR POLISI CITRA DEWI, S.H.", nrp_nip="90060419", pangkat="AKBP", tempat_lahir="Bandung", tanggal_lahir=date(1985, 9, 10), satker_id=satker_metro.id),
        Personel(id=str(uuid.uuid4()), nama="KOMISARIS POLISI DEDI KURNIAWAN, S.I.K.", nrp_nip="93070520", pangkat="KOMPOL", tempat_lahir="Bandung", tanggal_lahir=date(1988, 12, 5), satker_id=satker_jabar.id),
        Personel(id=str(uuid.uuid4()), nama="AJUN KOMISARIS POLISI EKO PRASETYO, S.T.K.", nrp_nip="96080621", pangkat="AKP", tempat_lahir="Semarang", tanggal_lahir=date(1991, 4, 18), satker_id=satker_jabar.id),
        Personel(id=str(uuid.uuid4()), nama="INSPEKTUR POLISI SATU FAUZI RAHMAN", nrp_nip="98090722", pangkat="IPTU", tempat_lahir="Malang", tanggal_lahir=date(1994, 7, 30), satker_id=satker_jatim.id),
    ]
    db.add_all(p)
    db.commit()
    for pp in p:
        db.refresh(pp)
    print(f"   ✅ {len(p)} personel berhasil dibuat")

    # ── Riwayat Jabatan ───────────────────────────────────────────
    print("\n[4/4] Membuat Riwayat Jabatan...")
    rj_list = [
        # P[0] - BRIGJEN ANDI WIJAYA (SSDM)
        RiwayatJabatan(id=str(uuid.uuid4()), personel_id=p[0].id, jabatan="KASUBDIT BINKAR", satuan_kerja="DITPERS POLRI", fungsi="PEMBINAAN KARIER", tanggal_mulai=date(2010, 1, 1), tanggal_berakhir=date(2014, 12, 31), nivelering_jabatan="ES-III/A", status_jabatan=StatusJabatan.NON_AKTIF, keterangan="Jabatan awal karier"),
        RiwayatJabatan(id=str(uuid.uuid4()), personel_id=p[0].id, jabatan="KASUBDIT MUTASI", satuan_kerja="DITPERS POLRI", fungsi="MUTASI PERSONEL", tanggal_mulai=date(2015, 1, 1), tanggal_berakhir=date(2018, 12, 31), nivelering_jabatan="ES-III/A", status_jabatan=StatusJabatan.NON_AKTIF, keterangan="Promosi internal"),
        RiwayatJabatan(id=str(uuid.uuid4()), personel_id=p[0].id, jabatan="KAROPERS SSDM POLRI", satuan_kerja="SSDM POLRI", fungsi="OPERASIONAL SDM", tanggal_mulai=date(2019, 1, 1), tanggal_berakhir=date(2022, 12, 31), nivelering_jabatan="ES-II/A", status_jabatan=StatusJabatan.NON_AKTIF, keterangan="Naik eselon II"),
        RiwayatJabatan(id=str(uuid.uuid4()), personel_id=p[0].id, jabatan="ASISTEN KAPOLRI BIDANG SDM", satuan_kerja="MABES POLRI", fungsi="MANAJEMEN SDM POLRI", tanggal_mulai=date(2023, 1, 1), tanggal_berakhir=None, nivelering_jabatan="ES-I/B", status_jabatan=StatusJabatan.AKTIF, keterangan="Jabatan saat ini"),

        # P[1] - KOMBES BUDI SANTOSO (Polda Metro)
        RiwayatJabatan(id=str(uuid.uuid4()), personel_id=p[1].id, jabatan="KASAT RESKRIM", satuan_kerja="POLRES JAKARTA SELATAN", fungsi="RESERSE KRIMINAL", tanggal_mulai=date(2012, 3, 1), tanggal_berakhir=date(2016, 2, 28), nivelering_jabatan="ES-IV/A", status_jabatan=StatusJabatan.NON_AKTIF, keterangan=""),
        RiwayatJabatan(id=str(uuid.uuid4()), personel_id=p[1].id, jabatan="WAKAPOLRES METRO JAKARTA SELATAN", satuan_kerja="POLRES METRO JAKARTA SELATAN", fungsi="OPERASIONAL", tanggal_mulai=date(2016, 3, 1), tanggal_berakhir=date(2020, 2, 28), nivelering_jabatan="ES-III/B", status_jabatan=StatusJabatan.NON_AKTIF, keterangan="Promosi jabatan"),
        RiwayatJabatan(id=str(uuid.uuid4()), personel_id=p[1].id, jabatan="DIRRESKRIMUM POLDA METRO JAYA", satuan_kerja="POLDA METRO JAYA", fungsi="RESERSE KRIMINAL UMUM", tanggal_mulai=date(2020, 3, 1), tanggal_berakhir=None, nivelering_jabatan="ES-II/B", status_jabatan=StatusJabatan.AKTIF, keterangan="Jabatan saat ini"),

        # P[2] - AKBP CITRA DEWI (Polda Metro)
        RiwayatJabatan(id=str(uuid.uuid4()), personel_id=p[2].id, jabatan="KASUBAG RENMIN", satuan_kerja="POLRES METRO DEPOK", fungsi="PERENCANAAN DAN ADMINISTRASI", tanggal_mulai=date(2015, 6, 1), tanggal_berakhir=date(2019, 5, 31), nivelering_jabatan="ES-IV/A", status_jabatan=StatusJabatan.NON_AKTIF, keterangan=""),
        RiwayatJabatan(id=str(uuid.uuid4()), personel_id=p[2].id, jabatan="KAPOLSEK CILINCING", satuan_kerja="POLRES METRO JAKARTA UTARA", fungsi="OPERASIONAL KEWILAYAHAN", tanggal_mulai=date(2019, 6, 1), tanggal_berakhir=date(2022, 5, 31), nivelering_jabatan="ES-IV/A", status_jabatan=StatusJabatan.NON_AKTIF, keterangan="Mutasi antar satker"),
        RiwayatJabatan(id=str(uuid.uuid4()), personel_id=p[2].id, jabatan="KABAG OPS POLRES METRO JAKARTA UTARA", satuan_kerja="POLRES METRO JAKARTA UTARA", fungsi="OPERASIONAL", tanggal_mulai=date(2022, 6, 1), tanggal_berakhir=None, nivelering_jabatan="ES-III/B", status_jabatan=StatusJabatan.AKTIF, keterangan="Jabatan saat ini"),

        # P[3] - KOMPOL DEDI KURNIAWAN (Polda Jabar)
        RiwayatJabatan(id=str(uuid.uuid4()), personel_id=p[3].id, jabatan="KASAT LANTAS", satuan_kerja="POLRES BANDUNG", fungsi="LALU LINTAS", tanggal_mulai=date(2018, 1, 1), tanggal_berakhir=date(2021, 12, 31), nivelering_jabatan="ES-IV/A", status_jabatan=StatusJabatan.NON_AKTIF, keterangan="Jabatan pertama"),
        RiwayatJabatan(id=str(uuid.uuid4()), personel_id=p[3].id, jabatan="KAPOLSEK COBLONG", satuan_kerja="POLRESTABES BANDUNG", fungsi="OPERASIONAL KEWILAYAHAN", tanggal_mulai=date(2022, 1, 1), tanggal_berakhir=None, nivelering_jabatan="ES-IV/A", status_jabatan=StatusJabatan.AKTIF, keterangan="Jabatan saat ini"),

        # P[4] - AKP EKO PRASETYO (Polda Jabar)
        RiwayatJabatan(id=str(uuid.uuid4()), personel_id=p[4].id, jabatan="KANIT RESKRIM", satuan_kerja="POLSEK BANDUNG WETAN", fungsi="RESERSE KRIMINAL", tanggal_mulai=date(2020, 7, 1), tanggal_berakhir=date(2023, 6, 30), nivelering_jabatan="ES-V/A", status_jabatan=StatusJabatan.NON_AKTIF, keterangan=""),
        RiwayatJabatan(id=str(uuid.uuid4()), personel_id=p[4].id, jabatan="KASAT RESKRIM POLRES CIMAHI", satuan_kerja="POLRES CIMAHI", fungsi="RESERSE KRIMINAL", tanggal_mulai=date(2023, 7, 1), tanggal_berakhir=None, nivelering_jabatan="ES-IV/A", status_jabatan=StatusJabatan.AKTIF, keterangan="Promosi jabatan pertama"),

        # P[5] - IPTU FAUZI RAHMAN (Polda Jatim)
        RiwayatJabatan(id=str(uuid.uuid4()), personel_id=p[5].id, jabatan="KANIT INTELKAM", satuan_kerja="POLRES MALANG", fungsi="INTELIJEN DAN KEAMANAN", tanggal_mulai=date(2022, 3, 1), tanggal_berakhir=None, nivelering_jabatan="ES-V/A", status_jabatan=StatusJabatan.AKTIF, keterangan="Jabatan pertama"),
    ]
    db.add_all(rj_list)
    db.commit()
    print(f"   ✅ {len(rj_list)} riwayat jabatan berhasil dibuat")

    print("\n" + "=" * 60)
    print("🎉 SEEDING SELESAI!")
    print("=" * 60)
    print("\n📋 Akun login yang tersedia:")
    print("   Username      | Password      | Role")
    print("   ------------- | ------------- | ---------------")
    print("   admin.ssdm    | Admin@12345   | ADMIN_SSDM")
    print("   operator.metro| Operator@123  | OPERATOR_SATKER")
    print("   operator.jabar| Operator@123  | OPERATOR_SATKER")
    print("   operator.jatim| Operator@123  | OPERATOR_SATKER")
    print("\n🌐 Swagger UI : http://localhost:8000/docs")
    print("📄 ReDoc      : http://localhost:8000/redoc")

except Exception as exc:
    print(f"\n❌ Error saat seeding: {exc}")
    db.rollback()
    raise
finally:
    db.close()


