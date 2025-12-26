package database

import (
	"async-api/internal/config"
	"fmt"
	"github.com/elastic/go-elasticsearch/v9"
	"log"
)

func SetupElasticClient(cfg config.Config) (*elasticsearch.Client, error) {
	esCfg := elasticsearch.Config{
		Addresses: []string{"http://" + cfg.Elastic.Host + ":" + cfg.Elastic.Port},
		Username:  cfg.Elastic.User,
		Password:  cfg.Elastic.Password,
	}

	es, err := elasticsearch.NewClient(esCfg)
	if err != nil {
		return nil, fmt.Errorf("Error creating client: %s", err)
	}

	log.Println(es.Info())

	return es, nil
}
