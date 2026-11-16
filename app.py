"""
Kütüphane Kataloğu - Flask + SQLite Örnek Uygulaması
Veri Tabanı Yönetim Sistemleri dersi için hazırlanmıştır.

Temel CRUD (Create, Read, Update, Delete) ve Arama işlemlerini
parametreli SQL sorguları (sqlite3) kullanarak gösterir.
"""

import os
import sqlite3
from flask import Flask, flash, g, redirect, render_template, request, url_for

from init_db import DB_PATH, veri_tabani_olustur

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "kutuphane-vtys-ornek-anahtar")

SAYFA_BASINA_KAYIT = 20

KATEGORILER = [
    "Veri Tabanı ve Yazılım",
    "Bilgi ve Belge Yönetimi",
    "Türk Edebiyatı",
    "Dünya Edebiyatı",
    "Tarih",
    "Felsefe ve Sosyoloji",
    "Bilim ve Teknoloji",
    "Araştırma Yöntemleri",
]

SIRALAMA_SECENEKLERI = {
    "id_desc": ("Son Eklenenler", "id DESC"),
    "baslik_asc": ("Kitap Adı (A-Z)", "baslik COLLATE NOCASE ASC"),
    "yazar_asc": ("Yazar Adı (A-Z)", "yazar COLLATE NOCASE ASC"),
    "yil_desc": ("Yayın Yılı (Yeniden Eskiye)", "yayin_yili DESC, id DESC"),
    "yil_asc": ("Yayın Yılı (Eskiden Yeniye)", "yayin_yili ASC, id ASC"),
}


