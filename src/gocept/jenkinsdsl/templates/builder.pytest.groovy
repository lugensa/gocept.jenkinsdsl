
class PytestBuilder extends AbstractBuilder {

    def additional_commands
    def junit_filename
    def coverage_filename
    def htmlcov_path
    def pep8_filename

    // Run tests using py.test and publish coverage results.
    public void create_config(job, config) {
        super.create_config(job, config, this.additional_commands)

        job.with {

            publishers {
                if (this.junit_filename) {
                    archiveJunit(this.junit_filename) {
                        testDataPublishers {
                            publishTestAttachments()
                        }
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

            if (this.pep8_filename) {
                publishers {
                    violations(100) {
                        pep8(10, 100, 9999, this.pep8_filename)
                    }
                }
            }
        }
    }
}
