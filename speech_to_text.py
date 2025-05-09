#mikrofona konustgumuz sesleri text olarak yazar


import speech_recognition as sr
import time



def continuous_speech_to_text():
    recognizer = sr.Recognizer()

    recognizer.pause_threshold = 1.5 

    recognizer.dynamic_energy_threshold = True 

    try:
        with sr.Microphone() as source:
            print("Mikrofon ayarlanıyor... Lütfen birkaç saniye sessiz olun.")
            try:
                recognizer.adjust_for_ambient_noise(source, duration=3)
                print(f"Ortam gürültüsü ayarlandı. Enerji Eşiği: {recognizer.energy_threshold:.2f}")
            except Exception as e:
                 print(f"Gürültü ayarlanırken hata: {e}. Varsayılan değerler kullanılacak.")
             
            print("\nKonuşmaya başlayabilirsiniz. Çıkmak için Ctrl+C kullanın.")

            while True:
                print(f"\nDinleniyor... (Pause threshold: {recognizer.pause_threshold}s)")
                try:
                    
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=20) 

                    print("Ses kaydedildi, Google ile işleniyor...")
                    
                    text = recognizer.recognize_google(audio, language="tr-TR")
                    
                    text = text.lower().strip() 
                    
                    if text: 
                         print(f"Algılanan Metin: {text}")
                    else:
                         print("Boş veya anlamsız ses algılandı.")

                except sr.WaitTimeoutError:
                
                    pass 
                except sr.UnknownValueError:
                    print("Ses anlaşılamadı. Daha net konuşmayı veya ortamı sessizleştirmeyi deneyin.")
                except sr.RequestError as e:
                    print(f"Google API hatası: {e}. İnternet bağlantınızı kontrol edin.")
                except Exception as e:
                  
                    print(f"Bilinmeyen bir hata oluştu: {e}")
                
             

    except KeyboardInterrupt:
        print("\nDinleme durduruldu. Program sonlandırıldı.")
    except Exception as e:
        print(f"Program başlatılırken kritik bir hata oluştu: {e}")


if __name__ == "__main__":
    continuous_speech_to_text()