def get_db() -> sqlite3.Connection:
    """İstek boyunca geçerli bir SQLite bağlantısı döndürür."""
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    """İstek tamamlandığında SQLite bağlantısını kapatır."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def formu_dogrula(form_data: dict) -> tuple[dict, list[str]]:
    """Kitap ekleme/güncelleme formundaki alanları doğrular."""
    hatalar = []
    veriler = {
        "isbn": form_data.get("isbn", "").strip(),
        "baslik": form_data.get("baslik", "").strip(),
        "yazar": form_data.get("yazar", "").strip(),
        "yayinevi": form_data.get("yayinevi", "").strip(),
        "yayin_yili": form_data.get("yayin_yili", "").strip(),
        "kategori": form_data.get("kategori", "").strip(),
        "raf_kodu": form_data.get("raf_kodu", "").strip(),
        "durum": form_data.get("durum", "Mevcut").strip(),
    }

    if not veriler["isbn"]:
        hatalar.append("ISBN alanı boş bırakılamaz.")
    if not veriler["baslik"]:
        hatalar.append("Kitap adı boş bırakılamaz.")
    if not veriler["yazar"]:
        hatalar.append("Yazar adı boş bırakılamaz.")
    if not veriler["yayinevi"]:
        hatalar.append("Yayınevi boş bırakılamaz.")
    if not veriler["kategori"]:
        hatalar.append("Kategori seçilmelidir.")
    if not veriler["raf_kodu"]:
        hatalar.append("Raf kodu boş bırakılamaz.")

    try:
        yil = int(veriler["yayin_yili"])
        if yil < 1400 or yil > 2100:
            hatalar.append("Yayın yılı 1400 ile 2100 arasında olmalıdır.")
        veriler["yayin_yili_int"] = yil
    except ValueError:
        hatalar.append("Yayın yılı geçerli bir tam sayı olmalıdır.")
        veriler["yayin_yili_int"] = None

    if veriler["durum"] not in ("Mevcut", "Ödünçte"):
        veriler["durum"] = "Mevcut"

    return veriler, hatalar


# ---------------------------------------------------------------------------
# READ (Listeleme ve Arama)
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    db = get_db()

    arama = request.args.get("q", "").strip()
    kategori = request.args.get("kategori", "").strip()
    durum = request.args.get("durum", "").strip()
    sirala = request.args.get("sirala", "id_desc").strip()
    if sirala not in SIRALAMA_SECENEKLERI:
        sirala = "id_desc"

    try:
        sayfa = max(1, int(request.args.get("sayfa", 1)))
    except ValueError:
        sayfa = 1

    # Dinamik WHERE koşulları (SQL Injection'a karşı parametreli sorgu)
    kosullar = []
    parametreler = []

    if arama:
        kosullar.append(
            "(baslik LIKE ? OR yazar LIKE ? OR isbn LIKE ? OR yayinevi LIKE ? OR raf_kodu LIKE ?)"
        )
        arama_kalibi = f"%{arama}%"
        parametreler.extend([arama_kalibi] * 5)

    if kategori:
        kosullar.append("kategori = ?")
        parametreler.append(kategori)

    if durum in ("Mevcut", "Ödünçte"):
        kosullar.append("durum = ?")
        parametreler.append(durum)

    where_sql = f"WHERE {' AND '.join(kosullar)}" if kosullar else ""
    order_sql = SIRALAMA_SECENEKLERI[sirala][1]

    # Filtrelenmiş toplam kayıt sayısı
    toplam_filtrelenen = db.execute(
        f"SELECT COUNT(*) FROM kitaplar {where_sql}",
        parametreler,
    ).fetchone()[0]

    toplam_sayfa = max(1, (toplam_filtrelenen + SAYFA_BASINA_KAYIT - 1) // SAYFA_BASINA_KAYIT)
    if sayfa > toplam_sayfa:
        sayfa = toplam_sayfa

    offset = (sayfa - 1) * SAYFA_BASINA_KAYIT

    # Sayfalanmış kitap kayıtlarını getir
    kitaplar = db.execute(
        f"""
        SELECT id, isbn, baslik, yazar, yayinevi, yayin_yili, kategori, raf_kodu, durum, eklenme_tarihi
        FROM kitaplar
        {where_sql}
        ORDER BY {order_sql}
        LIMIT ? OFFSET ?
        """,
        parametreler + [SAYFA_BASINA_KAYIT, offset],
    ).fetchall()

    # Genel özet istatistikler
    istatistik = db.execute(
        """
        SELECT
            COUNT(*) AS toplam,
            SUM(CASE WHEN durum = 'Mevcut' THEN 1 ELSE 0 END) AS mevcut,
            SUM(CASE WHEN durum = 'Ödünçte' THEN 1 ELSE 0 END) AS odunc
        FROM kitaplar
        """
    ).fetchone()

    # Veri tabanındaki mevcut kategorileri getir
    kategoriler_db = [
        satir["kategori"]
        for satir in db.execute(
            "SELECT DISTINCT kategori FROM kitaplar ORDER BY kategori COLLATE NOCASE ASC"
        ).fetchall()
    ]

    return render_template(
        "index.html",
        kitaplar=kitaplar,
        arama=arama,
        secili_kategori=kategori,
        secili_durum=durum,
        secili_sirala=sirala,
        sirala_secenekleri=SIRALAMA_SECENEKLERI,
        kategoriler=kategoriler_db or KATEGORILER,
        istatistik=istatistik,
        toplam_filtrelenen=toplam_filtrelenen,
        sayfa=sayfa,
        toplam_sayfa=toplam_sayfa,
    )


# ---------------------------------------------------------------------------
# CREATE (Yeni Kitap Ekleme)
# ---------------------------------------------------------------------------
@app.route("/ekle", methods=["GET", "POST"])
def kitap_ekle():
    if request.method == "POST":
        veriler, hatalar = formu_dogrula(request.form)

        if not hatalar:
            db = get_db()
            try:
                db.execute(
                    """
                    INSERT INTO kitaplar (isbn, baslik, yazar, yayinevi, yayin_yili, kategori, raf_kodu, durum)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        veriler["isbn"],
                        veriler["baslik"],
                        veriler["yazar"],
                        veriler["yayinevi"],
                        veriler["yayin_yili_int"],
                        veriler["kategori"],
                        veriler["raf_kodu"],
                        veriler["durum"],
                    ),
                )
                db.commit()
                flash(f"'{veriler['baslik']}' kataloğa başarıyla eklendi.", "success")
                return redirect(url_for("index"))
            except sqlite3.IntegrityError:
                hatalar.append(
                    f"'{veriler['isbn']}' ISBN numarası veri tabanında zaten kayıtlı."
                )

        for hata in hatalar:
            flash(hata, "error")

        return render_template(
            "form.html",
            islem="ekle",
            kitap=veriler,
            kategoriler=KATEGORILER,
        )

    return render_template(
        "form.html",
        islem="ekle",
        kitap={"durum": "Mevcut"},
        kategoriler=KATEGORILER,
    )


