"""
Kütüphane Kataloğu - Veri Tabanı Başlatma ve Örnek Veri Yükleme Betiği
Veri Tabanı Yönetim Sistemleri dersi için hazırlanmıştır.

Kullanım:
    python init_db.py           # Veri tabanı yoksa oluşturur ve 100 örnek kayıt ekler
    python init_db.py --reset   # Mevcut tabloyu sıfırlar ve 100 örnek kaydı yeniden yükler
"""

import argparse
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "kutuphane.db")

# 100 adet örnek kütüphane kaydı:
# (isbn, baslik, yazar, yayinevi, yayin_yili, kategori, raf_kodu, durum)
ORNEK_KITAPLAR = [
    # --- Veri Tabanı, Bilgisayar ve Bilgi Bilimi (20) ---
    ("978-0133970777", "Fundamentals of Database Systems", "Ramez Elmasri, Shamkant B. Navathe", "Pearson", 2016, "Veri Tabanı ve Yazılım", "QA76.9.D3 E46", "Mevcut"),
    ("978-1260084504", "Database System Concepts", "Abraham Silberschatz, Henry F. Korth, S. Sudarshan", "McGraw-Hill", 2019, "Veri Tabanı ve Yazılım", "QA76.9.D3 S55", "Ödünçte"),
    ("978-0321197849", "An Introduction to Database Systems", "C. J. Date", "Addison-Wesley", 2004, "Veri Tabanı ve Yazılım", "QA76.9.D3 D38", "Mevcut"),
    ("978-1449373320", "Designing Data-Intensive Applications", "Martin Kleppmann", "O'Reilly Media", 2017, "Veri Tabanı ve Yazılım", "QA76.9.D3 K54", "Ödünçte"),
    ("978-9756797860", "Veri Tabanı Yönetim Sistemleri", "Mithat Uysal", "Papatya Yayıncılık", 2018, "Veri Tabanı ve Yazılım", "QA76.9.D3 U97", "Mevcut"),
    ("978-6053205692", "SQL ve İlişkisel Veri Tabanı Tasarımı", "Ahmet Yılmaz", "Seçkin Yayıncılık", 2021, "Veri Tabanı ve Yazılım", "QA76.73.S67 Y55", "Mevcut"),
    ("978-1491950357", "Learning SQL", "Alan Beaulieu", "O'Reilly Media", 2020, "Veri Tabanı ve Yazılım", "QA76.73.S67 B43", "Mevcut"),
    ("978-1491985571", "Flask Web Development", "Miguel Grinberg", "O'Reilly Media", 2018, "Veri Tabanı ve Yazılım", "QA76.73.P98 G75", "Mevcut"),
    ("978-1593279288", "Python Crash Course", "Eric Matthes", "No Starch Press", 2023, "Veri Tabanı ve Yazılım", "QA76.73.P98 M38", "Ödünçte"),
    ("978-0262046305", "Introduction to Algorithms", "Thomas H. Cormen, Charles E. Leiserson", "MIT Press", 2022, "Veri Tabanı ve Yazılım", "QA76.6 C67", "Mevcut"),
    ("978-0132350884", "Clean Code: A Handbook of Agile Software Craftsmanship", "Robert C. Martin", "Prentice Hall", 2008, "Veri Tabanı ve Yazılım", "QA76.76.D47 M37", "Mevcut"),
    ("978-0135957059", "The Pragmatic Programmer", "David Thomas, Andrew Hunt", "Addison-Wesley", 2019, "Veri Tabanı ve Yazılım", "QA76.6 T46", "Mevcut"),
    ("978-1492041139", "Data Science from Scratch", "Joel Grus", "O'Reilly Media", 2019, "Veri Tabanı ve Yazılım", "QA76.9.D343 G78", "Mevcut"),
    ("978-1491957660", "Python for Data Analysis", "Wes McKinney", "O'Reilly Media", 2022, "Veri Tabanı ve Yazılım", "QA76.73.P98 M35", "Mevcut"),
    ("978-0134685991", "Effective Java", "Joshua Bloch", "Addison-Wesley", 2018, "Veri Tabanı ve Yazılım", "QA76.73.J38 B56", "Mevcut"),
    ("978-9750406515", "Python ile Veri Bilimi ve Yapay Zeka", "Mustafa Akgül", "Kodlab", 2022, "Veri Tabanı ve Yazılım", "Q335 A34", "Mevcut"),
    ("978-0262035613", "Deep Learning", "Ian Goodfellow, Yoshua Bengio, Aaron Courville", "MIT Press", 2016, "Veri Tabanı ve Yazılım", "Q325.5 G66", "Ödünçte"),
    ("978-1098125974", "Hands-On Machine Learning", "Aurélien Géron", "O'Reilly Media", 2022, "Veri Tabanı ve Yazılım", "Q325.5 G47", "Mevcut"),
    ("978-0131103627", "The C Programming Language", "Brian W. Kernighan, Dennis M. Ritchie", "Prentice Hall", 1988, "Veri Tabanı ve Yazılım", "QA76.73.C15 K47", "Mevcut"),
    ("978-0201633610", "Design Patterns", "Erich Gamma, Richard Helm, Ralph Johnson", "Addison-Wesley", 1994, "Veri Tabanı ve Yazılım", "QA76.64 D47", "Mevcut"),

    # --- Bilgi ve Belge Yönetimi / Kütüphanecilik (15) ---
    ("978-9754912340", "Bilgi ve Belge Yönetimi Kuram ve Uygulamaları", "Yaşar Tonta", "Hacettepe Üniversitesi Yayınları", 2019, "Bilgi ve Belge Yönetimi", "Z665 T66", "Mevcut"),
    ("978-9756516126", "Kütüphanecilik ve Bilgi Bilimine Giriş", "İrfan Çakın", "Türk Kütüphaneciler Derneği", 2011, "Bilgi ve Belge Yönetimi", "Z665 C35", "Mevcut"),
    ("978-9756516201", "Bilgi Erişim Sistemleri ve Arama Motorları", "Umut Al", "Türk Kütüphaneciler Derneği", 2015, "Bilgi ve Belge Yönetimi", "Z699 A4", "Mevcut"),
    ("978-9754914108", "Açık Erişim ve Kurumsal Arşivler", "Orçun Madran", "Hacettepe Üniversitesi Yayınları", 2020, "Bilgi ve Belge Yönetimi", "Z674.75 M33", "Mevcut"),
    ("978-1555708535", "Foundations of Library and Information Science", "Richard E. Rubin", "ALA Neal-Schuman", 2020, "Bilgi ve Belge Yönetimi", "Z665 R83", "Mevcut"),
    ("978-1783301065", "Introduction to Information Science", "David Bawden, Lyn Robinson", "Facet Publishing", 2022, "Bilgi ve Belge Yönetimi", "Z665 B39", "Ödünçte"),
    ("978-0838914014", "Metadata", "Marcia Lei Zeng, Jian Qin", "ALA Neal-Schuman", 2022, "Bilgi ve Belge Yönetimi", "Z666.7 Z46", "Mevcut"),
    ("978-1440861536", "The Organization of Information", "Daniel N. Joudrey, Arlene G. Taylor", "Libraries Unlimited", 2017, "Bilgi ve Belge Yönetimi", "Z666.5 T39", "Mevcut"),
    ("978-9751738905", "Arşivcilik Terimleri Sözlüğü", "Devlet Arşivleri Genel Müdürlüğü", "Devlet Arşivleri Yayınları", 2016, "Bilgi ve Belge Yönetimi", "CD945 A77", "Mevcut"),
    ("978-6055091231", "Belge Yönetimi ve Elektronik Arşivleme", "Fahrettin Özdemirci", "Ankara Üniversitesi Basımevi", 2018, "Bilgi ve Belge Yönetimi", "CD974.4 O93", "Mevcut"),
    ("978-0262535205", "Information Architecture for the Web and Beyond", "Louis Rosenfeld, Peter Morville", "O'Reilly Media", 2015, "Bilgi ve Belge Yönetimi", "TK5105.888 R67", "Mevcut"),
    ("978-0199567935", "The Information: A History, a Theory, a Flood", "James Gleick", "Pantheon Books", 2011, "Bilgi ve Belge Yönetimi", "Q360 G54", "Mevcut"),
    ("978-6059850124", "Kütüphane ve Arşivlerde Koruma ve Restorasyon", "Nilüfer Kızıltan", "Kültür Bakanlığı Yayınları", 2017, "Bilgi ve Belge Yönetimi", "Z701 K59", "Mevcut"),
    ("978-1555709877", "Digital Libraries: Principles and Practice", "G. G. Chowdhury", "Facet Publishing", 2018, "Bilgi ve Belge Yönetimi", "ZA4080 C46", "Mevcut"),
    ("978-9750521232", "Kitabın Tarihi ve Okuma Kültürü", "Alberto Manguel", "Yapı Kredi Yayınları", 2017, "Bilgi ve Belge Yönetimi", "Z1003 M36", "Ödünçte"),

    # --- Türk Edebiyatı (20) ---
    ("978-9750807145", "İnce Memed 1", "Yaşar Kemal", "Yapı Kredi Yayınları", 2004, "Türk Edebiyatı", "PL248.Y3 I53", "Mevcut"),
    ("978-9750807152", "İnce Memed 2", "Yaşar Kemal", "Yapı Kredi Yayınları", 2004, "Türk Edebiyatı", "PL248.Y3 I54", "Mevcut"),
    ("978-9753638029", "Kürk Mantolu Madonna", "Sabahattin Ali", "Yapı Kredi Yayınları", 1998, "Türk Edebiyatı", "PL248.S23 K87", "Ödünçte"),
    ("978-9753638036", "İçimizdeki Şeytan", "Sabahattin Ali", "Yapı Kredi Yayınları", 1999, "Türk Edebiyatı", "PL248.S23 I35", "Mevcut"),
    ("978-9753638043", "Kuyucaklı Yusuf", "Sabahattin Ali", "Yapı Kredi Yayınları", 1999, "Türk Edebiyatı", "PL248.S23 K89", "Mevcut"),
    ("978-9754700114", "Tutunamayanlar", "Oğuz Atay", "İletişim Yayınları", 2000, "Türk Edebiyatı", "PL248.A77 T88", "Ödünçte"),
    ("978-9754700121", "Tehlikeli Oyunlar", "Oğuz Atay", "İletişim Yayınları", 2001, "Türk Edebiyatı", "PL248.A77 T44", "Mevcut"),
    ("978-9759954505", "Saatleri Ayarlama Enstitüsü", "Ahmet Hamdi Tanpınar", "Dergah Yayınları", 2014, "Türk Edebiyatı", "PL248.T24 S23", "Mevcut"),
    ("978-9759954512", "Huzur", "Ahmet Hamdi Tanpınar", "Dergah Yayınları", 2014, "Türk Edebiyatı", "PL248.T24 H89", "Mevcut"),
    ("978-9750738609", "Aylak Adam", "Yusuf Atılgan", "Can Yayınları", 2017, "Türk Edebiyatı", "PL248.A76 A95", "Mevcut"),
    ("978-9750738616", "Anayurt Oteli", "Yusuf Atılgan", "Can Yayınları", 2017, "Türk Edebiyatı", "PL248.A76 A53", "Mevcut"),
    ("978-9750826115", "Masumiyet Müzesi", "Orhan Pamuk", "Yapı Kredi Yayınları", 2013, "Türk Edebiyatı", "PL248.P34 M37", "Mevcut"),
    ("978-9750826122", "Benim Adım Kırmızı", "Orhan Pamuk", "Yapı Kredi Yayınları", 2013, "Türk Edebiyatı", "PL248.P34 B46", "Mevcut"),
    ("978-9750826139", "Kara Kitap", "Orhan Pamuk", "Yapı Kredi Yayınları", 2013, "Türk Edebiyatı", "PL248.P34 K37", "Mevcut"),
    ("978-9750719387", "Çalıkuşu", "Reşat Nuri Güntekin", "İnkılap Kitabevi", 2015, "Türk Edebiyatı", "PL248.G84 C35", "Mevcut"),
    ("978-9750719394", "Yaprak Dökümü", "Reşat Nuri Güntekin", "İnkılap Kitabevi", 2015, "Türk Edebiyatı", "PL248.G84 Y37", "Mevcut"),
    ("978-9750819032", "Bereketli Topraklar Üzerinde", "Orhan Kemal", "Everest Yayınları", 2012, "Türk Edebiyatı", "PL248.K46 B47", "Mevcut"),
    ("978-9750731105", "Puslu Kıtalar Atlası", "İhsan Oktay Anar", "İletişim Yayınları", 2016, "Türk Edebiyatı", "PL248.A53 P87", "Ödünçte"),
    ("978-9754705201", "Sevgili Arsız Ölüm", "Latife Tekin", "Can Yayınları", 2018, "Türk Edebiyatı", "PL248.T44 S48", "Mevcut"),
    ("978-9750802119", "Memleketimden İnsan Manzaraları", "Nazım Hikmet", "Yapı Kredi Yayınları", 2002, "Türk Edebiyatı", "PL248.H55 M46", "Mevcut"),

    # --- Dünya Edebiyatı (20) ---
    ("978-9750718533", "1984", "George Orwell", "Can Yayınları", 2019, "Dünya Edebiyatı", "PR6029.R8 N56", "Ödünçte"),
    ("978-9750719380", "Hayvan Çiftliği", "George Orwell", "Can Yayınları", 2019, "Dünya Edebiyatı", "PR6029.R8 A65", "Mevcut"),
    ("978-9754589023", "Suç ve Ceza", "Fyodor Dostoyevski", "Türkiye İş Bankası Kültür Yayınları", 2016, "Dünya Edebiyatı", "PG3326.P7 S83", "Mevcut"),
    ("978-9754589030", "Karamazov Kardeşler", "Fyodor Dostoyevski", "Türkiye İş Bankası Kültür Yayınları", 2017, "Dünya Edebiyatı", "PG3326.B7 K37", "Mevcut"),
    ("978-6053609124", "Savaş ve Barış", "Lev Tolstoy", "Türkiye İş Bankası Kültür Yayınları", 2018, "Dünya Edebiyatı", "PG3366.V6 S38", "Mevcut"),
    ("978-6053609131", "Anna Karenina", "Lev Tolstoy", "Türkiye İş Bankası Kültür Yayınları", 2018, "Dünya Edebiyatı", "PG3366.A6 A56", "Mevcut"),
    ("978-9750726439", "Yüzyıllık Yalnızlık", "Gabriel García Márquez", "Can Yayınları", 2018, "Dünya Edebiyatı", "PQ8180.17.A73 C54", "Mevcut"),
    ("978-9750726446", "Kırmızı Pazartesi", "Gabriel García Márquez", "Can Yayınları", 2018, "Dünya Edebiyatı", "PQ8180.17.A73 C76", "Mevcut"),
    ("978-9750739828", "Dönüşüm", "Franz Kafka", "Türkiye İş Bankası Kültür Yayınları", 2019, "Dünya Edebiyatı", "PT2621.A26 V47", "Mevcut"),
    ("978-9750739835", "Dava", "Franz Kafka", "Türkiye İş Bankası Kültür Yayınları", 2019, "Dünya Edebiyatı", "PT2621.A26 P76", "Mevcut"),
    ("978-9750721328", "Yabancı", "Albert Camus", "Can Yayınları", 2016, "Dünya Edebiyatı", "PQ2605.A3734 E87", "Mevcut"),
    ("978-9750721335", "Veba", "Albert Camus", "Can Yayınları", 2016, "Dünya Edebiyatı", "PQ2605.A3734 P47", "Mevcut"),
    ("978-9750718540", "Cesur Yeni Dünya", "Aldous Huxley", "İthaki Yayınları", 2017, "Dünya Edebiyatı", "PR6015.U9 B73", "Ödünçte"),
    ("978-6053754794", "Fahrenheit 451", "Ray Bradbury", "İthaki Yayınları", 2018, "Dünya Edebiyatı", "PS3503.R167 F34", "Mevcut"),
    ("978-6053754800", "Dune", "Frank Herbert", "İthaki Yayınları", 2019, "Dünya Edebiyatı", "PS3558.E63 D86", "Ödünçte"),
    ("978-9750736889", "Körlük", "José Saramago", "Kırmızı Kedi Yayınevi", 2017, "Dünya Edebiyatı", "PQ9261.S25 E57", "Mevcut"),
    ("978-9754587111", "Satranç", "Stefan Zweig", "Türkiye İş Bankası Kültür Yayınları", 2015, "Dünya Edebiyatı", "PT2653.W42 S34", "Mevcut"),
    ("978-9750735431", "Küçük Prens", "Antoine de Saint-Exupéry", "Can Yayınları", 2015, "Dünya Edebiyatı", "PQ2637.A274 P48", "Mevcut"),
    ("978-9750835612", "Gülün Adı", "Umberto Eco", "Doğan Kitap", 2016, "Dünya Edebiyatı", "PQ4865.C6 N66", "Mevcut"),
    ("978-9750835629", "Foucault Sarkacı", "Umberto Eco", "Doğan Kitap", 2016, "Dünya Edebiyatı", "PQ4865.C6 P46", "Mevcut"),

    # --- Tarih ve Sosyal Bilimler (15) ---
    ("978-9754587173", "Nutuk", "Mustafa Kemal Atatürk", "Türkiye İş Bankası Kültür Yayınları", 2017, "Tarih", "DR592.K4 A35", "Mevcut"),
    ("978-9752430501", "Devlet-i Aliyye: Osmanlı İmparatorluğu Üzerine Araştırmalar 1", "Halil İnalcık", "Türkiye İş Bankası Kültür Yayınları", 2016, "Tarih", "DR486 I53", "Mevcut"),
    ("978-9752430518", "İmparatorluğun En Uzun Yüzyılı", "İlber Ortaylı", "Kronik Kitap", 2018, "Tarih", "DR557 O78", "Mevcut"),
    ("978-6052980125", "Gazi Mustafa Kemal Atatürk", "İlber Ortaylı", "Kronik Kitap", 2018, "Tarih", "DR592.K4 O78", "Ödünçte"),
    ("978-6050924251", "Sapiens: Hayvanlardan Tanrılara İnsan Türünün Kısa Tarihi", "Yuval Noah Harari", "Kolektif Kitap", 2015, "Tarih", "CB113.H4 H37", "Mevcut"),
    ("978-6050938180", "Homo Deus: Yarının Kısa Tarihi", "Yuval Noah Harari", "Kolektif Kitap", 2016, "Tarih", "CB161 H37", "Mevcut"),
    ("978-9753421669", "Tüfek, Mikrop ve Çelik", "Jared Diamond", "Pegasus Yayınları", 2018, "Tarih", "HM621 D53", "Mevcut"),
    ("978-9750829147", "Ulusların Düşüşü", "Daron Acemoğlu, James A. Robinson", "Doğan Kitap", 2014, "Felsefe ve Sosyoloji", "HB74.P65 A34", "Mevcut"),
    ("978-9750846212", "Dar Koridor", "Daron Acemoğlu, James A. Robinson", "Doğan Kitap", 2020, "Felsefe ve Sosyoloji", "JC585 A34", "Mevcut"),
    ("978-9754587012", "Devlet", "Platon", "Türkiye İş Bankası Kültür Yayınları", 2015, "Felsefe ve Sosyoloji", "JC71.P26 D48", "Mevcut"),
    ("978-9754587029", "Nikomakhos'a Etik", "Aristoteles", "BilgeSu Yayıncılık", 2014, "Felsefe ve Sosyoloji", "B430.A8 T87", "Mevcut"),
    ("978-9750504785", "Hapishanenin Doğuşu", "Michel Foucault", "İmge Kitabevi", 2017, "Felsefe ve Sosyoloji", "HV8666 F68", "Mevcut"),
    ("978-9753423014", "Bilimsel Devrimlerin Yapısı", "Thomas S. Kuhn", "Kırmızı Yayınları", 2018, "Felsefe ve Sosyoloji", "Q175 K95", "Mevcut"),
    ("978-9754708127", "Hayali Cemaatler", "Benedict Anderson", "Metis Yayınları", 2015, "Felsefe ve Sosyoloji", "JC311 A65", "Mevcut"),
    ("978-9753424127", "Akışkan Modernite", "Zygmunt Bauman", "Can Yayınları", 2017, "Felsefe ve Sosyoloji", "HM831 B38", "Mevcut"),

    # --- Bilim, Teknoloji ve Araştırma Yöntemleri (10) ---
    ("978-9754039870", "Kozmos", "Carl Sagan", "Altın Kitaplar", 2016, "Bilim ve Teknoloji", "QB44.2 S24", "Mevcut"),
    ("978-6051051475", "Zamanın Kısa Tarihi", "Stephen Hawking", "Alfa Yayınları", 2017, "Bilim ve Teknoloji", "QB981 H39", "Mevcut"),
    ("978-6051713458", "Türlerin Kökeni", "Charles Darwin", "Alfa Yayınları", 2017, "Bilim ve Teknoloji", "QH365.O2 D37", "Mevcut"),
    ("978-9750831232", "Hızlı ve Yavaş Düşünme", "Daniel Kahneman", "Varlık Yayınları", 2015, "Bilim ve Teknoloji", "BF441 K34", "Ödünçte"),
    ("978-9751418906", "Sosyal Bilimlerde Araştırma Yöntemleri", "Niyazi Karasar", "Nobel Akademik Yayıncılık", 2020, "Araştırma Yöntemleri", "H62 K37", "Mevcut"),
    ("978-6053208907", "Nitel Araştırma Yöntemleri", "Ali Yıldırım, Hasan Şimşek", "Seçkin Yayıncılık", 2021, "Araştırma Yöntemleri", "H62 Y55", "Mevcut"),
    ("978-9751634122", "Bilimsel Araştırma ve Yazma Kılavuzu", "Orhan Türkdoğan", "Pegem Akademi", 2019, "Araştırma Yöntemleri", "Q180.55.M4 T87", "Mevcut"),
    ("978-6051337890", "SPSS ile İstatistiksel Veri Analizi", "Şeref Kalaycı", "Dinamik Akademi", 2018, "Araştırma Yöntemleri", "HA32 K35", "Mevcut"),
    ("978-9750528903", "Gödel, Escher, Bach: Bir Ebedi Gökçe Belik", "Douglas R. Hofstadter", "Kabalcı Yayınevi", 2014, "Bilim ve Teknoloji", "QA9.8 H64", "Mevcut"),
    ("978-6051719870", "Büyük Tasarım", "Stephen Hawking, Leonard Mlodinow", "Alfa Yayınları", 2018, "Bilim ve Teknoloji", "QB981 H38", "Mevcut"),
]


