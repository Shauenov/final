const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
const API = `${API_BASE.replace(/\/+$/, "")}/api/v1`;

const headers = (token?: string) => ({
  "Content-Type": "application/json",
  ...(token ? { Authorization: `Bearer ${token}` } : {}),
});

export async function signIn(phone: string, password: string) {
  const res = await fetch(`${API}/auth/sign-in`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify({ phone, password }),
  });
  if (!res.ok) throw new Error("Auth failed");
  return res.json(); // {access_token, refresh_token}
}

export async function me(token: string) {
  const res = await fetch(`${API}/auth/me`, { headers: headers(token) });
  if (!res.ok) throw new Error("Unauthorized");
  return res.json();
}

export async function listVideos(token: string) {
  const res = await fetch(`${API}/videos?limit=50&offset=0`, { headers: headers(token) });
  if (!res.ok) throw new Error("Failed to load videos");
  return res.json();
}
export async function listBooks(token: string) {
  const res = await fetch(`${API}/books`, { headers: headers(token) });
  if (!res.ok) throw new Error("Failed to load books");
  return res.json();
}
export async function listMusic(token: string) {
  const res = await fetch(`${API}/musics/`, { headers: headers(token) });
  if (!res.ok) throw new Error("Failed to load music");
  return res.json();
}
export async function listPlaylists(token: string) {
  const res = await fetch(`${API}/playlists/`, { headers: headers(token) });
  if (!res.ok) throw new Error("Failed to load playlists");
  return res.json();
}

// admin example
export async function createGenre(token: string, data: { name: string; type: string }) {
  const res = await fetch(`${API}/genres`, {
    method: "POST",
    headers: headers(token),
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create genre");
  return res.json();
}
