// =============================================================================
// Jenkinsfile - DevSecOps CI/CD Pipeline
// Online Boutique - Cloud Native Microservices
//
// Pipeline Stages:
//   1. Checkout        - Pull code from GitHub
//   2. Security Scan   - Trivy SAST scan (DevSecOps)
//   3. Build Images    - Docker build all 12 services
//   4. Image Scan      - Trivy CVE scan on each image (DevSecOps)
//   5. Push Images     - Push to DockerHub
//   6. Deploy          - Update K8s manifests with new image tags
// =============================================================================

pipeline {
    agent any

    environment {
        DOCKERHUB_USERNAME    = "pranitpotsure"   // ← CHANGE THIS
        GITHUB_REPO           = "https://github.com/pranitpotsure/cloud-native-devsecops-platform.git"  // ← CHANGE THIS
        IMAGE_TAG             = "${BUILD_NUMBER}"
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
    }

    stages {

        // ── Stage 1: Checkout ──────────────────────────────────────────────
        stage('Checkout') {
            steps {
                echo '📥 Pulling latest code from GitHub...'
                checkout scm
                echo "✅ Code checked out. Build #${BUILD_NUMBER}"
            }
        }

        // ── Stage 2: Security Scan (SAST) ──────────────────────────────────
        stage('Security Scan - SAST') {
            steps {
                echo '🔍 Running Trivy filesystem scan (DevSecOps)...'
                sh '''
                    # Install Trivy if not present
                    if ! command -v trivy &> /dev/null; then
                        curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
                    fi

                    # Scan source code for secrets and vulnerabilities
                    trivy fs . \
                        --severity HIGH,CRITICAL \
                        --exit-code 0 \
                        --format table \
                        --output trivy-fs-report.txt \
                        --scanners secret,vuln

                    echo "📄 Filesystem scan complete. Check trivy-fs-report.txt"
                    cat trivy-fs-report.txt
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'trivy-fs-report.txt', allowEmptyArchive: true
                }
            }
        }

        // ── Stage 3: Build Docker Images ───────────────────────────────────
        stage('Build Docker Images') {
            steps {
                echo '🐳 Building all 12 microservice images...'
                sh '''
                    cd src

                    # Build each service
                    SERVICES="adservice cartservice checkoutservice currencyservice emailservice frontend paymentservice productcatalogservice recommendationservice shippingservice shoppingassistantservice"

                    for SERVICE in $SERVICES; do
                        echo "🔨 Building $SERVICE..."
                        docker build \
                            -t ${DOCKERHUB_USERNAME}/${SERVICE}:${IMAGE_TAG} \
                            -t ${DOCKERHUB_USERNAME}/${SERVICE}:latest \
                            ./${SERVICE}/
                        echo "✅ $SERVICE built successfully"
                    done
                '''
            }
        }

        // ── Stage 4: Image Security Scan ───────────────────────────────────
        stage('Security Scan - Images') {
            steps {
                echo '🔒 Scanning Docker images for CVEs (DevSecOps)...'
                sh '''
                    SERVICES="adservice cartservice checkoutservice currencyservice emailservice frontend paymentservice productcatalogservice recommendationservice shippingservice shoppingassistantservice"

                    # Create report file
                    echo "=== IMAGE SCAN REPORT - Build #${IMAGE_TAG} ===" > trivy-image-report.txt
                    echo "Date: $(date)" >> trivy-image-report.txt
                    echo "" >> trivy-image-report.txt

                    for SERVICE in $SERVICES; do
                        echo "🔍 Scanning ${DOCKERHUB_USERNAME}/${SERVICE}:${IMAGE_TAG}..."
                        echo "--- $SERVICE ---" >> trivy-image-report.txt

                        trivy image \
                            --severity HIGH,CRITICAL \
                            --exit-code 0 \
                            --format table \
                            ${DOCKERHUB_USERNAME}/${SERVICE}:${IMAGE_TAG} >> trivy-image-report.txt 2>&1

                        echo "" >> trivy-image-report.txt
                    done

                    echo "📄 Image scan complete!"
                    cat trivy-image-report.txt
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'trivy-image-report.txt', allowEmptyArchive: true
                }
            }
        }

        // ── Stage 5: Push to DockerHub ─────────────────────────────────────
        stage('Push to DockerHub') {
            steps {
                echo '📤 Pushing images to DockerHub...'
                sh '''
                    # Login to DockerHub
                    echo "${DOCKERHUB_CREDENTIALS_PSW}" | docker login -u "${DOCKERHUB_CREDENTIALS_USR}" --password-stdin

                    SERVICES="adservice cartservice checkoutservice currencyservice emailservice frontend paymentservice productcatalogservice recommendationservice shippingservice shoppingassistantservice"

                    for SERVICE in $SERVICES; do
                        echo "📤 Pushing $SERVICE:${IMAGE_TAG}..."
                        docker push ${DOCKERHUB_USERNAME}/${SERVICE}:${IMAGE_TAG}
                        docker push ${DOCKERHUB_USERNAME}/${SERVICE}:latest
                        echo "✅ $SERVICE pushed"
                    done

                    docker logout
                    echo "✅ All images pushed to DockerHub"
                '''
            }
        }

        // ── Stage 6: Update K8s Manifests ─────────────────────────────────
        stage('Update K8s Manifests') {
            steps {
                echo '📝 Updating image tags in K8s manifests...'
                sh '''
                    SERVICES="adservice cartservice checkoutservice currencyservice emailservice frontend paymentservice productcatalogservice recommendationservice shippingservice shoppingassistantservice"

                    for SERVICE in $SERVICES; do
                        # Update image tag in services.yaml
                        sed -i "s|${DOCKERHUB_USERNAME}/${SERVICE}:.*|${DOCKERHUB_USERNAME}/${SERVICE}:${IMAGE_TAG}|g" \
                            k8s/services/services.yaml
                        echo "✅ Updated $SERVICE to tag ${IMAGE_TAG}"
                    done
                '''
            }
        }

        // ── Stage 7: Deploy (local Docker Compose for now) ────────────────
        stage('Deploy - Local') {
            steps {
                echo '🚀 Deploying updated services...'
                sh '''
                    cd src

                    # Pull latest images and restart changed services
                    docker compose pull
                    docker compose up -d --no-deps

                    echo "✅ Deployment complete!"
                    docker compose ps
                '''
            }
        }
    }

    // ── Post Pipeline Actions ──────────────────────────────────────────────
    post {
        success {
            echo """
            ✅ ================================================
            ✅  PIPELINE SUCCESS - Build #${BUILD_NUMBER}
            ✅  All 11 services built, scanned & pushed
            ✅  Images tagged: ${DOCKERHUB_USERNAME}/*:${BUILD_NUMBER}
            ✅ ================================================
            """
        }
        failure {
            echo """
            ❌ ================================================
            ❌  PIPELINE FAILED - Build #${BUILD_NUMBER}
            ❌  Check logs above for details
            ❌ ================================================
            """
        }
        always {
            // Clean up dangling images to save disk space
            sh 'docker image prune -f || true'
            echo '🧹 Cleanup complete'
        }
    }
}
