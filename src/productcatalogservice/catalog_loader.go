// productcatalogservice/catalog_loader.go - Cloud-Agnostic Refactored Version
//
// CHANGES:
//   - Removed cloud.google.com/go/alloydbconn (GCP AlloyDB)
//   - Removed cloud.google.com/go/secretmanager (GCP Secret Manager)
//   - Removed jackc/pgx/v5 (was AlloyDB PostgreSQL driver)
//   - Removed loadCatalogFromAlloyDB() and getSecretPayload() entirely
//   - loadCatalog() now always loads from local products.json file
//   - For AWS DB-backed catalog: see commented stub at bottom of file

package main

import (
	"bytes"
	"os"

	pb "github.com/GoogleCloudPlatform/microservices-demo/src/productcatalogservice/genproto"
	"github.com/golang/protobuf/jsonpb"
)

// loadCatalog loads the product catalog from local products.json.
// Works in any environment - no GCP dependencies.
// For AWS: to use RDS/Aurora, see commented stub at bottom of file.
func loadCatalog(catalog *pb.ListProductsResponse) error {
	catalogMutex.Lock()
	defer catalogMutex.Unlock()
	return loadCatalogFromLocalFile(catalog)
}

func loadCatalogFromLocalFile(catalog *pb.ListProductsResponse) error {
	log.Info("loading catalog from local products.json file...")

	catalogJSON, err := os.ReadFile("products.json")
	if err != nil {
		log.Warnf("failed to open product catalog json file: %v", err)
		return err
	}

	if err := jsonpb.Unmarshal(bytes.NewReader(catalogJSON), catalog); err != nil {
		log.Warnf("failed to parse the catalog JSON: %v", err)
		return err
	}

	log.Info("successfully parsed product catalog json")
	return nil
}

// ---------------------------------------------------------------------------
// OPTIONAL: AWS RDS / Aurora PostgreSQL catalog loader
// To use a database-backed catalog on AWS, uncomment this and add
// github.com/jackc/pgx/v5 to go.mod, then call loadCatalogFromPostgres()
// from loadCatalog() above.
//
// Required env vars: DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, DB_TABLE
//
// func loadCatalogFromPostgres(catalog *pb.ListProductsResponse) error {
// 	dsn := fmt.Sprintf(
// 		"postgres://%s:%s@%s:%s/%s?sslmode=require",
// 		os.Getenv("DB_USER"), os.Getenv("DB_PASSWORD"),
// 		os.Getenv("DB_HOST"), os.Getenv("DB_PORT"), os.Getenv("DB_NAME"),
// 	)
// 	pool, err := pgxpool.New(context.Background(), dsn)
// 	if err != nil { return err }
// 	defer pool.Close()
// 	rows, err := pool.Query(context.Background(),
// 		"SELECT id, name, description, picture, price_usd_currency_code, price_usd_units, price_usd_nanos, categories FROM "+os.Getenv("DB_TABLE"))
// 	if err != nil { return err }
// 	defer rows.Close()
// 	// ... scan rows into catalog.Products
// 	return nil
// }
// ---------------------------------------------------------------------------