# ---------------------------------------------------------------------------
# UPDATE (Kitap Güncelleme)
# ---------------------------------------------------------------------------
@app.route("/duzenle/<int:kitap_id>", methods=["GET", "POST"])
def kitap_duzenle(kitap_id: int):
    db = get_db()
    mevcut_kitap = db.execute(
        "SELECT * FROM kitaplar WHERE id = ?",
        (kitap_id,),
    ).fetchone()

    if mevcut_kitap is None:
        flash("Düzenlenmek istenen kitap kaydı bulunamadı.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        veriler, hatalar = formu_dogrula(request.form)

        if not hatalar:
            try:
                db.execute(
                    """
                    UPDATE kitaplar
                    SET isbn = ?, baslik = ?, yazar = ?, yayinevi = ?,
                        yayin_yili = ?, kategori = ?, raf_kodu = ?, durum = ?
                    WHERE id = ?
                    """,
                    (
                        veriler["isbn"],
                        veriler["baslik"],
                        veriler["yazar"],
                        veriler["yayinevi"],
                        veriler["yayin_yili_int"],
                        veriler["kategori"],
                        veriler["raf_kodu"],
                        veriler["durum"],
                        kitap_id,
                    ),
                )
                db.commit()
                flash(f"'{veriler['baslik']}' kaydı güncellendi.", "success")
                return redirect(url_for("index"))
            except sqlite3.IntegrityError:
                hatalar.append(
                    f"'{veriler['isbn']}' ISBN numarası başka bir kitapta kullanılıyor."
                )

        for hata in hatalar:
            flash(hata, "error")

        veriler["id"] = kitap_id
        return render_template(
            "form.html",
            islem="duzenle",
            kitap=veriler,
            kategoriler=KATEGORILER,
        )

    return render_template(
        "form.html",
        islem="duzenle",
        kitap=mevcut_kitap,
        kategoriler=KATEGORILER,
    )


# ---------------------------------------------------------------------------
# UPDATE (Hızlı Durum Değiştirme: Mevcut <-> Ödünçte)
# ---------------------------------------------------------------------------
@app.route("/durum/<int:kitap_id>", methods=["POST"])
def durum_degistir(kitap_id: int):
    db = get_db()
    kitap = db.execute(
        "SELECT id, baslik, durum FROM kitaplar WHERE id = ?",
        (kitap_id,),
    ).fetchone()

    if kitap is None:
        flash("Kitap kaydı bulunamadı.", "error")
    else:
        yeni_durum = "Ödünçte" if kitap["durum"] == "Mevcut" else "Mevcut"
        db.execute(
            "UPDATE kitaplar SET durum = ? WHERE id = ?",
            (yeni_durum, kitap_id),
        )
        db.commit()
        flash(f"'{kitap['baslik']}' durumu '{yeni_durum}' olarak güncellendi.", "success")

    return redirect(request.referrer or url_for("index"))


# ---------------------------------------------------------------------------
# DELETE (Kitap Silme)
# ---------------------------------------------------------------------------
@app.route("/sil/<int:kitap_id>", methods=["POST"])
def kitap_sil(kitap_id: int):
    db = get_db()
    kitap = db.execute(
        "SELECT id, baslik FROM kitaplar WHERE id = ?",
        (kitap_id,),
    ).fetchone()

    if kitap is None:
        flash("Silinmek istenen kitap kaydı bulunamadı.", "error")
    else:
        db.execute("DELETE FROM kitaplar WHERE id = ?", (kitap_id,))
        db.commit()
        flash(f"'{kitap['baslik']}' katalogdan silindi.", "success")

    return redirect(request.referrer or url_for("index"))


if __name__ == "__main__":
    # Veri tabanı yoksa otomatik oluştur ve 100 örnek kaydı yükle
    if not os.path.exists(DB_PATH):
        veri_tabani_olustur()
    app.run(debug=True, port=5000)
