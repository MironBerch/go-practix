package config

import (
	"fmt"
	"os"
)

type Config struct {
	App     AppConfig
	HTTP    HTTPConfig
	Elastic ElasticConfig
	Redis   RedisConfig
}

type AppConfig struct {
	Env string
}

type HTTPConfig struct {
	Port string
	CORS CORSConfig
}

type CORSConfig struct {
	AllowOrigins []string
	AllowMethods []string
	AllowHeaders []string
}

type RedisConfig struct {
	Host string
	Port string
	DB   string
}

type ElasticConfig struct {
	Host     string
	Port     string
	User     string
	Password string
}

func Load() (*Config, error) {
	cfg := &Config{
		App: AppConfig{
			Env: getEnv("APP_ENV"),
		},
		HTTP: HTTPConfig{
			Port: getEnv("HTTP_PORT"),
			CORS: CORSConfig{
				AllowOrigins: []string{"*"},
				AllowMethods: []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
				AllowHeaders: []string{"Content-Type", "Authorization"},
			},
		},
		Redis: RedisConfig{
			Host: getEnv("REDIS_HOST"),
			Port: getEnv("REDIS_PORT"),
			DB:   getEnv("REDIS_DB"),
		},
		Elastic: ElasticConfig{
			Host:     getEnv("ELASTIC_HOST"),
			Port:     getEnv("ELASTIC_PORT"),
			User:     getEnv("ELASTIC_USER"),
			Password: getEnv("ELASTIC_PASSWORD"),
		},
	}

	if err := cfg.Validate(); err != nil {
		return nil, err
	}

	return cfg, nil
}

func (c *Config) Validate() error {
	if c.App.Env == "" {
		return fmt.Errorf("ENV is required")
	}
	if c.HTTP.Port == "" {
		return fmt.Errorf("HTTP_PORT is required")
	}
	if c.Elastic.Host == "" {
		return fmt.Errorf("ELASTIC_HOST is required")
	}
	if c.Elastic.Port == "" {
		return fmt.Errorf("ELASTIC_PORT is required")
	}
	if c.Elastic.User == "" {
		return fmt.Errorf("ELASTIC_USER is required")
	}
	if c.Redis.Host == "" {
		return fmt.Errorf("REDIS_HOST is required")
	}
	if c.Redis.Port == "" {
		return fmt.Errorf("REDIS_PORT is required")
	}
	if c.Redis.DB == "" {
		return fmt.Errorf("REDIS_DB is required")
	}
	return nil
}

func getEnv(key string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return ""
}
