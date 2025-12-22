package main

import (
	"async-api/internal/config"
	"encoding/json"
	"log"
	"net/http"
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
    log.Fatal(err)
  }

  http.HandleFunc("/healthz", healthzHandler)

  log.Fatal(http.ListenAndServe(":" + cfg.HTTP.Port, nil))
}
