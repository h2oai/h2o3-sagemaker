pipeline {
    agent {label "mr-0x16"}
    environment {
        AWS_ECR = "524466471676.dkr.ecr.us-east-2.amazonaws.com/"
        AWS_ECR_GLM = "524466471676.dkr.ecr.us-east-2.amazonaws.com/h2o-sagemaker-glm"
        AWS_ECR_GBM = "524466471676.dkr.ecr.us-east-2.amazonaws.com/h2o-sagemaker-gbm"
        AWS_ECR_AUTOML = "524466471676.dkr.ecr.us-east-2.amazonaws.com/h2o-sagemaker-automl"
        AWS_ECR_DEEPLEARNING = "524466471676.dkr.ecr.us-east-2.amazonaws.com/h2o-sagemaker-deeplearning"
    }

    parameters {

        string(name: 'H2O_3_VERSION', defaultValue: 'h2o-3.40.0.2', description: 'Version of the H2O-3 product listed in http://h2o-release.s3.amazonaws.com/h2o/latest_stable')
        booleanParam(name: 'PUSH_H2O_3_GLM', defaultValue: false, description: 'Build & Push H2O-3 Sagemaker GLM Algorithm')
        booleanParam(name: 'PUSH_H2O_3_GBM', defaultValue: false, description: 'Build & Push H2O-3 Sagemaker GBM Algorithm')
        booleanParam(name: 'PUSH_H2O_3_AUTOML', defaultValue: false, description: 'Build & Push H2O-3 Sagemaker AutoML Algorithm')
        booleanParam(name: 'PUSH_H2O_3_DEEPLEARNING', defaultValue: false, description: 'Build & Push H2O-3 Sagemaker Deeplearning Algorithm')
    }


    stages {
        stage('1. Build & Push H2O-3 Sagemaker GLM') {
            when {
                environment(name: "PUSH_H2O_3_GLM", value: "true")
            }
            steps {
                echo "Building Docker image for H2O-3 Sagemaker GLM"
                sh "docker build --no-cache -t h2o-sagemaker-glm:${H2O_3_VERSION} -t h2o-sagemaker-glm:latest -f ${WORKSPACE}/glm/Dockerfile.new ."     
                echo "Push to ECR H2O-3 Sagemaker GLM"
                script {
                    publishToECR("h2o-sagemaker-glm")
                }
            }
            
        }
        stage('2. Build & Push H2O-3 Sagemaker GBM') {
            when {
                environment(name: "PUSH_H2O_3_GBM", value: "true")
            }
            steps {
                echo "Building Docker image for H2O-3 Sagemaker GBM"
                sh "docker build --no-cache -t h2o-sagemaker-gbm:${H2O_3_VERSION} -t h2o-sagemaker-gbm:latest -f ${WORKSPACE}/gbm/Dockerfile.awslinux ."     
                echo "Push to ECR H2O-3 Sagemaker GBM"
                script {
                    publishToECR("h2o-sagemaker-gbm")
                }
            }
            
        }       
        // stage('1. Build Docker images ') {
        //     steps {
        //         echo "Building Docker image"
        //         sh "docker build --no-cache -t sagemaker-glm:${H2O_3_VERSION} -t sagemaker-glm:latest -f ${WORKSPACE}/glm/Dockerfile ."
        //         sh "docker build --no-cache -t sagemaker-gbm:${H2O_3_VERSION} -t sagemaker-gbm:latest -f ${WORKSPACE}/gbm/Dockerfile ."
        //         sh "docker build --no-cache -t sagemaker-automl:${H2O_3_VERSION} -t sagemaker-automl:latest -f ${WORKSPACE}/automl/Dockerfile ."                
        //         sh "docker build --no-cache -t sagemaker-deeplearning:${H2O_3_VERSION} -t sagemaker-deeplearning:latest -f ${WORKSPACE}/deep_learning/Dockerfile ."                
        //     }
        // }

        // stage('2. Push to ECR') {
        //     steps {
        //         echo "Push to ECR"
        //         script {
        //             publishToECR()
        //         }
        //     }
        // }
    }
}

def publishToECR(SAGEMAKER_TYPE) {
     withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: "awsArtifactsUploader"]]) {
     aws_ecr_pwd = sh(script: 'aws ecr get-login-password --region us-east-2', returnStdout: true).trim()
     sh """
       docker login -u AWS -p "${aws_ecr_pwd}" ${AWS_ECR}
     """

    sh "docker tag ${SAGEMAKER_TYPE}:latest ${AWS_ECR_GLM}latest"
    sh "docker tag ${SAGEMAKER_TYPE}:${H2O_3_VERSION} ${AWS_ECR_GLM}:${H2O_3_VERSION}"
    sh "docker push ${AWS_ECR_GLM}:latest"
    sh "docker push ${AWS_ECR_GLM}:${H2O_3_VERSION}"       

    // sh "docker tag h2o-sagemaker-gbm:latest ${AWS_ECR_GBM}:latest"
    // sh "docker tag h2o-sagemaker-gbm:${H2O_3_VERSION} ${AWS_ECR_GBM}:${H2O_3_VERSION}"
    // sh "docker push ${AWS_ECR_GBM}latest"
    // sh "docker push ${AWS_ECR_GBM}:${H2O_3_VERSION}"  

    // sh "docker tag h2o-sagemaker-automl:latest ${AWS_ECR_AUTOML}:latest"
    // sh "docker tag h2o-sagemaker-automl:${H2O_3_VERSION} ${AWS_ECR_AUTOML}:${H2O_3_VERSION}"
    // sh "docker push ${AWS_ECR_AUTOML}:latest"
    // sh "docker push ${AWS_ECR_AUTOML}:${H2O_3_VERSION}"  

    // sh "docker tag h2o-sagemaker-deeplearning:latest ${AWS_ECR_DEEPLEARNING}:latest"
    // sh "docker tag h2o-sagemaker-deeplearning:${H2O_3_VERSION} ${AWS_ECR_DEEPLEARNING}:${H2O_3_VERSION}"
    // sh "docker push ${AWS_ECR_DEEPLEARNING}:latest"
    // sh "docker push ${AWS_ECR_DEEPLEARNING}:${H2O_3_VERSION}"  

    }
  }
