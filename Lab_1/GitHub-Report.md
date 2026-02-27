# Lab 1 — JWT authentication bypass via unverified signature

**Kaynak:** https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-unverified-signature

## Amaç

Bu laboratuvarda hedef, uygulamanın admin paneline erişim sağlayarak `Carlos` kullanıcısını silmektir.

## Kısa Özet

Uygulama JWT (JSON Web Token) kullanarak oturum yönetimi sağlıyor. Token başlığında (`header`) `RS256` algoritması gözükse de uygulama `alg` alanını güvenli şekilde doğrulamıyor. `alg` değeri `none` olarak değiştirildiğinde imza doğrulaması atlanabiliyor; bu şekilde admin yetkisi elde edildi.

## Analiz

- Yakalanan JWT header örneği:

```json
{
  "kid": "0da6557f-7c0a-4c62-b18f-11288b6994b4",
  "alg": "RS256"
}
```

- Payload örneği:

```json
{
  "iss": "portswigger",
  "exp": 1772141622,
  "sub": "wiener"
}
```

Header ve payload Base64URL ile kodlanmış; imza doğrulaması eksik veya hatalı uygulandığı için `alg` manipülasyonu ile atlatılabiliyor.

## Saldırı Adımları (PoC)

1. Mevcut `wiener` oturum token'ını yakalayın (tarayıcı devtools veya proxy ile).
2. Token'ı `header.payload.signature` biçiminde ayırın ve header kısmını Base64URL decode edin.
3. `alg` değerini `none` olarak değiştirin ve header ile payload'u Base64URL tekrar kodlayın.
4. İmza kısmını boş bırakın veya kaldırın; oluşturduğunuz token'ı uygulamaya gönderin (`Cookie` veya `Authorization` header).
5. `/admin` sayfasına erişerek admin yetkisini doğrulayın ve `Carlos` hesabını silin.

Örnek istek (cookie ile):

```bash
curl -sS -b "session=<MODIFIED_TOKEN>" https://TARGET-URL/admin
```

## Sonuç

`alg` alanının `none` olarak ayarlanması sonucu imza doğrulaması atlandı ve admin paneline erişildi; gerekli işlem (Carlos'un silinmesi) gerçekleştirildi.

## Tavsiyeler / Mitigasyon

- Sunucunun beklenen algoritmayı sabit olarak kontrol etmesi gerekir; `alg` başlığını asla yalnızca istemciden gelen değere göre kabul etmeyin.
- `alg: none` gibi boş algoritmaları reddedin.
- Güvenilir JWT kütüphaneleri kullanın ve bunların güncel olduğundan emin olun.
- Asimetrik imzalama (RS256) kullanılıyorsa, doğrulama için sunucu tarafında güvenli bir public key yönetimi veya JWKS kullanın.

## Kaynaklar

- PortSwigger lab: https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-unverified-signature
- JWT analiz: https://www.jwt.io/
