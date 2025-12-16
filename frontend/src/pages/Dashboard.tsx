import { useEffect, useMemo, useState } from "react";
import { getToken, clearToken } from "../auth";
import { listVideos, listBooks, listMusic, listPlaylists, me } from "../api";
import { Nav } from "../components/Nav";

type Profile = { fullname: string; role: "user" | "admin" };

type Category = "videos" | "books" | "music" | "playlists";

export default function Dashboard() {
  const token = getToken()!;
  const [profile, setProfile] = useState<Profile | null>(null);
  const [data, setData] = useState<Record<Category, any[]>>({
    videos: [],
    books: [],
    music: [],
    playlists: [],
  });
  const [active, setActive] = useState<Category>("videos");
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const u = await me(token);
        setProfile({ fullname: u.fullname ?? u.phone, role: u.role });

        const results = await Promise.allSettled([
          listVideos(token),
          listBooks(token),
          listMusic(token),
          listPlaylists(token),
        ]);

        const [videosRes, booksRes, musicRes, playlistsRes] = results;
        setData({
          videos: videosRes.status === "fulfilled" ? videosRes.value : [],
          books: booksRes.status === "fulfilled" ? booksRes.value : [],
          music: musicRes.status === "fulfilled" ? musicRes.value : [],
          playlists: playlistsRes.status === "fulfilled" ? playlistsRes.value : [],
        });

        if (results.some((r) => r.status === "rejected")) {
          const msgs = results
            .map((r, i) => (r.status === "rejected" ? ["videos", "books", "music", "playlists"][i] : null))
            .filter(Boolean)
            .join(", ");
          setError(`Не удалось загрузить: ${msgs}`);
        } else {
          setError("");
        }
      } catch (e: any) {
        setError("Ошибка загрузки: " + e.message);
      }
    })();
  }, [token]);

  const items = useMemo(() => data[active] || [], [data, active]);

  if (error) {
    return (
      <div style={{ padding: 16 }}>
        {error}{" "}
        <button
          onClick={() => {
            clearToken();
            location.href = "/login";
          }}
        >
          Войти заново
        </button>
      </div>
    );
  }

  return (
    <div style={{ padding: 16 }}>
      <Nav role={profile?.role ?? "user"} />
      <header style={{ marginBottom: 16 }}>
        <h2 style={{ margin: 0 }}>Hello, {profile?.role ?? "user"}</h2>
        <div style={{ color: "#555" }}>{profile?.fullname}</div>
      </header>

      <div style={{ display: "flex", gap: 12, marginBottom: 16, flexWrap: "wrap" }}>
        {(["videos", "books", "music", "playlists"] as Category[]).map((cat) => (
          <button
            key={cat}
            onClick={() => setActive(cat)}
            style={{
              padding: "8px 14px",
              borderRadius: 999,
              border: active === cat ? "1px solid #0f68f5" : "1px solid #e5e7eb",
              background: active === cat ? "#e7f0ff" : "#fff",
            }}
          >
            {cat}
          </button>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))", gap: 16 }}>
        {items.map((item) => (
          <Card key={item.id} type={active} item={item} />
        ))}
      </div>
    </div>
  );
}

function Card({ type, item }: { type: Category; item: any }) {
  const title = item.title || item.name || "Без названия";
  const description = item.description || item.author || "";

  const preview =
    (type === "videos" && item.preview_img) ||
    (type === "books" && item.cover_url) ||
    (type === "music" && item.preview_img) ||
    (type === "playlists" && item.preview_img) ||
    null;

  const link =
    (type === "videos" && item.video) ||
    (type === "books" && item.file_url) ||
    (type === "music" && item.music_url) ||
    null;

  return (
    <div className="card" style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      {preview ? (
        <img src={preview} alt={title} style={{ width: "100%", borderRadius: 8, objectFit: "cover", aspectRatio: "16/9" }} />
      ) : (
        <div style={{ width: "100%", borderRadius: 8, background: "#f0f2f5", aspectRatio: "16/9" }} />
      )}
      <div style={{ fontWeight: 600 }}>{title}</div>
      <div style={{ color: "#555", fontSize: 14, minHeight: 40 }}>{description}</div>
      {link && (
        <a href={link} target="_blank" rel="noreferrer" style={{ color: "#0f68f5", fontWeight: 600 }}>
          Открыть
        </a>
      )}
    </div>
  );
}
