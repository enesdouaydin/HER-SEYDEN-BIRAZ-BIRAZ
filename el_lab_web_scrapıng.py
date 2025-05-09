# web scraping ile ses dosyalari otomatik olarak indirilmesi
# bu script ile el lb sitesinde text to speech yapılıyor.
# telıf ya da dava yememek ıcın lınkı kaldırdım ama lınk kısmında yazan yere dedıgım lınkı yapıstırırsanız lınke gırer
# sıgn ın butonuna tıklamayı unutmusum ona da basmasınız gerek	

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import shutil
import traceback # Hata ayıklama için

# --- Ayarlar ---
DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
TEXT_FILE = "enes_text.txt" # ses dosyalari icin var olan text dosyasi
EMAIL = "temp@mil."  # Giriş için e-posta
PASSWORD = "passwd"   # Giriş için şifre
# Klasör oluştur
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# --- Chrome Ayarları ---
chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": DOWNLOAD_DIR,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})
chrome_options.add_argument("--start-maximized")

# --- Browser başlat ---
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 45)

# --- el lb sıtesı lınkı ---
driver.get("el lb linki speech to text kısmını alacaksınız.")
print("Abi, abla, site açılıyor ve login ekranı bekleniyor...")
time.sleep(5)

try:
    # --- LOGIN İŞLEMİ ---
    print("Login adımları deneniyor...")
    email_input = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@type='email' or @name='email' or contains(@class, 'border-gray-alpha-200')]")))
    email_input.send_keys(EMAIL)
    print("E-posta yazıldı.")
    time.sleep(1)
    password_input = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@data-testid='sign-in-password-input']")))
    password_input.send_keys(PASSWORD)
    print("Şifre yazıldı.")
    time.sleep(1)
    login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Sign in') or contains(., 'Continue') or contains(., 'Login') or @type='submit']")))
    login_button.click()
    print("Giriş yap butonuna tıklandı.")
    print("Giriş sonrası sayfanın yüklenmesi bekleniyor...")
    wait.until(EC.presence_of_element_located((By.XPATH, "//textarea[contains(@class, 'flex-1')]")))
    print("Abi, abla, giriş başarılı! ✅")
    time.sleep(5)

except Exception as login_error:
    print(f"Abi, abla, LOGIN sırasında bir hata oldu: {login_error}")
    driver.quit()
    exit()

# --- TXT dosyasını oku ---
try:
    with open(TEXT_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    print(f"Abi, abla, '{TEXT_FILE}' dosyası bulunamadı! Script durduruluyor.")
    driver.quit()
    exit()

# --- Textarea temizleme fonksiyonu ---
def temizle_textarea(textarea):
    try:
        textarea.click()
        time.sleep(0.2)
        textarea.send_keys(Keys.CONTROL, 'a')
        time.sleep(0.2)
        textarea.send_keys(Keys.BACKSPACE)
        time.sleep(0.2)
        textarea.clear()
        time.sleep(0.2)
        textarea.send_keys(Keys.CONTROL, 'a')
        textarea.send_keys(Keys.DELETE)
        time.sleep(0.2)
    except Exception as e:
        print(f"Abi, abla, textarea temizlenirken hata: {e}")

# --- XPath'ler ---
textarea_xpath = "//textarea[contains(@class, 'flex-1')]"
generate_button_xpath = "//button[.//span[contains(text(), 'Generate')]] | //button[contains(text(), 'Generate')]"
download_button_xpath = "//button[@aria-label='Download']"

# --- İŞLEM BAŞLAT ---
print("\n--- Metinleri sese çevirme işlemi başlıyor ---")

for idx, text in enumerate(lines, start=1):
    print(f"\n--- İşlem {idx} Başlatılıyor ---")
    try:
        textarea = wait.until(EC.element_to_be_clickable((By.XPATH, textarea_xpath)))
        temizle_textarea(textarea)
        textarea.send_keys(text)
        print(f"{idx}. Satır yazıldı: '{text[:50]}...'")

        if idx == 1:
            print("İlk cümle: 2 saniye bekleniyor...")
            time.sleep(2)
            print("İlk cümle: Download butonu tıklanıyor...")
            download_button = wait.until(EC.element_to_be_clickable((By.XPATH, download_button_xpath)))
            download_button.click()
            print("İlk cümle: Download tıklandı.")
        else:
            print(f"{idx}. cümle: 'Generate' butonu tıklanıyor...")
            generate_button = wait.until(EC.element_to_be_clickable((By.XPATH, generate_button_xpath)))
            generate_button.click()
            print(f"{idx}. cümle: 'Generate' tıklandı.")

            print(f"{idx}. cümle: Download butonu aktifleşmesi bekleniyor...")
            download_button = wait.until(EC.element_to_be_clickable((By.XPATH, download_button_xpath)))
            print(f"{idx}. cümle: Download tıklanıyor...")
            download_button.click()

        print("İndirme işlemi için 10 saniye bekleniyor...")
        time.sleep(10)

        downloaded_files = os.listdir(DOWNLOAD_DIR)
        mp3_files = [f for f in downloaded_files if f.endswith(".mp3") and not f.startswith("1-")]

        if not mp3_files:
            print(f"!!!!!!!!!! HATA: {idx}. satır için MP3 dosyası bulunamadı! Bu satır atlanıyor.")
            continue

        latest_mp3_path = max([os.path.join(DOWNLOAD_DIR, f) for f in mp3_files], key=os.path.getctime)
        new_mp3_name = f"1-{idx}.mp3"
        new_mp3_path = os.path.join(DOWNLOAD_DIR, new_mp3_name)
        shutil.move(latest_mp3_path, new_mp3_path)
        print(f"Dosya başarıyla yeniden adlandırıldı: {new_mp3_name}")

        with open(os.path.join(DOWNLOAD_DIR, f"1-{idx}.txt"), "w", encoding="utf-8") as text_file:
            text_file.write(text)

        print(f"Abi, abla, {idx}. işlem tamam ✅")

    except Exception as e:
        print(f"!!!!!!!!!! Abi, abla, {idx}. SATIRDA BEKLENMEDİK BİR HATA OLDU !!!!!!!!!!!")
        print(f"Hata Detayı: {str(e)}")
        print(f"Hata Traceback:\n{traceback.format_exc()}")
        try:
            print("Hata sonrası sayfa yenileme deneniyor...")
            driver.refresh()
            wait.until(EC.presence_of_element_located((By.XPATH, textarea_xpath)))
            time.sleep(3)
        except Exception as refresh_err:
            print(f"Sayfa yenilenirken hata: {refresh_err}")
            print("Sayfa yenileme başarısız, script durduruluyor.")
            break
        continue

# --- Bitti ---
print("\n==========================================")
print("Abi, abla, tüm işlemler tamamlandı!")
print(f"Dosyalar '{DOWNLOAD_DIR}' klasörüne kaydedildi.")
print("==========================================")
driver.quit()