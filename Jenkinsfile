stage('Build') {
  parallel (
    "linux64": {
      node("lin64") {
        checkout scm
        sh './scripts/install_build_dependencies.sh'
        sh './scripts/build.sh'
      }
    }
  )
}
