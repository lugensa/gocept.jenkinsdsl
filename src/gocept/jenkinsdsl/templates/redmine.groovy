
class Redmine {
    def website_name
    def project_name

    public void create_config(job, config) {
        job.with {
            configure { project ->
                project / 'properties' / 'hudson.plugins.redmine.RedmineProjectProperty' {
                    redmineWebsiteName this.website_name
                    projectName this.project_name
                }
            }
        }
    }
}
