package person

import (
	"context"
	"fmt"
)

type PersonService interface {
	GetByID(ctx context.Context, id string) (*Person, error)
	GetAll(ctx context.Context, page int, size int) ([]*Person, error)
	Search(ctx context.Context, query string, limit int) ([]*Person, error)
	GetPersonFilmworks(ctx context.Context, id string) ([]*PersonBaseFilmwork, error)
}

type personServiceImpl struct {
	repo Repository
}

func NewPersonService(repo Repository) PersonService {
	return &personServiceImpl{
		repo: repo,
	}
}

func (s *personServiceImpl) GetByID(ctx context.Context, id string) (*Person, error) {
	g, err := s.repo.GetByID(ctx, id)
	if err != nil {
		return nil, fmt.Errorf("failed to get person: %w", err)
	}
	return g, nil
}

func (s *personServiceImpl) GetAll(ctx context.Context, page int, size int) ([]*Person, error) {
	persons, err := s.repo.GetAll(ctx, page, size)
	if err != nil {
		return nil, fmt.Errorf("failed to get persons: %w", err)
	}
	return persons, nil
}

func (s *personServiceImpl) Search(ctx context.Context, query string, limit int) ([]*Person, error) {
	persons, err := s.repo.Search(ctx, query, limit)
	if err != nil {
		return nil, fmt.Errorf("failed to get persons: %w", err)
	}
	return persons, nil
}

func (s *personServiceImpl) GetPersonFilmworks(ctx context.Context, id string) ([]*PersonBaseFilmwork, error) {
	filmworks, err := s.repo.Filmworks(ctx, id)
	if err != nil {
		return nil, fmt.Errorf("failed to get person filmworks: %w", err)
	}
	return filmworks, nil
}
