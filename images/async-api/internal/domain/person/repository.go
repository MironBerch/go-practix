package person

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"

	"github.com/elastic/go-elasticsearch/v9"
	"github.com/elastic/go-elasticsearch/v9/esapi"
)

type Repository interface {
	GetByID(ctx context.Context, personId string) (*Person, error)
	GetAll(ctx context.Context, page int, size int) ([]*Person, error)
	Search(ctx context.Context, query string, limit int) ([]*Person, error)
	Filmworks(ctx context.Context, personId string) ([]*PersonBaseFilmwork, error)
	GetPersonFilmworkIDsAndRoles(ctx context.Context, personId string) (map[string][]string, error)
}

type personRepository struct {
	es *elasticsearch.Client
}

func NewPersonRepository(es *elasticsearch.Client) Repository {
	return &personRepository{es: es}
}

func (r *personRepository) GetByID(ctx context.Context, personId string) (*Person, error) {
	req := esapi.GetRequest{
		Index:      "persons",
		DocumentID: personId,
	}

	resp, err := req.Do(ctx, r.es)
	if err != nil {
		return nil, fmt.Errorf("Elasticsearch request error: %w", err)
	}
	defer resp.Body.Close()

	if resp.IsError() {
		if resp.StatusCode == 404 {
			return nil, fmt.Errorf("Person with ID '%s' not found", personId)
		}
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("Elasticsearch error [%d]: %s", resp.StatusCode, body)
	}

	var response struct {
		Source EsBasePerson `json:"_source"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, fmt.Errorf("response parsing error: %w", err)
	}

	filmworks, err := r.GetPersonFilmworkIDsAndRoles(ctx, response.Source.ID)
	if err != nil {
		return nil, fmt.Errorf("failed to get filmworks: %w", err)
	}

	return &Person{
		ID:          response.Source.ID,
		Name:        response.Source.Name,
		FilmworkIDs: filmworks["filmwork_ids"],
		Roles:       filmworks["roles"],
	}, nil
}

func (r *personRepository) GetAll(ctx context.Context, page int, size int) ([]*Person, error) {
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
		Index: []string{"persons"},
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
					ID       string `json:"id"`
					FullName string `json:"full_name"`
				} `json:"_source"`
			} `json:"hits"`
		} `json:"hits"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, fmt.Errorf("response parsing error: %w", err)
	}

	persons := make([]*Person, 0, len(response.Hits.Hits))
	for _, hit := range response.Hits.Hits {
		filmworks, err := r.GetPersonFilmworkIDsAndRoles(ctx, hit.Source.ID)
		if err != nil {
			continue
		}
		persons = append(persons, &Person{
			ID:          hit.Source.ID,
			Name:        hit.Source.FullName,
			FilmworkIDs: filmworks["filmwork_ids"],
			Roles:       filmworks["roles"],
		})
	}

	return persons, nil
}

