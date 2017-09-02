stage('Build') {
  parallel (
    "linux64": {
      node("lin64") {
        checkout scm
        sh './scripts/install_build_dependencies.sh'
        sh './scripts/build.sh'
        archiveArtifacts allowEmptyArchive: true, artifacts: 'out/*', onlyIfSuccessful: true
      }
    },
    "linux86": {
      node("lin86") {
        checkout scm
        sh './scripts/install_build_dependencies.sh'
        sh './scripts/build.sh'
        archiveArtifacts allowEmptyArchive: true, artifacts: 'out/*', onlyIfSuccessful: true
      }
    },
    "windows64": {
      node("win64") {
        checkout scm
        bat 'powershell -file .\\scripts\\install_build_dependencies.ps1'
        bat 'powershell -file .\\scripts\\build.ps1'
        archiveArtifacts allowEmptyArchive: true, artifacts: 'out/*', onlyIfSuccessful: true
      }
    },
    "windows86": {
      node("win86") {
        checkout scm
        bat 'powershell -file .\\scripts\\install_build_dependencies.ps1'
        bat 'powershell -file .\\scripts\\build.ps1'
        archiveArtifacts allowEmptyArchive: true, artifacts: 'out/*', onlyIfSuccessful: true
      }
    }
  )
}