"""
Seed Script - Merit System Personel Polri
Mengisi database dengan data lengkap: 34 Polda + Satker Mabes, pangkat lengkap, personel demo.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app.database import Base
import app.models
from app.models.user import User, UserRole
from app.models.satker import Satker
from app.models.personel import Personel
from app.models.riwayat_jabatan import RiwayatJabatan, StatusJabatan
from app.core.security import hash_password
from datetime import date
import uuid

Base.metadata.create_all(bind=engine)
db = SessionLocal()

try:
    if db.query(User).count() > 0:
        print("i  Database sudah memiliki data. Skip seeding.")
        sys.exit(0)

    print("Memulai proses seeding database...")
    print("=" * 60)

    # ─────────────────────────────────────────────────────────────
    # [1/4] SATUAN KERJA
    # ─────────────────────────────────────────────────────────────
    print("\n[1/4] Membuat Satuan Kerja...")

    SATKER_DATA = [
        # ── Mabes Polri ──────────────────────────────────────────
        ("SSDM POLRI",        "SSDM",          "Staf Sumber Daya Manusia Polri"),
        ("BARESKRIM POLRI",   "BARESKRIM",      "Badan Reserse Kriminal Polri"),
        ("BAINTELKAM POLRI",  "BAINTELKAM",     "Badan Intelijen Keamanan Polri"),
        ("BAHARKAM POLRI",    "BAHARKAM",       "Badan Pemelihara Keamanan Polri"),
        ("KORLANTAS POLRI",   "KORLANTAS",      "Korps Lalu Lintas Polri"),
        ("KORBRIMOB POLRI",   "KORBRIMOB",      "Korps Brigade Mobil Polri"),
        ("DENSUS 88 AT POLRI","DENSUS88",       "Detasemen Khusus 88 Anti Teror"),
        ("LEMDIKLAT POLRI",   "LEMDIKLAT",      "Lembaga Pendidikan dan Pelatihan Polri"),
        ("DIV PROPAM POLRI",  "DIVPROPAM",      "Divisi Profesi dan Pengamanan"),
        ("DIV TIK POLRI",     "DIVTIK",         "Divisi Teknologi Informasi dan Komunikasi"),
        ("ITWASUM POLRI",     "ITWASUM",        "Inspektorat Pengawasan Umum Polri"),
        # ── Polda (urut Aceh - Papua) ─────────────────────────────
        ("POLDA ACEH",                          "POLDAACEH",     "Polda Aceh - Banda Aceh"),
        ("POLDA SUMATERA UTARA",                "POLDASUMUT",    "Polda Sumut - Medan"),
        ("POLDA SUMATERA BARAT",                "POLDASUMBAR",   "Polda Sumbar - Padang"),
        ("POLDA RIAU",                          "POLDARIAU",     "Polda Riau - Pekanbaru"),
        ("POLDA KEPULAUAN RIAU",                "POLDAKEPRI",    "Polda Kepri - Batam"),
        ("POLDA JAMBI",                         "POLDAJAMBI",    "Polda Jambi - Jambi"),
        ("POLDA BENGKULU",                      "POLDABENGKULU", "Polda Bengkulu - Bengkulu"),
        ("POLDA SUMATERA SELATAN",              "POLDASUMSEL",   "Polda Sumsel - Palembang"),
        ("POLDA KEPULAUAN BANGKA BELITUNG",     "POLDABABEL",    "Polda Babel - Pangkalpinang"),
        ("POLDA LAMPUNG",                       "POLDALAMPUNG",  "Polda Lampung - Bandar Lampung"),
        ("POLDA METRO JAYA",                    "POLDAMETRO",    "Polda Metro Jaya - Jakarta"),
        ("POLDA BANTEN",                        "POLDABANTEN",   "Polda Banten - Serang"),
        ("POLDA JAWA BARAT",                    "POLDAJABAR",    "Polda Jabar - Bandung"),
        ("POLDA JAWA TENGAH",                   "POLDAJATENG",   "Polda Jateng - Semarang"),
        ("POLDA DI YOGYAKARTA",                 "POLDADIY",      "Polda DIY - Yogyakarta"),
        ("POLDA JAWA TIMUR",                    "POLDAJATIM",    "Polda Jatim - Surabaya"),
        ("POLDA BALI",                          "POLDABALI",     "Polda Bali - Denpasar"),
        ("POLDA KALIMANTAN BARAT",              "POLDAKALBAR",   "Polda Kalbar - Pontianak"),
        ("POLDA KALIMANTAN TENGAH",             "POLDAKALTENG",  "Polda Kalteng - Palangka Raya"),
        ("POLDA KALIMANTAN SELATAN",            "POLDAKALSEL",   "Polda Kalsel - Banjarmasin"),
        ("POLDA KALIMANTAN TIMUR",              "POLDAKALTIM",   "Polda Kaltim - Balikpapan"),
        ("POLDA KALIMANTAN UTARA",              "POLDAKALTARA",  "Polda Kaltara - Tanjung Selor"),
        ("POLDA NUSA TENGGARA BARAT",           "POLDANTB",      "Polda NTB - Mataram"),
        ("POLDA NUSA TENGGARA TIMUR",           "POLDANTT",      "Polda NTT - Kupang"),
        ("POLDA SULAWESI UTARA",                "POLDASULUT",    "Polda Sulut - Manado"),
        ("POLDA GORONTALO",                     "POLDAGORONTALO","Polda Gorontalo - Gorontalo"),
        ("POLDA SULAWESI TENGAH",               "POLDASULTENG",  "Polda Sulteng - Palu"),
        ("POLDA SULAWESI TENGGARA",             "POLDASULTRA",   "Polda Sultra - Kendari"),
        ("POLDA SULAWESI SELATAN",              "POLDASULSEL",   "Polda Sulsel - Makassar"),
        ("POLDA SULAWESI BARAT",                "POLDASULBAR",   "Polda Sulbar - Mamuju"),
        ("POLDA MALUKU",                        "POLDAMALUKU",   "Polda Maluku - Ambon"),
        ("POLDA MALUKU UTARA",                  "POLDAMALUT",    "Polda Malut - Ternate"),
        ("POLDA PAPUA",                         "POLDAPAPUA",    "Polda Papua - Jayapura"),
        ("POLDA PAPUA BARAT",                   "POLDAPAPBAR",   "Polda Papua Barat - Manokwari"),
        ("POLDA PAPUA TENGAH",                  "POLDAPAPTENG",  "Polda Papua Tengah - Nabire"),
    ]

    satker_objs = {}
    for nama, kode, desk in SATKER_DATA:
        s = Satker(id=str(uuid.uuid4()), nama=nama, kode=kode, deskripsi=desk)
        db.add(s)
        satker_objs[kode] = s
    db.commit()
    for s in satker_objs.values():
        db.refresh(s)
    print(f"   OK  {len(satker_objs)} satuan kerja berhasil dibuat (Mabes + 34 Polda)")

    # ─────────────────────────────────────────────────────────────
    # [2/4] AKUN PENGGUNA
    # ─────────────────────────────────────────────────────────────
    print("\n[2/4] Membuat Akun Pengguna...")
    admin = User(
        id=str(uuid.uuid4()), username="admin.ssdm",
        email="admin@ssdm.polri.go.id",
        password_hash=hash_password("Admin@12345"),
        role=UserRole.ADMIN_SSDM,
        satker_id=satker_objs["SSDM"].id, is_active=True
    )
    op_metro = User(
        id=str(uuid.uuid4()), username="operator.metro",
        email="operator@poldametro.polri.go.id",
        password_hash=hash_password("Operator@123"),
        role=UserRole.OPERATOR_SATKER,
        satker_id=satker_objs["POLDAMETRO"].id, is_active=True
    )
    op_jabar = User(
        id=str(uuid.uuid4()), username="operator.jabar",
        email="operator@poldajabar.polri.go.id",
        password_hash=hash_password("Operator@123"),
        role=UserRole.OPERATOR_SATKER,
        satker_id=satker_objs["POLDAJABAR"].id, is_active=True
    )
    op_jatim = User(
        id=str(uuid.uuid4()), username="operator.jatim",
        email="operator@poldajatim.polri.go.id",
        password_hash=hash_password("Operator@123"),
        role=UserRole.OPERATOR_SATKER,
        satker_id=satker_objs["POLDAJATIM"].id, is_active=True
    )
    op_sulsel = User(
        id=str(uuid.uuid4()), username="operator.sulsel",
        email="operator@poldasulsel.polri.go.id",
        password_hash=hash_password("Operator@123"),
        role=UserRole.OPERATOR_SATKER,
        satker_id=satker_objs["POLDASULSEL"].id, is_active=True
    )
    db.add_all([admin, op_metro, op_jabar, op_jatim, op_sulsel])
    db.commit()
    print("   OK  admin.ssdm | operator.metro | operator.jabar | operator.jatim | operator.sulsel")

    # ─────────────────────────────────────────────────────────────
    # [3/4] PERSONEL
    # ─────────────────────────────────────────────────────────────
    print("\n[3/4] Membuat Data Personel...")
    METRO  = satker_objs["POLDAMETRO"].id
    JABAR  = satker_objs["POLDAJABAR"].id
    JATIM  = satker_objs["POLDAJATIM"].id
    SSDM   = satker_objs["SSDM"].id
    SULSEL = satker_objs["POLDASULSEL"].id
    SUMUT  = satker_objs["POLDASUMUT"].id

    p = [
        # Perwira Tinggi
        Personel(id=str(uuid.uuid4()), nama="IRJEN POL ANDI WIJAYA, S.H., M.H.", nrp_nip="72040217",
                 pangkat="IRJEN POL", tempat_lahir="Jakarta", tanggal_lahir=date(1971, 3, 15), satker_id=SSDM),
        # Perwira Menengah
        Personel(id=str(uuid.uuid4()), nama="KOMBES POL BUDI SANTOSO, S.I.K.", nrp_nip="82050318",
                 pangkat="KOMBES POL", tempat_lahir="Surabaya", tanggal_lahir=date(1978, 6, 22), satker_id=METRO),
        Personel(id=str(uuid.uuid4()), nama="AKBP CITRA DEWI, S.H.", nrp_nip="90060419",
                 pangkat="AKBP", tempat_lahir="Bandung", tanggal_lahir=date(1985, 9, 10), satker_id=METRO),
        Personel(id=str(uuid.uuid4()), nama="KOMPOL DEDI KURNIAWAN, S.I.K.", nrp_nip="93070520",
                 pangkat="KOMPOL", tempat_lahir="Bandung", tanggal_lahir=date(1988, 12, 5), satker_id=JABAR),
        # Perwira Pertama
        Personel(id=str(uuid.uuid4()), nama="AKP EKO PRASETYO, S.T.K.", nrp_nip="96080621",
                 pangkat="AKP", tempat_lahir="Semarang", tanggal_lahir=date(1991, 4, 18), satker_id=JABAR),
        Personel(id=str(uuid.uuid4()), nama="IPTU FAUZI RAHMAN", nrp_nip="98090722",
                 pangkat="IPTU", tempat_lahir="Malang", tanggal_lahir=date(1994, 7, 30), satker_id=JATIM),
        Personel(id=str(uuid.uuid4()), nama="IPDA GRACE TAMAELA", nrp_nip="00100823",
                 pangkat="IPDA", tempat_lahir="Ambon", tanggal_lahir=date(1997, 11, 12), satker_id=JATIM),
        # Bintara
        Personel(id=str(uuid.uuid4()), nama="AIPTU HENDRA GUNAWAN", nrp_nip="85110924",
                 pangkat="AIPTU", tempat_lahir="Makassar", tanggal_lahir=date(1982, 2, 20), satker_id=SULSEL),
        Personel(id=str(uuid.uuid4()), nama="BRIGADIR IKA PERMATASARI", nrp_nip="95121025",
                 pangkat="BRIGADIR", tempat_lahir="Medan", tanggal_lahir=date(1992, 8, 5), satker_id=SUMUT),
        # Tamtama
        Personel(id=str(uuid.uuid4()), nama="BHARADA JOKO SUSILO", nrp_nip="05011126",
                 pangkat="BHARADA", tempat_lahir="Yogyakarta", tanggal_lahir=date(2002, 3, 17), satker_id=METRO),
    ]
    db.add_all(p)
    db.commit()
    for pp in p:
        db.refresh(pp)
    print(f"   OK  {len(p)} personel berhasil dibuat (Pati, Pamen, Pama, Bintara, Tamtama)")

    # ─────────────────────────────────────────────────────────────
    # [4/4] RIWAYAT JABATAN
    # ─────────────────────────────────────────────────────────────
    print("\n[4/4] Membuat Riwayat Jabatan...")
    rj_list = [
        # IRJEN ANDI (SSDM)
        RiwayatJabatan(id=str(uuid.uuid4()), personel_id=p[0].id, jabatan="KASUBDIT BINKAR",
            satuan_kerja="DITPERS POLRI", fungsi="PEMBINAAN KARIER",
            tanggal_mulai=date(2005, 1, 1), tanggal_berakhir=date(2010, 12, 31),
            nivelering_jabatan="ES-III/A", status_jabatan=StatusJabatan.NON_AKTIF, keterangan="Jabatan awal"),
        RiwayatJabatan(id=str(uuid.uuid4()), personel_id=p[0].id, jabatan="KAROPERS SSDM POLRI",
            satuan_kerja="SSDM POLRI", fungsi="OPERASIONAL SDM",
            tanggal_mulai=date(2011, 1, 1), tanggal_berakhir=date(2016, 12, 31),
            nivelering_jabatan="ES-II/A", status_jabatan=StatusJabatan.NON_AKTIF, keterangan="Naik eselon II"),
        RiwayatJabatan(id=str(uuid.uuid4()), personel_id=p[0].id, jabatan="WAKAPOLDA JAWA BARAT",
            satuan_kerja="POLDA JAWA BARAT", fungsi="PIMPINAN",
            tanggal_mulai=date(2017, 1, 1), tanggal_berakhir=date(2020, 12, 31),
            nivelering_jabatan="ES-I/B", status_jabatan=StatusJabatan.NON_AKTIF, keterangan=""),
        RiwayatJabatan(id=str(uuid.uuid4()), personel_id=p[0].id, jabatan="KAPOLDA SULAWESI SELATAN",
            satuan_kerja="POLDA SULAWESI SELATAN", fungsi="PIMPINAN",
            tanggal_mulai=date(2021, 1, 1), tanggal_berakhir=date(2023, 12, 31),
            nivelering_jabatan="ES-I/A", status_jabatan=StatusJabatan.NON_AKTIF, keterangan=""),
        RiwayatJabatan(id=str(uuid.uuid4()), personel_id=p[0].id, jabatan="ASISTEN KAPOLRI BIDANG SDM",
            satuan_kerja="MABES POLRI", fungsi="MANAJEMEN SDM POLRI",
            tanggal_mulai=date(2024, 1, 1), tanggal_berakhir=None,
            nivelering_jabatan="ES-I/A", status_jabatan=StatusJabatan.AKTIF, keterangan="Jabatan saat ini"),

        # KOMBES BUDI (Metro)
        RiwayatJabatan(id=str(uuid.uuid4()), personel_id=p[1].id, jabatan="KASAT RESKRIM",
            satuan_kerja="POLRES JAKARTA SELATAN", fungsi="RESERSE KRIMINAL",
            tanggal_mulai=date(2012, 3, 1), tanggal_berakhir=date(2016, 2, 28),
            nivelering_jabatan="ES-IV/A", status_jabatan=StatusJabatan.NON_AKTIF, keterangan=""),
        RiwayatJabatan(id=str(uuid.uuid4()), personel_id=p[1].id, jabatan="WAKAPOLRES METRO JAKARTA SELATAN",
            satuan_kerja="POLRES METRO JAKARTA SELATAN", fungsi="OPERASIONAL",
            tanggal_mulai=date(2016, 3, 1), tanggal_berakhir=date(2020, 2, 28),
            nivelering_jabatan="ES-III/B", status_jabatan=StatusJabatan.NON_AKTIF, keterangan=""),
        RiwayatJabatan(id=str(uuid.uuid4()), personel_id=p[1].id, jabatan="DIRRESKRIMUM POLDA METRO JAYA",
            satuan_kerja="POLDA METRO JAYA", fungsi="RESERSE KRIMINAL UMUM",
            tanggal_mulai=date(2020, 3, 1), tanggal_berakhir=None,
            nivelering_jabatan="ES-II/B", status_jabatan=StatusJabatan.AKTIF, keterangan="Jabatan saat ini"),

        # AKBP CITRA (Metro)
        RiwayatJabatan(id=str(uuid.uuid4()), personel_id=p[2].id, jabatan="KAPOLSEK CILINCING",
            satuan_kerja="POLRES METRO JAKARTA UTARA", fungsi="OPERASIONAL",
            tanggal_mulai=date(2018, 6, 1), tanggal_berakhir=date(2022, 5, 31),
            nivelering_jabatan="ES-IV/A", status_jabatan=StatusJabatan.NON_AKTIF, keterangan=""),
        RiwayatJabatan(id=str(uuid.uuid4()), personel_id=p[2].id, jabatan="KABAG OPS POLRES METRO JAKARTA UTARA",
            satuan_kerja="POLRES METRO JAKARTA UTARA", fungsi="OPERASIONAL",
            tanggal_mulai=date(2022, 6, 1), tanggal_berakhir=None,
            nivelering_jabatan="ES-III/B", status_jabatan=StatusJabatan.AKTIF, keterangan=""),

        # KOMPOL DEDI (Jabar)
        RiwayatJabatan(id=str(uuid.uuid4()), personel_id=p[3].id, jabatan="KASAT LANTAS POLRES BANDUNG",
            satuan_kerja="POLRES BANDUNG", fungsi="LALU LINTAS",
            tanggal_mulai=date(2018, 1, 1), tanggal_berakhir=date(2022, 12, 31),
            nivelering_jabatan="ES-IV/A", status_jabatan=StatusJabatan.NON_AKTIF, keterangan=""),
        RiwayatJabatan(id=str(uuid.uuid4()), personel_id=p[3].id, jabatan="KAPOLSEK COBLONG",
            satuan_kerja="POLRESTABES BANDUNG", fungsi="OPERASIONAL KEWILAYAHAN",
            tanggal_mulai=date(2023, 1, 1), tanggal_berakhir=None,
            nivelering_jabatan="ES-IV/A", status_jabatan=StatusJabatan.AKTIF, keterangan=""),

        # AKP EKO (Jabar)
        RiwayatJabatan(id=str(uuid.uuid4()), personel_id=p[4].id, jabatan="KANIT RESKRIM",
            satuan_kerja="POLSEK BANDUNG WETAN", fungsi="RESERSE KRIMINAL",
            tanggal_mulai=date(2020, 7, 1), tanggal_berakhir=date(2023, 6, 30),
            nivelering_jabatan="ES-V/A", status_jabatan=StatusJabatan.NON_AKTIF, keterangan=""),
        RiwayatJabatan(id=str(uuid.uuid4()), personel_id=p[4].id, jabatan="KASAT RESKRIM POLRES CIMAHI",
            satuan_kerja="POLRES CIMAHI", fungsi="RESERSE KRIMINAL",
            tanggal_mulai=date(2023, 7, 1), tanggal_berakhir=None,
            nivelering_jabatan="ES-IV/A", status_jabatan=StatusJabatan.AKTIF, keterangan="Promosi"),

        # IPTU FAUZI (Jatim)
        RiwayatJabatan(id=str(uuid.uuid4()), personel_id=p[5].id, jabatan="KANIT INTELKAM",
            satuan_kerja="POLRES MALANG", fungsi="INTELIJEN DAN KEAMANAN",
            tanggal_mulai=date(2022, 3, 1), tanggal_berakhir=None,
            nivelering_jabatan="ES-V/A", status_jabatan=StatusJabatan.AKTIF, keterangan="Jabatan pertama"),

        # IPDA GRACE (Jatim)
        RiwayatJabatan(id=str(uuid.uuid4()), personel_id=p[6].id, jabatan="KANIT BINMAS",
            satuan_kerja="POLRES SURABAYA", fungsi="PEMBINAAN MASYARAKAT",
            tanggal_mulai=date(2023, 8, 1), tanggal_berakhir=None,
            nivelering_jabatan="ES-V/B", status_jabatan=StatusJabatan.AKTIF, keterangan="Jabatan pertama"),

        # AIPTU HENDRA (Sulsel)
        RiwayatJabatan(id=str(uuid.uuid4()), personel_id=p[7].id, jabatan="ANGGOTA SAMAPTA",
            satuan_kerja="POLRES MAKASSAR", fungsi="SAMAPTA",
            tanggal_mulai=date(2005, 1, 1), tanggal_berakhir=date(2015, 12, 31),
            nivelering_jabatan="NON-ES", status_jabatan=StatusJabatan.NON_AKTIF, keterangan=""),
        RiwayatJabatan(id=str(uuid.uuid4()), personel_id=p[7].id, jabatan="BAMIN POLDA SULSEL",
            satuan_kerja="POLDA SULAWESI SELATAN", fungsi="ADMINISTRASI",
            tanggal_mulai=date(2016, 1, 1), tanggal_berakhir=None,
            nivelering_jabatan="NON-ES", status_jabatan=StatusJabatan.AKTIF, keterangan=""),

        # BRIGADIR IKA (Sumut)
        RiwayatJabatan(id=str(uuid.uuid4()), personel_id=p[8].id, jabatan="ANGGOTA LANTAS",
            satuan_kerja="POLRES MEDAN", fungsi="LALU LINTAS",
            tanggal_mulai=date(2015, 6, 1), tanggal_berakhir=None,
            nivelering_jabatan="NON-ES", status_jabatan=StatusJabatan.AKTIF, keterangan="Jabatan pertama"),

        # BHARADA JOKO (Metro)
        RiwayatJabatan(id=str(uuid.uuid4()), personel_id=p[9].id, jabatan="ANGGOTA SAT SABHARA",
            satuan_kerja="POLRES METRO JAKARTA BARAT", fungsi="KETERTIBAN DAN KEAMANAN",
            tanggal_mulai=date(2024, 3, 1), tanggal_berakhir=None,
            nivelering_jabatan="NON-ES", status_jabatan=StatusJabatan.AKTIF, keterangan="Jabatan pertama"),
    ]
    db.add_all(rj_list)
    db.commit()
    print(f"   OK  {len(rj_list)} riwayat jabatan berhasil dibuat")

    print("\n" + "=" * 60)
    print("SEEDING SELESAI!")
    print("=" * 60)
    print("\nAkun login:")
    print("  admin.ssdm     | Admin@12345  | ADMIN_SSDM")
    print("  operator.metro | Operator@123 | OPERATOR_SATKER")
    print("  operator.jabar | Operator@123 | OPERATOR_SATKER")
    print("  operator.jatim | Operator@123 | OPERATOR_SATKER")
    print("  operator.sulsel| Operator@123 | OPERATOR_SATKER")
    print("\nSwagger UI : http://localhost:8000/docs")
    print("Web UI     : http://localhost:8000/app/")

except Exception as exc:
    print(f"\nError saat seeding: {exc}")
    db.rollback()
    raise
finally:
    db.close()
