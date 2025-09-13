package main

import (
	"database/sql"
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"time"

	_ "github.com/lib/pq"
)

type Config struct {
	DBHost     string
	DBPort     string
	DBName     string
	DBUser     string
	DBPassword string
	ExportPath string
}

func main() {
	config := Config{
		DBHost:     getEnv("DB_HOST", "localhost"),
		DBPort:     getEnv("DB_PORT", "5432"),
		DBName:     getEnv("DB_NAME", "transport_db"),
		DBUser:     getEnv("DB_USER", "postgres"),
		DBPassword: getEnv("DB_PASSWORD", ""),
		ExportPath: getEnv("EXPORT_PATH", "/data/exports"),
	}

	if err := exportShipments(config); err != nil {
		log.Fatalf("Export failed: %v", err)
	}

	log.Println("Export completed successfully")
}

func exportShipments(config Config) error {
	connStr := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		config.DBHost, config.DBPort, config.DBUser, config.DBPassword, config.DBName)

	db, err := sql.Open("postgres", connStr)
	if err != nil {
		return fmt.Errorf("failed to connect to database: %v", err)
	}
	defer db.Close()

	if err := db.Ping(); err != nil {
		return fmt.Errorf("failed to ping database: %v", err)
	}

	query := `
		SELECT id, client_id, driver_id, vehicle_id, origin, destination, 
			   status, weight_kg, volume_m3, created_at, updated_at
		FROM shipments 
		WHERE DATE(created_at) = CURRENT_DATE - INTERVAL '1 day'
	`

	rows, err := db.Query(query)
	if err != nil {
		return fmt.Errorf("failed to query shipments: %v", err)
	}
	defer rows.Close()

	timestamp := time.Now().Format("20060102_150405")
	filename := fmt.Sprintf("%s/shipments_export_%s.csv", config.ExportPath, timestamp)

	file, err := os.Create(filename)
	if err != nil {
		return fmt.Errorf("failed to create file: %v", err)
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	headers := []string{
		"id", "client_id", "driver_id", "vehicle_id", "origin", "destination",
		"status", "weight_kg", "volume_m3", "created_at", "updated_at",
	}
	if err := writer.Write(headers); err != nil {
		return fmt.Errorf("failed to write headers: %v", err)
	}

	var count int
	for rows.Next() {
		var (
			id, clientID, driverID, vehicleID int
			origin, destination, status       string
			weightKg, volumeM3                float64
			createdAt, updatedAt              time.Time
		)

		if err := rows.Scan(
			&id, &clientID, &driverID, &vehicleID,
			&origin, &destination, &status,
			&weightKg, &volumeM3, &createdAt, &updatedAt,
		); err != nil {
			return fmt.Errorf("failed to scan row: %v", err)
		}

		record := []string{
			fmt.Sprintf("%d", id),
			fmt.Sprintf("%d", clientID),
			fmt.Sprintf("%d", driverID),
			fmt.Sprintf("%d", vehicleID),
			origin,
			destination,
			status,
			fmt.Sprintf("%.2f", weightKg),
			fmt.Sprintf("%.2f", volumeM3),
			createdAt.Format(time.RFC3339),
			updatedAt.Format(time.RFC3339),
		}

		if err := writer.Write(record); err != nil {
			return fmt.Errorf("failed to write record: %v", err)
		}

		count++
	}

	if err := rows.Err(); err != nil {
		return fmt.Errorf("error iterating rows: %v", err)
	}

	log.Printf("Exported %d shipment records to %s", count, filename)
	return nil
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}
