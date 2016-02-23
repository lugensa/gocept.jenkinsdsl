
class PytestBuilder extends AbstractBuilder {

    def additional_commands
    def junit_filename
    def coverage_filename
    def htmlcov_path

    // Run tests using py.test and publish coverage results.
    public void create_config(job, config) {
        super.create_config(job, config, this.additional_commands)

        job.with {

            publishers {
                archiveJunit(this.junit_filename) {
                    retainLongStdout()
                    testDataPublishers {
                        publishTestAttachments()
                    }
                }

                if (this.coverage_filename) {
                    cobertura(this.coverage_filename) {
                        onlyStable true
                        sourceEncoding 'UTF_8'
                    }
                }
            }

            if (this.htmlcov_path) {
                configure {
                    project -> project / 'publishers' / 'jenkins.plugins.shiningpanda.publishers.CoveragePublisher' {
                        htmlDir this.htmlcov_path
                    }
                }
            }
        }
    }
}