func (r *personRepository) Search(ctx context.Context, queryStr string, limit int) ([]*Person, error) {
	if limit <= 0 {
		limit = 10
	}

	query := map[string]interface{}{
		"query": map[string]interface{}{
			"multi_match": map[string]interface{}{
				"query":    queryStr,
				"fields":   []string{"full_name", "full_name.raw"},
				"operator": "and",
				"type":     "best_fields",
			},
		},
		"size": limit,
		"sort": []map[string]interface{}{
			{"_score": map[string]interface{}{"order": "desc"}},
		},
	}

	var buf bytes.Buffer
	if err := json.NewEncoder(&buf).Encode(query); err != nil {
		return nil, fmt.Errorf("request coding error: %w", err)
	}

	req := esapi.SearchRequest{
		Index: []string{"persons"},
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
					ID       string `json:"id"`
					FullName string `json:"full_name"`
				} `json:"_source"`
			} `json:"hits"`
		} `json:"hits"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, fmt.Errorf("response parsing error: %w", err)
	}

	persons := make([]*Person, 0, len(response.Hits.Hits))
	for _, hit := range response.Hits.Hits {
		filmworks, err := r.GetPersonFilmworkIDsAndRoles(ctx, hit.Source.ID)
		if err != nil {
			continue
		}
		persons = append(persons, &Person{
			ID:          hit.Source.ID,
			Name:        hit.Source.FullName,
			FilmworkIDs: filmworks["filmwork_ids"],
			Roles:       filmworks["roles"],
		})
	}

	return persons, nil
}

func (r *personRepository) Filmworks(ctx context.Context, personId string) ([]*PersonBaseFilmwork, error) {
	query := map[string]interface{}{
		"query": map[string]interface{}{
			"bool": map[string]interface{}{
				"should": []map[string]interface{}{
					{
						"nested": map[string]interface{}{
							"path": "actors",
							"query": map[string]interface{}{
								"match": map[string]interface{}{
									"actors.id": personId,
								},
							},
						},
					},
					{
						"nested": map[string]interface{}{
							"path": "directors",
							"query": map[string]interface{}{
								"match": map[string]interface{}{
									"directors.id": personId,
								},
							},
						},
					},
					{
						"nested": map[string]interface{}{
							"path": "writers",
							"query": map[string]interface{}{
								"match": map[string]interface{}{
									"writers.id": personId,
								},
							},
						},
					},
				},
			},
		},
		"size": 1000,
		"sort": map[string]interface{}{
			"rating": map[string]interface{}{
				"order": "desc",
			},
		},
		"_source": []string{"id", "title", "rating"},
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

	filmworks := make([]*PersonBaseFilmwork, 0, len(response.Hits.Hits))
	for _, hit := range response.Hits.Hits {
		filmworks = append(filmworks, &PersonBaseFilmwork{
			ID:     hit.Source.ID,
			Title:  hit.Source.Title,
			Rating: hit.Source.Rating,
		})
	}

	return filmworks, nil
}

func (r *personRepository) GetPersonFilmworkIDsAndRoles(ctx context.Context, personId string) (map[string][]string, error) {
	filmworks, err := r.Filmworks(ctx, personId)
	if err != nil {
		return nil, fmt.Errorf("failed to get filmworks: %w", err)
	}

	query := map[string]interface{}{
		"query": map[string]interface{}{
			"bool": map[string]interface{}{
				"should": []map[string]interface{}{
					{
						"nested": map[string]interface{}{
							"path": "actors",
							"query": map[string]interface{}{
								"match": map[string]interface{}{
									"actors.id": personId,
								},
							},
						},
					},
					{
						"nested": map[string]interface{}{
							"path": "directors",
							"query": map[string]interface{}{
								"match": map[string]interface{}{
									"directors.id": personId,
								},
							},
						},
					},
					{
						"nested": map[string]interface{}{
							"path": "writers",
							"query": map[string]interface{}{
								"match": map[string]interface{}{
									"writers.id": personId,
								},
							},
						},
					},
				},
			},
		},
		"size":    1000,
		"_source": []string{"id", "actors", "directors", "writers"},
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
					ID     string `json:"id"`
					Actors []struct {
						ID   string `json:"id"`
						Name string `json:"name"`
					} `json:"actors"`
					Directors []struct {
						ID   string `json:"id"`
						Name string `json:"name"`
					} `json:"directors"`
					Writers []struct {
						ID   string `json:"id"`
						Name string `json:"name"`
					} `json:"writers"`
				} `json:"_source"`
			} `json:"hits"`
		} `json:"hits"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
		return nil, fmt.Errorf("response parsing error: %w", err)
	}

	roles := make(map[string]struct{})
	filmworkIDs := make([]string, 0, len(filmworks))

	for _, hit := range response.Hits.Hits {
		filmworkIDs = append(filmworkIDs, hit.Source.ID)

		for _, actor := range hit.Source.Actors {
			if actor.ID == personId {
				roles["actor"] = struct{}{}
				break
			}
		}

		for _, director := range hit.Source.Directors {
			if director.ID == personId {
				roles["director"] = struct{}{}
				break
			}
		}

		for _, writer := range hit.Source.Writers {
			if writer.ID == personId {
				roles["writer"] = struct{}{}
				break
			}
		}
	}

	rolesSlice := make([]string, 0, len(roles))
	for role := range roles {
		rolesSlice = append(rolesSlice, role)
	}

	return map[string][]string{
		"roles":        rolesSlice,
		"filmwork_ids": filmworkIDs,
	}, nil
}
