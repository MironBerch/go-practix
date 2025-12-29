package filmwork

import "async-api/internal/domain/person"

type BaseFilmwork struct {
	ID     string  `json:"uuid"`
	Title  string  `json:"title"`
	Rating float32 `json:"rating"`
}

type Filmwork struct {
	ID          string              `json:"id"`
	Title       string              `json:"title"`
	Rating      float32             `json:"rating"`
	Description string              `json:"description"`
	ReleaseDate string              `json:"release_date"`
	Type        string              `json:"type"`
	Genres      []string            `json:"genres"`
	Actors      []person.BasePerson `json:"actors"`
	Writers     []person.BasePerson `json:"writers"`
	Directors   []person.BasePerson `json:"directors"`
}
