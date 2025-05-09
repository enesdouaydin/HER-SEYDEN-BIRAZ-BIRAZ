import speech_recognition as sr
import time 
def continuous_speech_to_text():
    recognizer = sr.Recognizer()

    # *** İYİLEŞTİRME 1: Daha uzun duraksamalara izin ver ***
    # Konuşmanın bittiğini anlamak için gereken sessizlik süresi (saniye).
    # Varsayılan 0.8'dir. Cümleleriniz erken kesiliyorsa artırın (örn: 1.5 veya 2.0).
    # Eğer konuşma bittikten sonra çok uzun süre bekliyorsa düşürebilirsiniz.
    recognizer.pause_threshold = 1.5 

    # *** İYİLEŞTİRME 2: Enerji Eşiği Ayarı (Opsiyonel ama Faydalı) ***
    # recognizer.energy_threshold değerini ortam gürültüsüne göre otomatik ayarlar.
    # Bu değer, neyin konuşma neyin gürültü olduğunu ayırt etmeye yarar.
    # 'dynamic_energy_threshold = True' (varsayılan) ise, konuşma sırasında da bu eşiği ayarlar.
    recognizer.dynamic_energy_threshold = True 

    try:
        with sr.Microphone() as source:
            print("Mikrofon ayarlanıyor... Lütfen birkaç saniye sessiz olun.")
            # Ortam gürültüsünü ölç ve enerji eşiğini ayarla
            try:
                # adjust_for_ambient_noise'in bitmesini beklemek için biraz daha sağlam bir yol
                recognizer.adjust_for_ambient_noise(source, duration=3)
                print(f"Ortam gürültüsü ayarlandı. Enerji Eşiği: {recognizer.energy_threshold:.2f}")
            except Exception as e:
                 print(f"Gürültü ayarlanırken hata: {e}. Varsayılan değerler kullanılacak.")
                 # Eğer hata olursa varsayılan bir eşik atanabilir ama genelde otomatik ayar daha iyidir.
                 # recognizer.energy_threshold = 4000 # Örnek manuel ayar

            print("\nKonuşmaya başlayabilirsiniz. Çıkmak için Ctrl+C kullanın.")

            while True:
                print(f"\nDinleniyor... (Pause threshold: {recognizer.pause_threshold}s)")
                try:
                    # *** İYİLEŞTİRME 3: phrase_time_limit Ayarı ***
                    # Bir konuşma bölümünün maksimum uzunluğu (saniye).
                    # Eğer çok uzun cümleler kuruyorsanız ve kesiliyorsa artırın (örn: 30).
                    # VEYA None yaparak limiti kaldırın. None yaparsanız, siz duraklayana
                    # (pause_threshold süresi kadar) veya Ctrl+C'ye basana kadar kayıt sürer.
                    # Dikkat: None yapınca çok uzun konuşursanız API'ye gönderim sorun olabilir.
                    # Önce artırmayı deneyin (örn: 20 veya 30).
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=20) 
                    # Veya limitsiz: audio = recognizer.listen(source, timeout=5, phrase_time_limit=None)

                    print("Ses kaydedildi, Google ile işleniyor...")
                    
                    # Google API'sini kullanarak sesi metne çevir
                    text = recognizer.recognize_google(audio, language="tr-TR")
                    
                    # Doğruluk kontrolü için küçük harfe çevirip baştaki/sondaki boşlukları alabiliriz
                    text = text.lower().strip() 
                    
                    if text: # Eğer boş bir sonuç dönmediyse yazdır
                         print(f"Algılanan Metin: {text}")
                    else:
                         print("Boş veya anlamsız ses algılandı.")

                except sr.WaitTimeoutError:
                    # Belirtilen 'timeout' süresi içinde konuşma başlamazsa
                    # print("Zaman aşımı: Konuşma algılanmadı. Tekrar dinleniyor...") # İsteğe bağlı mesaj
                    pass # Sürekli mesaj yazdırmamak için pas geçebiliriz
                except sr.UnknownValueError:
                    # Konuşma algılandı ancak anlaşılamadıysa
                    print("Ses anlaşılamadı. Daha net konuşmayı veya ortamı sessizleştirmeyi deneyin.")
                except sr.RequestError as e:
                    # Google API'sine ulaşılamazsa
                    print(f"Google API hatası: {e}. İnternet bağlantınızı kontrol edin.")
                except Exception as e:
                    # Diğer beklenmedik hatalar
                    print(f"Bilinmeyen bir hata oluştu: {e}")
                
                # Çok hızlı döngüyü önlemek için küçük bir bekleme (isteğe bağlı)
                # time.sleep(0.1) 

    except KeyboardInterrupt:
        print("\nDinleme durduruldu. Program sonlandırıldı.")
    except Exception as e:
        print(f"Program başlatılırken kritik bir hata oluştu: {e}")

# Çalıştır
if __name__ == "__main__":
    continuous_speech_to_text()