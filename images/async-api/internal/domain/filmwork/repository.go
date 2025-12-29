package filmwork

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
	GetByID(ctx context.Context, filmworkId string) (*Filmwork, error)
	GetAll(ctx context.Context, page int, size int) ([]*BaseFilmwork, error)
	Search(ctx context.Context, q string, limit int) ([]*BaseFilmwork, error)
}

type filmworkRepository struct {
	es *elasticsearch.Client
}

func NewFilmworkRepository(es *elasticsearch.Client) Repository {
	return &filmworkRepository{es: es}
}

func (r *filmworkRepository) GetByID(ctx context.Context, filmworkId string) (*Filmwork, error) {
	req := esapi.GetRequest{
		Index:      "movies",
		DocumentID: filmworkId,
	}

	resp, err := req.Do(ctx, r.es)
	if err != nil {
		return nil, fmt.Errorf("Elasticsearch request error: %w", err)
	}
	defer resp.Body.Close()

	if resp.IsError() {
		if resp.StatusCode == 404 {
			return nil, fmt.Errorf("Filmwork with ID '%s' not found", filmworkId)
		}
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("Elasticsearch error [%d]: %s", resp.StatusCode, body)
	}

	var response struct {
		Source Filmwork `json:"_source"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, fmt.Errorf("response parsing error: %w", err)
	}

	return &response.Source, nil
}

func (r *filmworkRepository) GetAll(ctx context.Context, page int, size int) ([]*BaseFilmwork, error) {
	offset := (page - 1) * size
	query := map[string]interface{}{
		"query": map[string]interface{}{
			"match_all": map[string]interface{}{},
		},
		"from": offset,
		"size": size,
	}

	var buf bytes.Buffer
	if err := json.NewEncoder(&buf).Encode(query); err != nil {
		return nil, fmt.Errorf("request coding error: %w", err)
	}

	req := esapi.SearchRequest{
		Index: []string{"movies"},
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
					ID     string  `json:"id"`
					Title  string  `json:"title"`
					Rating float32 `json:"rating"`
				} `json:"_source"`
			} `json:"hits"`
		} `json:"hits"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, fmt.Errorf("response parsing error: %w", err)
	}

	filmworks := make([]*BaseFilmwork, 0, len(response.Hits.Hits))
	for _, hit := range response.Hits.Hits {
		filmworks = append(filmworks, &BaseFilmwork{
			ID:     hit.Source.ID,
			Title:  hit.Source.Title,
			Rating: hit.Source.Rating,
		})
	}

	return filmworks, nil
}

func (r *filmworkRepository) Search(ctx context.Context, q string, limit int) ([]*BaseFilmwork, error) {
	var queryBody map[string]interface{}

	if q == "" {
		queryBody = map[string]interface{}{
			"query": map[string]interface{}{
				"match_all": map[string]interface{}{},
			},
			"size": limit,
		}
	} else {
		queryBody = map[string]interface{}{
			"query": map[string]interface{}{
				"multi_match": map[string]interface{}{
					"query":     q,
					"fields":    []string{"title", "description"},
					"type":      "best_fields",
					"fuzziness": "AUTO",
				},
			},
			"size": limit,
		}
	}

	var buf bytes.Buffer
	if err := json.NewEncoder(&buf).Encode(queryBody); err != nil {
		return nil, fmt.Errorf("request coding error: %w", err)
	}

	req := esapi.SearchRequest{
		Index: []string{"movies"},
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
					ID          string  `json:"id"`
					Title       string  `json:"title"`
					Description string  `json:"description"`
					Rating      float32 `json:"rating"`
				} `json:"_source"`
				Highlight struct {
					Title       []string `json:"title"`
					Description []string `json:"description"`
				} `json:"highlight"`
			} `json:"hits"`
		} `json:"hits"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, fmt.Errorf("response parsing error: %w", err)
	}

	filmworks := make([]*BaseFilmwork, 0, len(response.Hits.Hits))
	for _, hit := range response.Hits.Hits {
		filmworks = append(filmworks, &BaseFilmwork{
			ID:     hit.Source.ID,
			Title:  hit.Source.Title,
			Rating: hit.Source.Rating,
		})
	}

	return filmworks, nil
}
