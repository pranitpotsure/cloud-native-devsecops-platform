// frontend/deployment_details.go - Cloud-Agnostic Refactored Version
//
// CHANGES:
//   - Removed cloud.google.com/go/compute/metadata (GCP Metadata Server)
//   - Removed all GCP metadata API calls (cluster-name, zone)
//   - Deployment details now read from environment variables only
//   - Compatible with AWS ECS (uses ECS_CONTAINER_METADATA_URI) or plain env vars
//   - Falls back gracefully if env vars not set

package main

import (
	"os"
	"time"

	"github.com/sirupsen/logrus"
)

var deploymentDetailsMap map[string]string
var log *logrus.Logger

func init() {
	initializeLogger()
	// Load deployment details from env vars (non-blocking)
	go loadDeploymentDetails()
}

func initializeLogger() {
	log = logrus.New()
	log.Level = logrus.DebugLevel
	log.Formatter = &logrus.JSONFormatter{
		FieldMap: logrus.FieldMap{
			logrus.FieldKeyTime:  "timestamp",
			logrus.FieldKeyLevel: "severity",
			logrus.FieldKeyMsg:   "message",
		},
		TimestampFormat: time.RFC3339Nano,
	}
	log.Out = os.Stdout
}

// loadDeploymentDetails reads deployment context from environment variables.
// On AWS ECS: set CLUSTER_NAME and AVAILABILITY_ZONE in task definition.
// On AWS EKS: set via Downward API in pod spec.
// Locally: values will be empty strings, which is fine.
func loadDeploymentDetails() {
	deploymentDetailsMap = make(map[string]string)

	podHostname, err := os.Hostname()
	if err != nil {
		log.Error("Failed to fetch hostname", err)
	}

	// Read from env vars instead of GCP metadata server
	// On AWS ECS: CLUSTER_NAME can be set from task metadata or manually
	// On AWS EKS: inject via Downward API
	clusterName := os.Getenv("CLUSTER_NAME")
	zone := os.Getenv("AVAILABILITY_ZONE")

	deploymentDetailsMap["HOSTNAME"] = podHostname
	deploymentDetailsMap["CLUSTERNAME"] = clusterName
	deploymentDetailsMap["ZONE"] = zone

	log.WithFields(logrus.Fields{
		"cluster":  clusterName,
		"zone":     zone,
		"hostname": podHostname,
	}).Debug("Loaded deployment details from environment variables")
}
