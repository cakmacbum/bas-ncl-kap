# Geometri ajanı

Geometri ajanı, kullanıcının Türkçe komutunu temel geometri değişikliklerine
çevirir. Öneriler projeye yazılmadan önce sağ çekmecede onaylanır.

## Sağlayıcı ayarları

`.env.example` dosyasını `.env` olarak kopyalayıp aşağıdaki değerleri doldurun:

- `GEOMETRY_AGENT_BASE_URL`: OpenAI uyumlu API kök adresi. OpenRouter varsayılanı
  `https://openrouter.ai/api/v1` adresidir.
- `GEOMETRY_AGENT_API_KEY`: Yalnızca backend tarafında kullanılan gizli anahtar.
- `GEOMETRY_AGENT_MODEL`: Sağlayıcıdaki model kimliği.
- `GEOMETRY_AGENT_TIMEOUT_SECONDS`: İstek zaman aşımı; varsayılan 30 saniye.

Backend'i dosyayla başlatmak için:

```powershell
uvicorn apps.api.main:app --reload --env-file .env
```

Anahtar ve model ayarlanmadan ekran kullanılabilir, ancak `Yorumla` isteği yapılandırma
uyarısı döndürür.

## Güvenlik sınırı

Model tam proje verisini almaz ve projeyi doğrudan değiştiremez. Yalnızca aktif gövde,
bombe kimlikleri ve çap bağlantı durumu gönderilir. Dönen yapı hem backend hem frontend
tarafında izin verilen alanlarla sınırlanır. Malzeme, kaynak, nozul, destek ve tasarım
koşulları ajan kapsamı dışındadır.

## Geri alma

Ajan özelliği ayrı bir Git commit'inde tutulur. Özellik commit'ini geri almak için
commit kimliğiyle `git revert <commit>` kullanılabilir; ajan öncesi kontrol noktası
`5ca3faf` olarak korunur.
