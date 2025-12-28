package person

type EsBasePerson struct {
	ID   string `json:"id"`
	Name string `json:"full_name"`
}

type BasePerson struct {
	ID   string `json:"id"`
	Name string `json:"name"`
}

type Person struct {
	ID          string   `json:"id"`
	Name        string   `json:"name"`
	Roles       []string `json:"roles"`
	FilmworkIDs []string `json:"filmwork_ids"`
}

type PersonBaseFilmwork struct {
	ID     string  `json:"uuid"`
	Title  string  `json:"title"`
	Rating float32 `json:"rating"`
}
