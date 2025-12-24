package genre

import (
	"context"
	"fmt"

	"bytes"
	"encoding/json"
	"github.com/elastic/go-elasticsearch/v9"
	"io"

	"github.com/elastic/go-elasticsearch/v9/esapi"
)

type Repository interface {
	GetByID(ctx context.Context, genreId string) (*Genre, error)
	GetAll(ctx context.Context) ([]*Genre, error)
}

type genreRepository struct {
	es *elasticsearch.Client
}

func NewGenreRepository(es *elasticsearch.Client) Repository {
	return &genreRepository{es: es}
}

func (r *genreRepository) GetByID(ctx context.Context, genreId string) (*Genre, error) {
	req := esapi.GetRequest{
		Index:      "genres",
		DocumentID: genreId,
	}

	resp, err := req.Do(ctx, r.es)
	if err != nil {
		return nil, fmt.Errorf("Elasticsearch request error: %w", err)
	}
	defer resp.Body.Close()

	if resp.IsError() {
		if resp.StatusCode == 404 {
			return nil, fmt.Errorf("genre with ID '%s' not found", genreId)
		}
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("Elasticsearch error [%d]: %s", resp.StatusCode, body)
	}
	var response struct {
		Source Genre `json:"_source"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, fmt.Errorf("response parsing error: %w", err)
	}

	return &response.Source, nil
}

func (r *genreRepository) GetAll(ctx context.Context) ([]*Genre, error) {
	query := map[string]interface{}{
		"query": map[string]interface{}{
			"match_all": map[string]interface{}{},
		},
		"size": 1000,
	}

	var buf bytes.Buffer
	if err := json.NewEncoder(&buf).Encode(query); err != nil {
		return nil, fmt.Errorf("request coding error: %w", err)
	}

	req := esapi.SearchRequest{
		Index: []string{"genres"},
		Body:  &buf,
	}

	resp, err := req.Do(ctx, r.es)
	if err != nil {
		return nil, fmt.Errorf("Elasticsearch search error: %w", err)
	}
	defer resp.Body.Close()

	if resp.IsError() {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("error Elasticsearch [%d]: %s", resp.StatusCode, body)
	}

	var response struct {
		Hits struct {
			Hits []struct {
				Source struct {
					ID          string `json:"id"`
					Name        string `json:"name"`
					Description string `json:"description"`
				} `json:"_source"`
			} `json:"hits"`
		} `json:"hits"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, fmt.Errorf("response parsing error: %w", err)
	}

	genres := make([]*Genre, 0, len(response.Hits.Hits))
	for _, hit := range response.Hits.Hits {
		genres = append(genres, &Genre{
			ID:          hit.Source.ID,
			Name:        hit.Source.Name,
			Description: hit.Source.Description,
		})
	}

	return genres, nil
}
