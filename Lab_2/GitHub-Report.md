# Lab 2 — JWT authentication bypass via flawed signature verification

**Kaynak:** https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-flawed-signature-verification

## Amaç

Hedef uygulamada JWT doğrulama zafiyetinden faydalanarak admin yetkisi elde etmek ve gerekli işlemleri (ör. `Carlos` kullanıcısını silme) gerçekleştirmektir.

## Kısa Özet

Bu laboratuvarda JWT doğrulama mekanizmasındaki algoritma karışıklığı (algorithm confusion) sayesinde doğrulama atlanabiliyor. Laboratuvar, başlıkta ve imzada tutarsızlık yaratarak veya `alg` manipülasyonu ile token doğrulamasının bypass edilmesine izin veriyor.

## Analiz

- Sistem JWT ile oturum yönetimi sağlıyor.
- İlk denemede `alg: none` ile bypass denenmiş ve farklı lab senaryolarında olduğu gibi bu yöntem bazen işe yarayabiliyor.
- Lab 1 ile benzerlik gösteren bir zafiyet gözlemlendi; başlık/payload manipülasyonu ile doğrulama atlatılabiliyor.

## Saldırı Adımları (PoC)

1. `wiener` hesabı ile oturum açın ve JWT cookie'sini yakalayın.
2. `/admin` sayfasından uygulamanın admin kullanıcı adını veya ilgili ipuçlarını öğrenin.
3. Token header'ını Base64URL decode ederek `alg` değerini `none` olarak değiştirin; payload içindeki `sub` alanını `administrator` olarak güncelleyin.
4. Header ve payload'u yeniden Base64URL ile kodlayın; imza kısmını boş bırakın.
5. Yeni token ile uygulamaya istek gönderin ve admin paneline erişimi doğrulayın.

Not: Bazı uygulamalar `alg: none` manipülasyonunu reddeder; bu durumda zafiyet farklı bir doğrulama hatasından kaynaklanıyor olabilir ve payload değişiklikleriyle (ör. `sub`) birlikte farklı teknikler denenmelidir.

## Sonuç

Başarıyla admin paneline erişildiğinde `Carlos` hesabı silinebilmektedir. Zafiyet, JWT doğrulama mantığındaki karışıklık veya eksik kontrollere dayanmaktadır.

## Tavsiyeler / Mitigasyon

- Sunucu tarafında beklenen imzalama algoritmasını sabit olarak doğrulayın; başlıktaki `alg` değerine güvenmeyin.
- `alg: none` desteğini tamamen devre dışı bırakın.
- JWT doğrulama için güvenilir, güncel kütüphaneler kullanın ve ek testlerle doğrulama akışını kontrol edin.

## Kaynaklar

- PortSwigger lab: https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-flawed-signature-verification
- JWT analiz: https://www.jwt.io/
