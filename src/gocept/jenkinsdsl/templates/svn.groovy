
class SVN implements VersionControlSystem {
    def baseurl = null
    def group = null
    def name = null
    def postfix = 'trunk'
    def credentials = null
    def realm = null
    def scm_browser = null
    def subdirectory = null

    public void create_config(job, config) {
        def fullurl

        fullurl = this.baseurl + '/'
        if ( this.group != null ) {
            fullurl = fullurl + this.group + '/'
        }
        fullurl = fullurl + this.name + '/' + this.postfix

        job.with {
            scm {
                svn {
                    location(fullurl) {
                        credentials this.credentials
                        if (this.subdirectory != null) {
                            directory(this.subdirectory)
                        }
                    }
                }
            }
            if ( this.realm != null ) {
                configure { project ->
                    project / scm / 'additionalCredentials' / 'hudson.scm.SubversionSCM_-AdditionalCredentials' {
                        realm this.realm
                        credentialsId this.credentials
                    }
                }
            }

            if ( this.scm_browser != null ) {
                configure { project ->
                    project / scm / browser (class: this.scm_browser)
                }
            }
        }
    }
}
