# Lab 7 — JWT authentication bypass via algorithm confusion

**Kaynak:** https://portswigger.net/web-security/jwt/algorithm-confusion/lab-jwt-authentication-bypass-via-algorithm-confusion
## Amaç

Bu laboratuvarda hedef, algoritma karışıklığı (algorithm confusion) zafiyetinden faydalanarak RSA public key'in HS256 simetrik anahtarı gibi kabul edilmesinden yararlanıp admin token üretmek ve uygulamada `Carlos` kullanıcısını silmektir.
## Kısa Özet

Algorithm confusion zafiyeti sunucunun, JWT doğrulama esnasında hangi algoritmanın kullanılacağını katı şekilde kısıtlamamasından kaynaklanır. Eğer sunucu hem asimetrik (RS256) hem de simetrik (HS256) algoritmaları kabul ediyorsa, saldırgan RS256 için kullanılan public key'i HS256'ın secret (k) değeri olarak kullanarak doğrulamayı atlatabilir.
## Analiz

- Hedef uygulama JWT doğrulamasında hem RS256 hem de HS256 algoritmalarını kabul ediyor olabilir.
- Sunucu, hangi anahtarın hangi algoritmada kullanılacağını katı şekilde kontrol etmiyor.
- JWK seti veya sunucu üzerinde bulunan anahtar dosyalarından elde edilen public key, base64'e çevrilip HS256 için simetrik anahtar olarak kullanılabiliyorsa zafiyet oluşur.
## Saldırı Adımları (PoC)

1. Hedef sunucuda (veya yakalanan token içinde referans verilen yerde) bulunan `JWK.json` veya benzeri dosyaları araştırın ve `keys` içindeki public key değerlerini elde edin.
2. Elde edilen RSA public key'i PEM formatında alın ve base64'e çevirin. Örnek çıktı: `LS0tLS1CRUdJTiBQVUJMSUMg...`
3. Bu base64 içeriğini HS256 için kullanılacak simetrik anahtar (`k`) olarak kullanacak bir key objesi oluşturun:
```json
{
   "kty": "oct",
   "kid": "8dd1a353-ef07-49c6-be7b-b369143725ea",
   "k": "<BASE64_RSA_PUBLIC_KEY>"
}
```
4. JWT header'ını `HS256` olarak ayarlayın ve uygun `kid` değerini kullanın:

```json
{
   "kid": "7058b3bc-be59-4ae9-8e98-91bd5393faa5",
   "alg": "HS256"
}
```
5. Payload içindeki `sub` alanını `administrator` olarak değiştirin, `exp` değerini gelecekte bir timestamp ile güncelleyin ve token'ı HS256 ile, önceki adımda oluşturduğunuz `k` değeriyle imzalayın.

```json
{
   "iss": "portswigger",
   "exp": 1772224952,
   "sub": "administrator"
}
```
6. Oluşturduğunuz token'ı `/admin` yoluna gönderin ve admin paneline erişimi doğrulayın.
7. Admin panelinden `Carlos` kullanıcısını silerek labı tamamlayın.

## Sonuç

Algoritma karışıklığı zafiyeti kullanılarak sunucunun RS256 public key'ini HS256 secret olarak kabul etmesi sağlandı. Bu sayede `administrator` yetkisi veren token üretilebildi ve admin yetkisi elde edildi.
## Tavsiyeler / Mitigasyon

- Sunucu tarafında JWT doğrulaması yalnızca beklenen algoritmayı (ör. RS256) kabul edecek şekilde kısıtlanmalıdır.
- Asimetrik (RSA) ve simetrik (HMAC) anahtarlar kesinlikle karıştırılmamalıdır; public key asla secret olarak kullanılmamalıdır.
- `kid` doğrulaması yapılarak yalnızca önceden tanımlı ve güvenilir anahtarlar kullanılmalıdır.
- Anahtar kaynaklarının ve izin verilen URL'lerin whitelist kontrolü uygulanmalıdır.
- Algoritma karışıklığı senaryolarını kapsayan düzenli güvenlik testleri uygulanmalıdır.
## Kaynaklar

- PortSwigger lab: https://portswigger.net/web-security/jwt/algorithm-confusion/lab-jwt-authentication-bypass-via-algorithm-confusion
- JWT analiz: https://www.jwt.io/

---
