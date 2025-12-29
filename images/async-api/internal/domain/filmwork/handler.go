package filmwork

import (
	"net/http"
	"strconv"
	"strings"

	"github.com/gorilla/mux"

	"async-api/internal/http"
)

type FilmworkHandler struct {
	service FilmworkService
}

func NewFilmworkHandler(service FilmworkService) *FilmworkHandler {
	return &FilmworkHandler{service: service}
}

func (h *FilmworkHandler) RegisterRoutes(router *mux.Router) {
	router.HandleFunc("/filmworks/search", h.Search).Methods("GET")
	router.HandleFunc("/filmworks", h.GetAll).Methods("GET")
	router.HandleFunc("/filmworks/{id}", h.GetByID).Methods("GET")
}

func (h *FilmworkHandler) GetByID(w http.ResponseWriter, r *http.Request) {
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

func (h *FilmworkHandler) Search(w http.ResponseWriter, r *http.Request) {
	query := r.URL.Query().Get("q")
	filmworks, err := h.service.Search(r.Context(), query, 1000)
	if err != nil {
		response.SendErrorResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}
	response.SendSuccessResponse(w, filmworks, http.StatusOK)
}

func (h *FilmworkHandler) GetAll(w http.ResponseWriter, r *http.Request) {
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
	filmworks, err := h.service.GetAll(r.Context(), pageNumber, pageSize)
	if err != nil {
		response.SendErrorResponse(w, err.Error(), http.StatusInternalServerError)
		return
	}
	response.SendSuccessResponse(w, filmworks, http.StatusOK)
}
