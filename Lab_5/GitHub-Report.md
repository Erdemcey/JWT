# Lab 5 — JWT authentication bypass via JKU header injection

**Kaynak:** https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-jku-header-injection

## Amaç

Bu laboratuvarda hedef, JKU (JWK Set URL) başlığı injeksiyonu yöntemi kullanarak kendi özel anahtarlarıyla imzalanmış bir admin token üretmek ve sistem yetki kontrolünü atlatarak `Carlos` kullanıcısını silmektir.

## Kısa Özet

JWT token'ında `jku` başlığı, token imzasını doğrulamak için kullanılacak JWK (JSON Web Key) setinin bulunduğu URL'i gösterir. `kid` alanı ise bu setinden hangi key'in kullanılacağını belirtir. Sunucu, istemcinin sağladığı URL'den key seti indirerek token'ı doğrularsa, saldırgan kendi sunucusunda (veya sağlanan sunucu alanında) sahte bir JWK seti yerleştirerek ve bunu JKU başlığında referans göstererek doğrulamayı atlatabilir.

## Analiz

- Sistem JWT doğrulaması yaparken `jku` başlığında verilen URL'den JWK seti almaktadır.
- `kid` alanı, JWK seti içinde hangi key'in kullanılacağını gösterir.
- Zafiyet: Sunucu, saldırganın kontrol ettiği (veya erişebildiği) URL'den seti alıyorsa, saldırgan kendi anahtarını bu sete yerleştirebilir.

## Saldırı Adımları (PoC)

### 1. Aşama: JWK Seti Hazırlama

Burp Suite'te JWK Token Editorü eklentisini kullanarak yeni bir RSA anahtarı üretin veya Python betiği ile oluşturun:

1. Burp Suite JWK Token Editorü ile yeni bir anahtar oluşturun (veya `cryptography` kütüphanesi ile).
2. Üretilen key bilgilerini (public ve private key parametreleri) alıp aşağıdaki JSON formatında bir dosya oluşturun:

```json
{
  "keys": [
    {
      "kty": "RSA",
      "kid": "ae22c587-3777-493f-b48e-8df16d669a61",
      "n": "<RSA_MODULUS>",
      "e": "AQAB",
      "d": "<PRIVATE_EXPONENT>",
      "p": "<PRIME_P>",
      "q": "<PRIME_Q>",
      "dp": "<EXPONENT1>",
      "dq": "<EXPONENT2>",
      "qi": "<COEFFICIENT>"
    }
  ]
}
```

3. Bu JSON dosyasını uygun bir web sunucusuna (`exploit-ac123abc.web-security-academy.net` gibi) yükleyin ve bir URL elde edin (ör. `https://exploit-server.com/jwks.json`).

### 2. Aşama: Token Manipülasyonu ve İmzalama

1. Yakalanan orijinal JWT token'ını Burp'ün Repeater veya JWK Token Editorü'nde açın.
2. Token header kısmını düzenleyin:
   - `jku` alanını eklerin ve yukarıda sunucuya yüklediğiniz JWK seti URL'ini yazın.
   - `kid` değerini yukarıda üretilen anahtarın `kid` değeri ile değiştirin.

```json
{
  "jku": "https://exploit-server.com/jwks.json",
  "kid": "ae22c587-3777-493f-b48e-8df16d669a61",
  "alg": "RS256"
}
```

3. Payload kısmını düzenleyin:
   - `sub` alanını `wiener`'den `administrator` olarak değiştirin.

```json
{
  "iss": "portswigger",
  "exp": <future_timestamp>,
  "sub": "administrator"
}
```

4. JWK Token Editorü'nde "Sign" butonuna basarak token'ı kendi private key ile imzalayın.
5. Oluşturulan token'ı kopyalayın.

### 3. Aşama: Exploit

1. Tarayıcıda uygulamaya gidiş yapın ve session cookie'sini manipüle edilen token ile değiştirin (DevTools > Storage > Cookies).
2. Sayfayı yenileyin; `/admin` paneline admin yetkisiyle erişim sağlayabilirsiniz.
3. Admin panelinden `Carlos` kullanıcısını silin ve labı tamamlayın.

## Sonuç

JKU header injection zafiyeti sayesinde kendi anahtarımızla imzalanmış token'ı oluşturduk ve sunucu, JKU URL'sinden alınan key seti ile bu token'ı doğru kabul etti. Bu şekilde admin yetkisiyle işlem yapabilme imkanı elde ettik.

## Tavsiyeler / Mitigasyon

- **JKU URL'sini önceden tanımlayın:** Sunucu, `jku` başlığını asla dinamik olarak kabul etmemelidir. Beklenen JWK seti URL'si sabit olmalıdır.
- **JWK seti URL'sini doğrulayın:** Sunucu, sadece whitelist'teki URL'lerden JWK seti indirebilmelidir.
- **Key ID (kid) doğrulaması:** `kid` alanı sadece beklenen ve önceden tanınan key setinde aranmalıdır.
- **JKU başlığını kapatın:** Eğer gerekli değilse, JKU başlığı tamamen devre dışı bırakılmalıdır.
- **İstemci tarafı doğrulaması:** Token imzasını doğrulamak için sabit bir public key kullanın; hiçbir zaman istemcinin sağladığı parametrelere güvenmeyin.

## Kaynaklar

- PortSwigger lab: https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-jku-header-injection
- JWT analiz: https://www.jwt.io/

---


