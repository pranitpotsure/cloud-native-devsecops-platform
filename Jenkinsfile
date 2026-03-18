// =============================================================================
// Jenkinsfile.aws - Production Pipeline for AWS
// Jenkins on EC2 → builds → pushes to ECR → updates Git → ArgoCD deploys
//
// Flow:
//   GitHub Push → Jenkins → Trivy Scan → Build → Push ECR → Update Git Tag
//                                                                    ↓
//                                                          ArgoCD detects change
//                                                                    ↓
//                                                          Auto deploys to EKS
// =============================================================================

pipeline {
    agent any

    environment {
        AWS_REGION        = "ap-south-1"
        AWS_ACCOUNT_ID    = sh(script: "aws sts get-caller-identity --query Account --output text", returnStdout: true).trim()
        ECR_REGISTRY      = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        PROJECT_NAME      = "boutique"
        IMAGE_TAG         = "${BUILD_NUMBER}"
        GITHUB_REPO       = "https://github.com/pranitpotsure/cloud-native-devsecops-platform.git"
        GITHUB_CREDENTIALS = credentials('github-credentials')
    }

    stages {

        // ── Stage 1: Checkout ──────────────────────────────────────────────
        stage('Checkout') {
            steps {
                echo '📥 Pulling latest code...'
                checkout scm
                echo "✅ Build #${BUILD_NUMBER} started"
            }
        }

        // ── Stage 2: Security Scan ─────────────────────────────────────────
        stage('Security Scan - SAST') {
            steps {
                echo '🔍 Running Trivy filesystem scan...'
                sh '''
                    trivy fs . \
                        --severity HIGH,CRITICAL \
                        --exit-code 0 \
                        --format table \
                        --output trivy-fs-report.txt \
                        --scanners secret,vuln
                    cat trivy-fs-report.txt
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'trivy-fs-report.txt', allowEmptyArchive: true
                }
            }
        }

        // ── Stage 3: Login to ECR ──────────────────────────────────────────
        stage('ECR Login') {
            steps {
                echo '🔐 Logging into AWS ECR...'
                sh '''
                    aws ecr get-login-password --region ${AWS_REGION} | \
                    docker login --username AWS --password-stdin ${ECR_REGISTRY}
                    echo "✅ ECR login successful"
                '''
            }
        }

        // ── Stage 4: Build & Push Images ───────────────────────────────────
        stage('Build & Push to ECR') {
            steps {
                echo '🐳 Building and pushing images to ECR...'
                sh '''
                    cd src
                    SERVICES="adservice cartservice checkoutservice currencyservice emailservice frontend paymentservice productcatalogservice recommendationservice shippingservice shoppingassistantservice"

                    for SERVICE in $SERVICES; do
                        ECR_IMAGE="${ECR_REGISTRY}/${PROJECT_NAME}/${SERVICE}"

                        echo "🔨 Building ${SERVICE}..."
                        docker build \
                            -t ${ECR_IMAGE}:${IMAGE_TAG} \
                            -t ${ECR_IMAGE}:latest \
                            ./${SERVICE}/

                        echo "🔍 Scanning ${SERVICE} image..."
                        trivy image \
                            --severity HIGH,CRITICAL \
                            --exit-code 0 \
                            --format table \
                            ${ECR_IMAGE}:${IMAGE_TAG}

                        echo "📤 Pushing ${SERVICE} to ECR..."
                        docker push ${ECR_IMAGE}:${IMAGE_TAG}
                        docker push ${ECR_IMAGE}:latest

                        echo "✅ ${SERVICE} done"
                    done
                '''
            }
        }

        // ── Stage 5: Update K8s Manifests in Git ──────────────────────────
        // This is what triggers ArgoCD auto-sync!
        stage('Update Git Manifests') {
            steps {
                echo '📝 Updating image tags in Git - ArgoCD will detect this...'
                sh '''
                    SERVICES="adservice cartservice checkoutservice currencyservice emailservice frontend paymentservice productcatalogservice recommendationservice shippingservice shoppingassistantservice"

                    git config user.email "jenkins@boutique.com"
                    git config user.name "Jenkins CI"

                    for SERVICE in $SERVICES; do
                        ECR_IMAGE="${ECR_REGISTRY}/${PROJECT_NAME}/${SERVICE}"

                        # Update image tag in services.yaml
                        sed -i "s|${ECR_IMAGE}:.*|${ECR_IMAGE}:${IMAGE_TAG}|g" \
                            k8s/services/services.yaml

                        echo "✅ Updated ${SERVICE} → tag ${IMAGE_TAG}"
                    done

                    # Commit and push updated manifests
                    git add k8s/services/services.yaml
                    git commit -m "CI: Update image tags to build #${IMAGE_TAG} [skip ci]"
                    git push https://${GITHUB_CREDENTIALS_USR}:${GITHUB_CREDENTIALS_PSW}@github.com/pranitpotsure/cloud-native-devsecops-platform.git HEAD:main

                    echo "✅ Git updated - ArgoCD will now auto-deploy!"
                '''
            }
        }
    }

    post {
        success {
            echo """
            ✅ ================================================
            ✅  PIPELINE SUCCESS - Build #${BUILD_NUMBER}
            ✅  Images pushed to ECR with tag: ${BUILD_NUMBER}
            ✅  Git manifests updated
            ✅  ArgoCD is now syncing to EKS automatically
            ✅ ================================================
            """
        }
        failure {
            echo """
            ❌  PIPELINE FAILED - Build #${BUILD_NUMBER}
            ❌  Check logs above for details
            """
        }
        always {
            sh 'docker image prune -f || true'
        }
    }
}
