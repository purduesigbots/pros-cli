stage('Build') {
  parallel (
    "linux64": {
      node("lin64") {
        checkout scm
        sh './scripts/install_build_dependencies.sh'
        sh 'vex -mr jenkins ./scripts/build.sh'
        archiveArtifacts artifacts: 'out/*', onlyIfSuccessful: true
      }
    },
    "linux86": {
      node("lin86") {
        checkout scm
        sh './scripts/install_build_dependencies.sh'
        sh 'vex -mr jenkins ./scripts/build.sh'
        archiveArtifacts artifacts: 'out/*', onlyIfSuccessful: true
      }
    },
    "windows64": {
      node("win64") {
        checkout scm
        bat 'powershell -file .\\scripts\\install_build_dependencies.ps1'
        bat '.\\scripts\\build.bat'
        archiveArtifacts artifacts: 'out/*', onlyIfSuccessful: true
      }
    },
    "windows86": {
      node("win86") {
        checkout scm
        bat 'powershell -file .\\scripts\\install_build_dependencies.ps1'
        bat '.\\scripts\\build.bat'
        archiveArtifacts artifacts: 'out/*', onlyIfSuccessful: true
      }
    }
  )
}