from uuid import UUID

from fastapi import APIRouter, Depends, Path

from api.dependencies import check_filmwork_exist
from api.paginator import Paginator
from models.models import FilmworkBookmark
from services.auth import AuthService
from services.bookmarks import BookmarksService, get_bookmarks_service

router = APIRouter(tags=['bookmarks'])


@router.get(
    '/bookmarks',
    summary='Просмотр списка закладок',
    response_description='Закладки пользователя',
    response_model=list[FilmworkBookmark],
)
async def get_bookmarks(
    auth: AuthService = Depends(),
    service: BookmarksService = Depends(get_bookmarks_service),
    paginator: Paginator = Depends(),
) -> list[FilmworkBookmark]:
    result = await service.filter(user_id=auth.user_id, paginator=paginator)
    return result


@router.post(
    '/filmworks/{filmwork_id}/bookmarks',
    summary='Добавление фильма в закладки',
    response_description='Результат добавления фильма в закладки',
    response_model=FilmworkBookmark,
    dependencies=[Depends(check_filmwork_exist)],
)
async def bookmark_filmwork(
    auth: AuthService = Depends(),
    service: BookmarksService = Depends(get_bookmarks_service),
    filmwork_id: UUID = Path(title='UUID фильма'),
) -> FilmworkBookmark:
    result = await service.update(user_id=auth.user_id, filmwork_id=filmwork_id)
    return result


@router.delete(
    '/filmworks/{filmwork_id}/bookmarks',
    summary='Удаление фильма из закладок',
    response_description='Результат удаления фильма из закладок',
    response_model=FilmworkBookmark,
    dependencies=[Depends(check_filmwork_exist)],
)
async def unbookmark_film(
    auth: AuthService = Depends(),
    service: BookmarksService = Depends(get_bookmarks_service),
    filmwork_id: UUID = Path(title='UUID фильма'),
) -> FilmworkBookmark:
    result = await service.remove(user_id=auth.user_id, filmwork_id=filmwork_id)
    return result
