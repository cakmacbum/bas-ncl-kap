// Anonim istemci kimliği: localStorage'da kalıcı UUID (depolama yoksa oturum boyunca bellekte).
// Sunucu bunu proje sahipliği için X-Client-Id başlığında kullanır. Gizli bir sır DEĞİLDİR.

const KEY = "pvs.clientId";
const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;

let memoryId: string | null = null;

export function getClientId(): string {
  if (memoryId) return memoryId;
  try {
    const stored = window.localStorage.getItem(KEY);
    if (stored && UUID_RE.test(stored)) {
      memoryId = stored;
      return stored;
    }
  } catch {
    /* depolama yok/engelli */
  }
  const id = crypto.randomUUID();
  memoryId = id;
  try {
    window.localStorage.setItem(KEY, id);
  } catch {
    /* yalnızca bellekte kalır */
  }
  return id;
}
