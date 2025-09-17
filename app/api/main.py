from fastapi import APIRouter

from app.modules.auth.auth_router import auth_router
from app.modules.user.user_router import user_router

# контентные модули по ТЗ
# from app.modules.video.video_router import video_router
# from app.modules.music.music_router import music_router
# from app.modules.playlist.playlist_router import playlist_router
# from app.modules.books.books_router import books_router
# from app.modules.stats.stats_router import stats_router

api_router = APIRouter()

# порядок соответствует навигации админки
api_router.include_router(auth_router, tags=["auth"])
api_router.include_router(user_router, prefix="/users", tags=["users"])
# api_router.include_router(video_router, prefix="/video", tags=["video"])
# api_router.include_router(music_router, prefix="/music", tags=["music"])
# api_router.include_router(playlist_router, prefix="/playlist", tags=["playlist"])
# api_router.include_router(books_router, prefix="/books", tags=["books"])
# api_router.include_router(stats_router, prefix="/stats", tags=["stats"])
