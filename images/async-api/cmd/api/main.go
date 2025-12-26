package main

import (
	"async-api/internal/config"
	"async-api/internal/domain/filmwork"
	"async-api/internal/domain/genre"
	"async-api/internal/domain/person"
	"async-api/pkg/database"
	"encoding/json"
	"log"
	"net/http"

	"github.com/gorilla/handlers"
	"github.com/gorilla/mux"
)

type healthzResponse struct {
	Message string `json:"message"`
}

func healthzHandler(w http.ResponseWriter, r *http.Request) {
	response := healthzResponse{
		Message: "ok",
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(200)

	if err := json.NewEncoder(w).Encode(response); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
	}
}

func main() {
	cfg, err := config.Load()
	if err != nil {
		log.Fatal("Failed to load config:", err)
	}

	esClient, err := database.SetupElasticClient(*cfg)
	if err != nil {
		log.Fatal("Failed to setup Elasticsearch client:", err)
	}

	genreRepo := genre.NewGenreRepository(esClient)
	genreService := genre.NewGenreService(genreRepo)
	genreHandler := genre.NewGenreHandler(genreService)

	personRepo := person.NewPersonRepository(esClient)
	personService := person.NewPersonService(personRepo)
	personHandler := person.NewPersonHandler(personService)

	filmworkRepo := filmwork.NewFilmworkRepository(esClient)
	filmworkService := filmwork.NewFilmworkService(filmworkRepo)
	filmworkHandler := filmwork.NewFilmworkHandler(filmworkService)

	router := mux.NewRouter()

	router.HandleFunc("/healthz", healthzHandler)
	genreHandler.RegisterRoutes(router)
	personHandler.RegisterRoutes(router)
	filmworkHandler.RegisterRoutes(router)

	corsHandler := handlers.CORS(
		handlers.AllowedOrigins(cfg.HTTP.CORS.AllowOrigins),
		handlers.AllowedMethods(cfg.HTTP.CORS.AllowMethods),
		handlers.AllowedHeaders(cfg.HTTP.CORS.AllowHeaders),
	)

	log.Fatal(http.ListenAndServe(":"+cfg.HTTP.Port, corsHandler(router)))
}
