import cv2
import os
import numpy as np
import insightface

# Загружаем модель
app = insightface.app.FaceAnalysis(
    providers=["CUDAExecutionProvider", "CPUExecutionProvider"]
)
app.prepare(ctx_id=0, det_size=(640, 640))

known_faces = {}


def load_known_faces(path="known_faces"):
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.lower().endswith((".jpg", ".jpeg", ".png")):
                full_path = os.path.join(root, file)
                name = (
                    os.path.basename(root)
                    if root != path
                    else os.path.splitext(file)[0]
                )

                img = cv2.imread(full_path)
                faces = app.get(img)
                if not faces:
                    print(f"[!] Лицо не найдено: {full_path}")
                    continue

                emb = faces[0].normed_embedding
                if name not in known_faces:
                    known_faces[name] = []
                known_faces[name].append(emb)
                print(f"[+] Зарегистрирован {name} из {file}")

    # усредняем несколько фото одного человека
    for name, embs in known_faces.items():
        known_faces[name] = np.mean(embs, axis=0)


# Загружаем всех из папки
load_known_faces("database")

# Запускаем камеру
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    faces = app.get(frame)
    for face in faces:
        box = face.bbox.astype(int)
        emb = face.normed_embedding

        best_match = None
        best_score = -1
        for name, ref_emb in known_faces.items():
            score = np.dot(emb, ref_emb)  # cosine similarity
            if score > best_score:
                best_score = score
                best_match = name

        label = f"{best_match} ({best_score:.2f})" if best_match else "Unknown"
        cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)
        cv2.putText(
            frame,
            label,
            (box[0], box[1] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
        )

    cv2.imshow("Face Recognition", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
