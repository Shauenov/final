from fastapi import APIRouter

from app.modules.auth.auth_router import auth_router
from app.modules.user.user_router import user_router
from app.modules.statistics.statistics_router import statistics_router
from app.modules.music.music_router import music_router
from app.modules.playlist.playlist_router import playlist_router
from app.modules.genre.genre_router import genre_router
from app.modules.videos.router import router as video_router
from app.modules.ads.ads_router import ad_router
# from app.modules.books.books_router import books_router

api_router = APIRouter()

# порядок соответствует навигации админки
api_router.include_router(auth_router, tags=["auth"])
api_router.include_router(user_router, prefix="/users", tags=["users"])
api_router.include_router(music_router, tags=["Music"])
api_router.include_router(playlist_router, tags=["Playlist"])
api_router.include_router(genre_router, tags=["Genres"])
api_router.include_router(statistics_router, tags=["Statistics"])
api_router.include_router(ad_router, tags=["Ads"])

api_router.include_router(video_router)
# api_router.include_router(books_router, prefix="/books", tags=["books"])
