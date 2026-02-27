# Lab 4 — JWT authentication bypass via JWK header injection

**Kaynak:** https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-jwk-header-injection

## Amaç

Bu laboratuvarda amaç, sunucunun JWK (JSON Web Key) başlığı üzerinden kabul ettiği zayıf doğrulamayı kullanarak kendi anahtarlarımızla yönetici token'ı üretmek ve `Carlos` kullanıcısını silmektir.

## Kısa Özet

JWT doğrulaması sırasında sunucu, token içinde sağlanan JWK başlığını (`jwk` header) kullanarak imzayı doğrulamaktadır. Bu, istemci tarafından sağlanan anahtarın kötüye kullanılmasına olanak verir; saldırgan kendi RSA anahtar çiftini yaratarak ve JWK başlığına bu anahtarın public parametrelerini (`n`, `e`) koyarak imzalı bir token üretebilir. Sunucu, doğru formattaysa bu token'ı geçerli kabul eder.

## Analiz

- Orijinal token incelendiğinde header'da `RS256` algoritması ve bir `kid` değeri görüyoruz.
- `alg: none` kapalıdır; bu yüzden başka bir bypass tekniğine ihtiyaç var.
- Sunucunun JWK başlığını desteklediği fark edildi; `jwk` alanı, JSON Web Key objesi içeriyor olabilir.
- Zayıf nokta: sunucu **istemcinin sağladığı** JWK anahtarını kullanarak imzayı doğruluyor. Böylece saldırgan kendi anahtar çiftini üretebilir.

## Saldırı Adımları (PoC)

1. Önce terminalde RSA anahtar çiftini oluşturun:

   ```bash
   openssl genrsa -out private.pem 2048
   openssl rsa -in private.pem -pubout -out public.pem
   ```

2. Tarayıcıdan mevcut oturum token'ını (JWT) yakalayın.
3. `public.pem` ve `private.pem` dosyalarını aynı klasöre koyun.
4. `Lab_4/token_fabrika.py` script'ini kullanarak kendi token'ınızı üretin. Script aşağıdaki adımları otomatikleştirir:

   - Orijinal token'ı decode eder (doğrulama yapmadan).
   - Payload içindeki `sub` alanını `administrator` olarak değiştirir.
   - RSA public key'den `n` ve `e` değerlerini Base64URL formatına çevirip bir JWK objesi oluşturur.
   - Kendi private key ile yeni token'ı `RS256` algoritmasıyla imzalar ve header'a `jwk` alanını ekler.

   Script çalıştırıldığında ekrana yeni token ve header bilgisi basılır; bu token'ı tarayıcıya yapıştırarak kullanabilirsiniz.

   ```bash
   python3 token_fabrikası.py
   ```

5. Üretilen token ile `/admin` paneline erişin ve oradan `Carlos` hesabını silin.

## Sonuç

JWK header injection zafiyeti sayesinde kendi anahtarımızla imzalanmış bir token ürettik ve sistem tarafından kabul edildi. Bu token ile admin paneline girilip `Carlos` silindi.

## Tavsiyeler / Mitigasyon

- Sunucunun asla istemcinin sağladığı JWK'a göre token doğrulaması yapmaması gerekir; doğrulama için sabit, güvenli bir public key kullanılmalıdır.
- JWK başlığı içeriğinin beklenen anahtarla eşleştiğini kontrol edin ve `kid` gibi değerleri zorunlu kılın.
- Anahtar yönetim sistemleri ve kütüphaneler güncel tutulmalı; JWK desteği güvenli şekilde yapılandırılmalıdır.

## Ek Bilgiler

`token_fabrika.py` içeriği bu raporla birlikte sunulmuştur. Script, Python `PyJWT` ve `cryptography` paketlerini gerektirir:

```bash
pip install PyJWT cryptography
```

---
