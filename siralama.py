import os
import re
import sys

def sort_key_natural(name):
    """
    '1-10' gibi isimleri (1, 10) tuple'ına çevirerek
    doğru sayısal sıralama yapılmasını sağlar.
    """
    try:
        # '-' karakterine göre ayırıp tamsayıya çevir
        parts = name.split('-')
        return tuple(map(int, parts))
    except ValueError:
        # Eğer format bozuksa veya beklenmedik bir durum olursa
        # sıralamada sona atması için büyük bir değer döndür
        return (float('inf'),)

def renumber_files(folder_path, start_number_str):
    """
    Belirtilen klasördeki 'sayı-sayı.uzantı' formatlı dosyaları
    belirtilen numaradan başlayarak yeniden adlandırır.
    """
    # 1. Klasörün varlığını kontrol et
    if not os.path.isdir(folder_path):
        print(f"Hata: Klasör bulunamadı: {folder_path}")
        return

    # 2. Başlangıç numarasını kontrol et
    try:
        start_number = int(start_number_str)
        if start_number <= 0:
            raise ValueError("Başlangıç sayısı pozitif olmalı.")
    except ValueError:
        print(f"Hata: Geçersiz başlangıç sayısı: '{start_number_str}'. Pozitif bir tamsayı girin.")
        return

    print(f"Klasör taranıyor: {folder_path}")

    # 3. 'sayı-sayı' formatındaki temel adları ve uzantılarını bul
    base_names = set()
    # Hangi temel adın hangi uzantılara sahip olduğunu saklamak için:
    # Örnek: {'1-1': {'.mp3', '.txt'}, '1-2': {'.mp3'}}
    file_details = {}

    # 'sayı-sayı' formatını eşleştirmek için regex (Regular Expression)
    # ^ : Satır başı
    # \d+ : Bir veya daha fazla rakam
    # - : Tire karakteri
    # \d+ : Bir veya daha fazla rakam
    # $ : Satır sonu
    pattern = re.compile(r"^(\d+-\d+)$")

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        # Sadece dosyaları dikkate al, klasörleri değil
        if os.path.isfile(file_path):
            # Dosya adını ve uzantısını ayır (örn: '1-1', '.mp3')
            base, ext = os.path.splitext(filename)
            ext_lower = ext.lower() # Uzantıyı küçük harfe çevir (örn: .MP3 -> .mp3)

            # Sadece .mp3 ve .txt uzantılıları dikkate al
            if ext_lower in ['.mp3', '.txt']:
                # Dosya adının 'sayı-sayı' formatına uyup uymadığını kontrol et
                match = pattern.match(base)
                if match:
                    # Eşleşiyorsa, temel adı (örn: '1-1') set'e ekle
                    # (set kullanarak tekrarları önlemiş oluruz)
                    base_names.add(base)
                    # Bu temel ad için bulunan uzantıyı kaydet
                    if base not in file_details:
                        file_details[base] = set()
                    file_details[base].add(ext) # Orijinal uzantıyı sakla (.mp3 veya .MP3)

    # Eğer uygun formatta dosya bulunamazsa kullanıcıyı bilgilendir
    if not base_names:
        print("Klasörde 'sayı-sayı.mp3' veya 'sayı-sayı.txt' formatında dosya bulunamadı.")
        return

    # 4. Bulunan temel adları doğal sayısal sıraya göre sırala
    # Örn: '1-1', '1-2', '1-10', '2-1' şeklinde sıralanır
    sorted_base_names = sorted(list(base_names), key=sort_key_natural)

    print(f"\n{len(sorted_base_names)} adet eşleşen temel dosya adı bulundu ve sıralandı.")
    print("Yeniden adlandırma işlemi başlıyor...")

    # 5. Çakışma Kontrolü: Yeni adların mevcut başka dosyalarla çakışıp çakışmadığını kontrol et
    potential_targets = set()
    current_num_check = start_number
    for _ in sorted_base_names:
        potential_targets.add(str(current_num_check) + ".mp3")
        potential_targets.add(str(current_num_check) + ".txt")
        current_num_check += 1

    all_files_in_dir = set(os.listdir(folder_path))
    original_files_to_rename = set()
    for base in sorted_base_names:
        for ext in file_details.get(base, set()):
            original_files_to_rename.add(base + ext)

    conflicts = set()
    for target in potential_targets:
        # Eğer hedef dosya adı klasörde varsa VE bu dosya bizim yeniden adlandıracağımız
        # dosyalardan biri DEĞİLSE, bu bir çakışmadır.
        if target in all_files_in_dir and target not in original_files_to_rename:
            conflicts.add(target)

    if conflicts:
        print("\n!!! KRİTİK HATA: Yeniden adlandırma işlemi çakışmaya neden olacak.")
        print("Aşağıdaki hedef dosya adları zaten klasörde mevcut ve yeniden adlandırılacak dosyalar arasında değiller:")
        for conflict_file in sorted(list(conflicts)):
            print(f"- {conflict_file}")
        print("\nİşlem durduruldu. Lütfen bu çakışan dosyaları taşıyın/yeniden adlandırın veya farklı bir başlangıç numarası seçin.")
        sys.exit(1) # Programı sonlandır

    # 6. Sıralanmış listedeki her bir temel ad için yeniden adlandırma yap
    current_number = start_number
    rename_count = 0
    error_count = 0

    for old_base in sorted_base_names:
        new_base = str(current_number) # Yeni sıra numarasını stringe çevir
        # Bu temel ada ait uzantıları al (örn: {'.mp3', '.txt'})
        extensions = file_details.get(old_base, set())

        print(f"\n-> İşleniyor: '{old_base}' dosyaları -> '{new_base}' olarak adlandırılacak")

        files_renamed_this_group = 0
        # Bu temel adın her bir uzantısı için (mp3, txt) döngü yap
        for ext in extensions:
            old_filename = old_base + ext # Eski tam dosya adı (örn: 1-1.mp3)
            new_filename = new_base + ext # Yeni tam dosya adı (örn: 101.mp3)

            old_path = os.path.join(folder_path, old_filename)
            new_path = os.path.join(folder_path, new_filename)

            # Eski dosyanın hala var olduğundan emin ol (pratikte hep olmalı)
            if os.path.exists(old_path):
                try:
                    # Yeniden adlandırma işlemini yap
                    os.rename(old_path, new_path)
                    print(f"   Başarılı: '{old_filename}' -> '{new_filename}'")
                    files_renamed_this_group += 1
                except OSError as e:
                    # Yeniden adlandırma sırasında bir hata olursa (örn: izinler)
                    print(f"   HATA: '{old_filename}' yeniden adlandırılamadı: {e}")
                    error_count += 1
            else:
                # Bu durumun normalde olmaması gerekir
                print(f"   Uyarı: Beklenen '{old_filename}' dosyası bulunamadı (belki arada silindi?).")

        # Eğer bu grupta en az bir dosya adlandırıldıysa sayaçları artır
        if files_renamed_this_group > 0:
            rename_count += files_renamed_this_group
            # Bir sonraki sıra numarasına geç
            current_number += 1

    print(f"\n--- İşlem Tamamlandı ---")
    print(f"Toplam {rename_count} dosya başarıyla yeniden adlandırıldı.")
    if error_count > 0:
        print(f"Toplam {error_count} dosyada hata oluştu.")

# --- Kullanıcıdan Girdi Alma ---
if __name__ == "__main__":
    target_folder = input("Lütfen dosyaların bulunduğu klasörün tam yolunu girin: ")
    # Girdiyi temizle (başındaki/sonundaki boşlukları ve tırnak işaretlerini kaldır)
    target_folder = target_folder.strip().strip('"').strip("'")

    start_num_input = input("Dosyaların başlayacağı yeni numarayı girin (örn: 1, 101, vb.): ")
    start_num_input = start_num_input.strip()

    # Ana fonksiyonu çağır
    renumber_files(target_folder, start_num_input)

    # Betik bittiğinde kullanıcıya mesaj göster
    input("\nÇıkmak için Enter tuşuna basın...")