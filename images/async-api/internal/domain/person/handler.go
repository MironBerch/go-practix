package person

import (
	"net/http"
	"strconv"
	"strings"

	"async-api/internal/http"
	"github.com/gorilla/mux"
)

type PersonHandler struct {
	service PersonService
}

func NewPersonHandler(service PersonService) *PersonHandler {
	return &PersonHandler{service: service}
}

func (h *PersonHandler) RegisterRoutes(router *mux.Router) {
	router.HandleFunc("/persons/search", h.Search).Methods("GET")
	router.HandleFunc("/persons", h.GetAll).Methods("GET")
	router.HandleFunc("/persons/{id}", h.GetByID).Methods("GET")
	router.HandleFunc("/persons/{id}/filmworks", h.PersonFilmworks).Methods("GET")
}

func (h *PersonHandler) GetByID(w http.ResponseWriter, r *http.Request) {
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

func (h *PersonHandler) Search(w http.ResponseWriter, r *http.Request) {
	query := r.URL.Query().Get("q")
	persons, err := h.service.Search(r.Context(), query, 1000)
	if err != nil {
		response.SendErrorResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}
	response.SendSuccessResponse(w, persons, http.StatusOK)
}

func (h *PersonHandler) GetAll(w http.ResponseWriter, r *http.Request) {
	pageNumberStr := r.URL.Query().Get("page_number")
	pageSizeStr := r.URL.Query().Get("page_size")
	pageNumber := 1
	pageSize := 100
	if pageNumberStr != "" {
		if p, err := strconv.Atoi(pageNumberStr); err == nil && p > 0 {
			pageNumber = p
		} else {
			response.SendErrorResponse(w, "Неверный формат page_number", http.StatusBadRequest)
			return
		}
	}
	if pageSizeStr != "" {
		if s, err := strconv.Atoi(pageSizeStr); err == nil && s > 0 {
			if s > 100 {
				pageSize = 100
			} else {
				pageSize = s
			}
		} else {
			response.SendErrorResponse(w, "Неверный формат page_size", http.StatusBadRequest)
			return
		}
	}
	persons, err := h.service.GetAll(r.Context(), pageNumber, pageSize)
	if err != nil {
		response.SendErrorResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}
	response.SendSuccessResponse(w, persons, http.StatusOK)
}

func (h *PersonHandler) PersonFilmworks(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	id := vars["id"]
	filmworks, err := h.service.GetPersonFilmworks(r.Context(), id)
	if err != nil {
		response.SendErrorResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}
	response.SendSuccessResponse(w, filmworks, http.StatusOK)
}
