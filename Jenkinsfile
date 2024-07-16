pipeline {
    agent any  // Run on any available agent

    stages {
        stage('Checkout') {
            steps {
                checkout([
                    $class: 'GitSCM', 
                    branches: [[name: '*/master']],
                    userRemoteConfigs: [[
                        url: 'https://github.com/BS-PMC-2024/BS-PMC-2024-Team2.git', 
                        credentialsId: 'jenkinstoken'
                    ]]
                ])
            }
        }
        
        stage('Build and Test') {
            agent {
                docker {
                    image 'python:3.8-alpine'
                    args '-u root:root'  // Running as root user
                }
            }
            steps {
                sh 'pip install flask pymongo pytest'
                sh 'mkdir -p test-reports'
                sh 'python -m unittest discover -s tests -p "*.py" --verbose --junit-xml=test-reports/results.xml'
            }
            post {
                always {
                    junit 'test-reports/results.xml'
                }
            }
 }
}
}

