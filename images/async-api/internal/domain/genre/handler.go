package genre

import (
	"net/http"
	"strings"

	"async-api/internal/http"
	"github.com/gorilla/mux"
)

type GenreHandler struct {
	service GenreService
}

func NewGenreHandler(service GenreService) *GenreHandler {
	return &GenreHandler{service: service}
}

func (h *GenreHandler) RegisterRoutes(router *mux.Router) {
	router.HandleFunc("/genres", h.GetAll).Methods("GET")
	router.HandleFunc("/genres/{id}", h.GetByID).Methods("GET")
}

func (h *GenreHandler) GetByID(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id := vars["id"]
	g, err := h.service.GetByID(r.Context(), id)
	if err != nil {
		statusCode := http.StatusInternalServerError
		if strings.Contains(err.Error(), "not found") {
			statusCode = http.StatusNotFound
		}
		response.SendErrorResponse(w, err.Error(), statusCode)
		return
	}
	response.SendSuccessResponse(w, g, http.StatusOK)
}

func (h *GenreHandler) GetAll(w http.ResponseWriter, r *http.Request) {
	genres, err := h.service.GetAll(r.Context())
	if err != nil {
		response.SendErrorResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}
	response.SendSuccessResponse(w, genres, http.StatusOK)
}
