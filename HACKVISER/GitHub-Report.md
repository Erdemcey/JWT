# Quiz — JWT Manipulation (Alg: none) — HACKVİSER

## Amaç

Hedef, uygulamada admin hesabına erişim sağlayarak parola bilgisini elde etmektir.

## Kısa Özet

Uygulama tarafından kullanılan JWT'de (`header`) `alg` alanı `none` olarak ayarlanmıştır. Bu durum, sunucu tarafı doğrulamasının yetersiz veya hatalı olabileceğini gösterir; dolayısıyla header ve payload içeriği doğrudan değiştirilebilmekte ve sunucu bu değişiklikleri tespit edememektedir. Bu zafiyet kullanılarak `sub` (muhtemel kullanıcı ID) değeri değiştirilmiş ve admin hesabına erişilmiştir.

## Analiz

- Yakalanan token incelendiğinde header veya payload Base64URL ile kodlanmış durumda ve header'da `alg: none` değeri bulunuyor.
- Token içindeki `sub` alanı `2` olarak gözükmektedir; bu muhtemelen kullanıcı kimliğini (user id) temsil etmektedir.
- `alg: none` nedeniyle sunucu imza doğrulaması yapmıyor veya `none` algoritmasını kabul edecek şekilde yapılandırılmış; bu da payload değişikliklerinin tespit edilmemesine yol açıyor.

## Saldırı Adımları (PoC)

1. Oturum açılmış durumda olan kullanıcının JWT'sini (cookie veya Authorization header) yakalayın.
2. Token'ı `header.payload.signature` formatında parçalayın.
3. `header` kısmını Base64URL decode edin; `alg` değerinin `none` olduğunu doğrulayın.
4. `payload` kısmını decode ederek `sub` değerini `1` (admin ID) olarak değiştirin.
5. Header ve payload'ı Base64URL ile tekrar kodlayın. `alg: none` kullanıldığında imza kısmı boş bırakılır veya kaldırılır.
6. Oluşturduğunuz yeni token ile hedef uygulamaya istek gönderin (ör. `Cookie: session=<TOKEN>` veya `Authorization: Bearer <TOKEN>`).
7. `index.php` veya `/admin` gibi yönetici sayfalarına erişerek admin yetkisini doğrulayın ve parola bilgisine ulaşın.

Örnek istek (cookie ile):

```bash
curl -sS -b "session=<MODIFIED_TOKEN>" https://TARGET-URL/index.php
```

Not: Bu PoC, yalnızca eğitim amaçlı ve hedef sistem sahiplerinin izni ile gerçekleştirilmelidir.

## Sonuç

`alg: none` zafiyeti kullanılarak payload üzerinde yapılan değişiklikler sunucu tarafından fark edilmedi ve sonuç olarak admin hesabına erişilerek parola bilgisi elde edildi.

## Önerilen Düzeltmeler (Mitigasyon)

- Sunucu tarafında beklenen imzalama algoritmasını sabit olarak belirleyin ve istemciden gelen `alg` başlığını asla güvenilir kabul etmeyin.
- `alg: none` desteğini tamamen devre dışı bırakın veya sunucu tarafından reddedilsin.
- JWT doğrulaması için güvenilir, güncel kütüphaneler kullanın ve imza doğrulamasını zorunlu kılın.
- Tüm kritik işlemler için ek sunucu tarafı kontrolleri uygulayın (ör. kullanıcı yetki kontrolü, ID ile kullanıcı doğrulaması), yalnızca token içeriğine güvenmeyin.
- Güvenlik testleri ve kod incelemeleri ile benzer yanlış konfigürasyonların önceden tespit edilmesini sağlayın.

## Kaynaklar

- JWT temel bilgileri: https://www.jwt.io/

---

_Rapor `Quiz_rapor.txt` içeriğine dayanılarak hazırlandı. İsterseniz rapora istek/yanıt örnekleri, Burp ekran görüntüleri veya otomatik PoC script'i ekleyebilirim._
