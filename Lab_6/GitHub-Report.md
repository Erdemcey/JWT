# Lab 6 — JWT authentication bypass via KID header path traversal

**Kaynak:** https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-kid-header-path-traversal

## Amaç

Bu laboratuvarda hedef, `kid` (Key ID) başlığında path traversal zafiyetinden faydalanarak null anahtar ile imzalanmış bir admin token üretmek ve sistem yetki kontrolünü atlatarak `Carlos` kullanıcısını silmektir.

## Kısa Özet

JWT token'ının header'ında bulunan `kid` alanı genellikle sunucunun anahtarları yönettiği bir store'dan hangi key'i kullanacağını belirtir. Bu laboratuvarda `kid` alanında path traversal (`../../../`) kullanılarak sunucu üzerinde önceden tanımlı boş bir dosyaya (ör. `/dev/null`) yönlendirilip, saldırgan tarafından kontrol edilen null anahtar (`AA==` Base64 formatında) ile imzalanan token kabul edilebilir.

## Analiz

- Sistem HMAC-SHA256 (`HS256`) algoritması kullanıyor; bu simetrik imzalama yöntemidir.
- `kid` başlığı sunucu tarafında path traversal açısından kontrol edilmiyor.
- Zafiyet: `kid` değerinde `../` ifadeleri kullanarak `/dev/null` gibi bilinen dosyalara yönlendirilirse, sunucu bunları anahtar dosyası olarak açmaya çalışır.
- `/dev/null` dosyasının içeriği boş olduğundan, saldırgan boş (null) anahtar ile imzalanan token'ı imzasız kabul ettirebilir.

## Saldırı Adımları (PoC)

### 1. Aşama: Yakalama ve İlk İnceleme

1. Tarayıcının geliştirici araçlarından veya Burp Suite ile orijinal JWT token'ını yakalayın.
2. Token'ı `jwt.io` veya Burp JWK Token Editorü'nde açıp `HS256` algoritmasının kullanıldığını doğrulayın.

### 2. Aşama: Null Anahtar ile Token Hazırlama

1. Burp Suite JWT Token Editorü'nde **simetrik anahtar** seçeneğine gidin.
2. Anahtar değeri olarak `AA==` (Base64 formatında null/boş karakter) girin.
3. Header kısmını aşağıdaki şekilde düzenleyin:

```json
{
  "kid": "../../../../../../../dev/null",
  "alg": "HS256"
}
```

**Açıklama:** `../` ifadeleri sunucudaki dosya sisteminde kök dizine kadar geri gitmek için kullanılır. `/dev/null` dosyası Linux/Unix sistemlerinde boş bir dosyadır ve içeriği null'dır.

4. Payload kısmını aşağıdaki şekilde düzenleyin:

```json
{
  "iss": "portswigger",
  "exp": <future_timestamp>,
  "sub": "administrator"
}
```

`exp` değerini gelecekteki bir timestamp ile değiştirin (ör. `1772222906`).

### 3. Aşama: Token İmzalama ve Gönderme

1. JWK Token Editorü'nde "Sign" düğmesine basıp token'ı `AA==` null anahtarı ile imzalayın.
2. Oluşturulan token'ı kopyalayın.
3. Tarayıcının DevTools'unda session cookie'sini bu yeni token ile değiştirin veya Burp Repeater'da cookie'yi güncelleyin.
4. `/admin` endpoint'ine istek gönderin:

```bash
curl -sS -b "session=<MODIFIED_TOKEN>" https://TARGET-URL/admin
```

### 4. Aşama: Exploit Tamamlama

1. Admin paneline başarıyla giriş yaptığınızı doğrulayın.
2. `Carlos` kullanıcısını silme endpoint'ine gidin:

```
https://TARGET-URL/admin/delete?username=carlos
```

3. Labı tamamlayın.

## Sonuç

Path traversal zafiyeti sayesinde `kid` başlığında `/dev/null` dosyasına yönlendirdik. Null anahtar ile imzalanan token, sunucu tarafından boş anahtar ile doğrulanmış ve kabul edilmiştir. Bu şekilde admin yetkisiyle işlem yapabilme imkanı elde ettik.

## Tavsiyeler / Mitigasyon

- **Kid doğrulaması:** Sunucu, `kid` değerini istemciden gelen girdiye göre doğrudan dosya yolu olarak kullanmamalıdır. Whitelist yöntemi ile sadece önceden tanımlı key ID'leri kabul etmelidir.
- **Path traversal kontrolü:** `kid` değerinde `../`, `..\\` gibi path traversal karakterleri kontrol edilip reddedilmelidir.
- **Anahtar yönetimi:** Null veya boş anahtarlar asla kullanılmamalıdır. HMAC'de simetrik anahtarlar güçlü ve yeterince uzun olmalıdır.
- **Input sanitization:** Token başlıklarının tüm alanları sıkı bir şekilde doğrulanmalıdır.
- **Kütüphane güvenliği:** JWT işlemleri için güncel ve güvenli kütüphaneler kullanılmalıdır.

## Kaynaklar

- PortSwigger lab: https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-kid-header-path-traversal
- JWT analiz: https://www.jwt.io/

---


