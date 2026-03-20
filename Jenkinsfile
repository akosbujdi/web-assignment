pipeline {
    agent any

    stages {

        stage('Clone Repo') {
            steps {
                echo 'Code pulled from GitHub successfully'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t web-assignment ./web-assignment'
            }
        }

        stage('Run Container') {
            steps {
                withCredentials([string(credentialsId: 'MONGO_URI', variable: 'MONGO_URI')]) {
                    sh 'docker rm -f web-assignment-container || true'
                    sh 'docker run -d -p 8000:8000 --name web-assignment-container -e MONGO_URI=$MONGO_URI web-assignment'
                    sh 'sleep 5'
                }
            }
        }

        stage('Run Tests') {
            steps {
                sh 'cd web-assignment && newman run tests/postman_collection.json'
            }
        }

        stage('Generate README') {
            steps {
                sh '''
                cat > README.txt << EOF
Web Services Assignment 1 - API Endpoints
==========================================

GET  /getSingleProduct?id=1          - Returns a single product by ID
GET  /getAll                         - Returns all products
POST /addNew                         - Adds a new product (JSON body required)
DELETE /deleteOne?id=1               - Deletes a product by ID
GET  /startsWith?letter=s            - Returns all products starting with a letter
GET  /paginate?start_id=1&end_id=50  - Returns up to 10 products in ID range
GET  /convert?id=1                   - Returns product price converted to EUR

FastAPI Interactive Docs: http://localhost:8000/docs
Full FastAPI documentation: https://fastapi.tiangolo.com/
EOF
                '''
            }
        }

        stage('Package') {
            steps {
                sh 'zip -r complete-$(date +%Y%m%d-%H%M%S).zip web-assignment/ README.txt'
            }
        }

        stage('Cleanup') {
            steps {
                sh 'docker stop web-assignment-container'
                sh 'docker rm web-assignment-container'
            }
        }
    }
}