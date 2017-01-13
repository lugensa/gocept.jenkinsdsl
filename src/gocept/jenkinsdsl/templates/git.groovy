class GIT implements VersionControlSystem {
    def baseurl = null
    def group = null
    def name = null
    def branch = 'default'
    def scm_browser = null
    def scm_browser_url = null
    def subdirectory = null

    public void create_config(job, config) {
        def fullurl
        def full_scm_browser_url

        fullurl = this.baseurl + '/'
        if (this.group != null) {
            fullurl = fullurl + this.group + '/'
        }
        fullurl = fullurl + this.name +'.git'

        if (scm_browser_url) {
            full_scm_browser_url = this.scm_browser_url + '/'
        } else {
            full_scm_browser_url = this.baseurl + '/'
        }
        full_scm_browser_url = full_scm_browser_url + this.name + '/'

        job.with {
            scm {
                git(fullurl) {
                    branch(this.branch)
                    if (this.subdirectory != null) {
                        extensions {
                            relativeTargetDirectory(this.subdirectory)
                        }
                    }
                    if (this.scm_browser != null){
                        configure{
                            git -> git / browser(class: this.scm_browser) {
                            url full_scm_browser_url
                            }
                        }
                    }
                }
            }
        }
    }
}
