// configure Notification plug-in
class Notification {

    def credential_id

    private void create_config(job, config) {

        job.with {
            properties {
                if (this.credential_id){
                    hudsonNotificationProperty {
                        endpoints {
                            endpoint {
                                urlInfo {
                                urlType('SECRET')
                                urlOrId(this.credential_id)
                                }
                            event('finalized')
                            format('JSON')
                            loglines(0)
                            protocol('HTTP')
                            retries(0)
                            timeout(30000)
                            }
                        }
                    }
                }
            }
        }
    }
}
