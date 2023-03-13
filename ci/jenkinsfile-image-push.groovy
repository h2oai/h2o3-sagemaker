pipeline {
    agent {label "linux && docker"}
    environment {
        AWS_ECR = "524466471676.dkr.ecr.us-east-2.amazonaws.com/"
        AWS_ECR_GLM = "524466471676.dkr.ecr.us-east-2.amazonaws.com/h2o-sagemaker-glm"
        AWS_ECR_GBM = "524466471676.dkr.ecr.us-east-2.amazonaws.com/h2o-sagemaker-gbm"
        AWS_ECR_AUTOML = "524466471676.dkr.ecr.us-east-2.amazonaws.com/h2o-sagemaker-automl"
        AWS_ECR_DEEPLEARNING = "524466471676.dkr.ecr.us-east-2.amazonaws.com/h2o-sagemaker-deeplearning"
    }

    parameters {

        string(name: 'H2O-3_VERSION', defaultValue: 'h2o-3.40.0.2', description: 'Version of the H2O-3 product listed in http://h2o-release.s3.amazonaws.com/h2o/latest_stable')
    }


    stages {
        
        stage('1. Build Docker images ') {
            steps {
                echo "Building Docker image"
                sh "docker build --no-cache -t sagemaker-glm:${H2O-3_VERSION} -t sagemaker-glm:latest -f ${WORKSPACE}/glm/Dockerfile ."
                sh "docker build --no-cache -t sagemaker-gbm:${H2O-3_VERSION} -t sagemaker-gbm:latest -f ${WORKSPACE}/gbm/Dockerfile ."
                sh "docker build --no-cache -t sagemaker-automl:${H2O-3_VERSION} -t sagemaker-automl:latest -f ${WORKSPACE}/automl/Dockerfile ."                
                sh "docker build --no-cache -t sagemaker-deeplearning:${H2O-3_VERSION} -t sagemaker-deeplearning:latest -f ${WORKSPACE}/deep_learning/Dockerfile ."                
            }
        }


        stage('2. Push to ECR') {
            steps {
                echo "Push to ECR"
                script {
                    publishToECR()
                }
            }
        }
    }
}

def publishToECR() {
     withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: "awsArtifactsUploader"]]) {
     aws_ecr_pwd = sh(script: 'aws ecr get-login-password --region us-east-2', returnStdout: true).trim()
     sh """
       docker login -u AWS -p "${aws_ecr_pwd}" ${AWS_ECR}
     """

    sh "docker tag h2o-sagemaker-glm:latest ${AWS_ECR_GLM}latest"
    sh "docker tag h2o-sagemaker-glm:${H2O-3_VERSION} ${AWS_ECR_GLM}:${H2O-3_VERSION}"
    sh "docker push ${AWS_ECR_GLM}:latest"
    sh "docker push ${AWS_ECR_GLM}:${H2O-3_VERSION}"       

    sh "docker tag h2o-sagemaker-gbm:latest ${AWS_ECR_GBM}:latest"
    sh "docker tag h2o-sagemaker-gbm:${H2O-3_VERSION} ${AWS_ECR_GBM}:${H2O-3_VERSION}"
    sh "docker push ${AWS_ECR_GBM}latest"
    sh "docker push ${AWS_ECR_GBM}:${H2O-3_VERSION}"  

    sh "docker tag h2o-sagemaker-automl:latest ${AWS_ECR_AUTOML}:latest"
    sh "docker tag h2o-sagemaker-automl:${H2O-3_VERSION} ${AWS_ECR_AUTOML}:${H2O-3_VERSION}"
    sh "docker push ${AWS_ECR_AUTOML}:latest"
    sh "docker push ${AWS_ECR_AUTOML}:${H2O-3_VERSION}"  

    sh "docker tag h2o-sagemaker-deeplearning:latest ${AWS_ECR_DEEPLEARNING}:latest"
    sh "docker tag h2o-sagemaker-deeplearning:${H2O-3_VERSION} ${AWS_ECR_DEEPLEARNING}:${H2O-3_VERSION}"
    sh "docker push ${AWS_ECR_DEEPLEARNING}:latest"
    sh "docker push ${AWS_ECR_DEEPLEARNING}:${H2O-3_VERSION}"  

    }
  }
