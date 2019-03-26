
class JobConfig {
    public String name
    public String description
    public String disabled
    public String is_public
    public VersionControlSystem vcs
    public Builder builder
    def redmine = null // new Redmine(name: 'relaunch-verdi-p2')
    def notification = null // new Notification(credatial_id: 'ci.gocept.com')

}