def veri_tabani_olustur(reset: bool = False) -> int:
    """SQLite veri tabanını oluşturur ve örnek kitap kayıtlarını yükler."""
    if reset and os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    baglanti = sqlite3.connect(DB_PATH)
    imlec = baglanti.cursor()

    # Kitaplar tablosunu oluştur
    imlec.execute(
        """
        CREATE TABLE IF NOT EXISTS kitaplar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isbn TEXT NOT NULL UNIQUE,
            baslik TEXT NOT NULL,
            yazar TEXT NOT NULL,
            yayinevi TEXT NOT NULL,
            yayin_yili INTEGER NOT NULL,
            kategori TEXT NOT NULL,
            raf_kodu TEXT NOT NULL,
            durum TEXT NOT NULL DEFAULT 'Mevcut' CHECK (durum IN ('Mevcut', 'Ödünçte')),
            eklenme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # Arama performansını artırmak için indeksler
    imlec.execute("CREATE INDEX IF NOT EXISTS idx_kitaplar_baslik ON kitaplar(baslik)")
    imlec.execute("CREATE INDEX IF NOT EXISTS idx_kitaplar_yazar ON kitaplar(yazar)")
    imlec.execute("CREATE INDEX IF NOT EXISTS idx_kitaplar_kategori ON kitaplar(kategori)")

    # Tablo boşsa örnek kayıtları ekle
    imlec.execute("SELECT COUNT(*) FROM kitaplar")
    mevcut_sayi = imlec.fetchone()[0]

    if mevcut_sayi == 0:
        imlec.executemany(
            """
            INSERT INTO kitaplar (isbn, baslik, yazar, yayinevi, yayin_yili, kategori, raf_kodu, durum)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ORNEK_KITAPLAR,
        )
        baglanti.commit()
        eklenen_sayi = len(ORNEK_KITAPLAR)
    else:
        eklenen_sayi = 0

    imlec.execute("SELECT COUNT(*) FROM kitaplar")
    toplam = imlec.fetchone()[0]
    baglanti.close()
    return toplam if eklenen_sayi > 0 else mevcut_sayi


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Kütüphane SQLite veri tabanını başlatır.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Mevcut veri tabanını silip 100 örnek kaydı baştan oluşturur.",
    )
    args = parser.parse_args()

    toplam_kayit = veri_tabani_olustur(reset=args.reset)
    print(f"Veri tabanı hazır: {DB_PATH}")
    print(f"Toplam kitap kaydı: {toplam_kayit}")
