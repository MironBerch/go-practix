package genre

import (
	"context"
	"fmt"
)

type GenreService interface {
	GetByID(ctx context.Context, id string) (*Genre, error)
	GetAll(ctx context.Context) ([]*Genre, error)
}

type genreServiceImpl struct {
	repo Repository
}

func NewGenreService(repo Repository) GenreService {
	return &genreServiceImpl{
		repo: repo,
	}
}

func (s *genreServiceImpl) GetByID(ctx context.Context, id string) (*Genre, error) {
	g, err := s.repo.GetByID(ctx, id)
	if err != nil {
		return nil, fmt.Errorf("failed to get genre: %w", err)
	}
	return g, nil
}

func (s *genreServiceImpl) GetAll(ctx context.Context) ([]*Genre, error) {
	genres, err := s.repo.GetAll(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to get genres: %w", err)
	}
	return genres, nil
}
