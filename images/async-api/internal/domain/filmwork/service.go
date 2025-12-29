package filmwork

import (
	"context"
	"fmt"
)

type FilmworkService interface {
	GetByID(ctx context.Context, id string) (*Filmwork, error)
	GetAll(ctx context.Context, page int, size int) ([]*BaseFilmwork, error)
	Search(ctx context.Context, query string, limit int) ([]*BaseFilmwork, error)
}

type filmworkServiceImpl struct {
	repo Repository
}

func NewFilmworkService(repo Repository) FilmworkService {
	return &filmworkServiceImpl{
		repo: repo,
	}
}

func (s *filmworkServiceImpl) GetByID(ctx context.Context, id string) (*Filmwork, error) {
	f, err := s.repo.GetByID(ctx, id)
	if err != nil {
		return nil, fmt.Errorf("failed to get filmwork: %w", err)
	}
	return f, nil
}

func (s *filmworkServiceImpl) GetAll(ctx context.Context, page int, size int) ([]*BaseFilmwork, error) {
	filmworks, err := s.repo.GetAll(ctx, page, size)
	if err != nil {
		return nil, fmt.Errorf("failed to get filmworks: %w", err)
	}
	return filmworks, nil
}

func (s *filmworkServiceImpl) Search(ctx context.Context, query string, limit int) ([]*BaseFilmwork, error) {
	filmworks, err := s.repo.Search(ctx, query, limit)
	if err != nil {
		return nil, fmt.Errorf("failed to search filmworks: %w", err)
	}
	return filmworks, nil
}
