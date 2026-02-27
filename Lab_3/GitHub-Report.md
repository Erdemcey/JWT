# Lab 3 — JWT authentication bypass via weak signing key

**Kaynak:** https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-weak-signing-key

## Amaç

Uygulamanın JWT imza anahtarının zayıf/kolay tahmin edilebilir olması nedeniyle admin hakları kazanmak ve `Carlos` kullanıcısını silmektir.

## Kısa Özet

Bu laboratuvarda token imzası HMAC-SHA256 (`HS256`) ile yapılmıştır; bu simetrik algoritma tek bir gizli anahtar kullanır. Anahtarın zayıf olduğu tespit edilirse, brute-force ile anahtar bulunabilir ve saldırgan aynı anahtarla token üreterek yetkili işlemler gerçekleştirebilir.

## Analiz

- Mevcut JWT yakalandı ve `alg: none` ile denendiğinde bypass başarısız oldu; dolayısıyla farklı bir zafiyet senaryosu araştırıldı.
- Token'ın HS256 ile imzalandığı belirlendi; bu, aynı gizli anahtarın hem imzalama hem de doğrulamada kullanıldığı simetrik bir yöntemdir.
- Zayıf gizli anahtar kullanımı şüphesi olduğundan, parola listesi (wordlist) ile brute-force denenmesi uygun görüldü.

## Saldırı Adımları (PoC)

1. JWT token'ını yakalayın.
2. Anahtar karma işlevi olarak HMAC-SHA256 (`HS256`) kullanıldığı için uygun `hashcat` modu ile brute-force deneyin (ör. `-m 16500`).

Örnek `hashcat` komutu:

```bash
sudo hashcat -a 0 -m 16500 \
  eyJraWQiOiI4OTQ0Zjk0ZC00MmE0LTRkYzYtODM4OS00NTk1ODI2NWNjZmIiLCJhbGciOiJIUzI1NiJ9.\
  eyJpc3MiOiJwb3J0c3dpZ2dlciIsImV4cCI6MTc3MjE1MzcwNSwic3ViIjoid2llbmVyIn0.\
  rw7p6ztxWo8kbosuc30t52cezDS-zOnnL79Pl5rkyPY \
  jwt-secrets/jwt.secrets.list
```

Not: Örnek komutta kullanılan `jwt-secrets/jwt.secrets.list` gibi wordlistler GitHub ve açık kaynak deposunda mevcuttur.

3. Eğer brute-force sonucu basit bir anahtar (ör. `secret1`) bulunduysa, aynı anahtarla yeni bir token oluşturun ve admin yetkisi içeren payload ile imzalayın.
4. Oluşturulan token ile uygulamaya istek gönderin ve `/admin` yolunu ziyaret ederek admin yetkisini doğrulayın.

## Sonuç

Brute-force ile gizli anahtar tespit edildiğinde, HS256 imzası ile yeni token oluşturularak admin paneline erişildi ve `Carlos` kullanıcısı silinebildi.

## Tavsiyeler / Mitigasyon

- Simetrik anahtarların güçlü, yeterli uzunlukta ve rastgele olmasını sağlayın; kolay tahmin edilebilir anahtarlar kullanmayın.
- Anahtar yönetimini güvenli şekilde yapın; anahtar rotasyonu ve erişim kontrolleri uygulayın.
- Mümkünse asimetrik imzalama (RS256) tercih edin; böylece sunucu sadece public key ile doğrulama yapar ve private key sunucuda güvenli şekilde saklanır.
- Brute-force saldırılarına karşı rate limiting, anomalili oturum tespiti ve izleme uygulayın.

## Kaynaklar

- PortSwigger lab: https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-weak-signing-key
- Wordlist örnekleri: https://github.com/Erdemcey/jwt-secrets
