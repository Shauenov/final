import { useState } from "react";
import { getToken } from "../auth";
import { createGenre } from "../api";
import { Nav } from "../components/Nav";

export default function Admin() {
  const token = getToken()!;
  const [name, setName] = useState("");
  const [type, setType] = useState<"music" | "movie" | "book">("music");
  const [msg, setMsg] = useState("");

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setMsg("");
    try {
      await createGenre(token, { name, type });
      setMsg("Создано");
    } catch (err: any) {
      setMsg("Ошибка: " + err.message);
    }
  }

  return (
    <div style={{ padding: 16 }}>
      <Nav role="admin" />
      <h2>Админка</h2>

      <h3>Новый жанр</h3>
      <form onSubmit={submit} style={{ display: "grid", gap: 8, maxWidth: 320 }}>
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Название" />
        <select value={type} onChange={(e) => setType(e.target.value as any)}>
          <option value="music">music</option>
          <option value="movie">movie</option>
          <option value="book">book</option>
        </select>
        <button type="submit">Создать</button>
      </form>
      {msg && <div>{msg}</div>}

      <p style={{ marginTop: 24, color: "#555" }}>
        Для загрузки видео/музыки/книг потребуется форма с FormData на соответствующие эндпоинты.
      </p>
    </div>
  );
}
