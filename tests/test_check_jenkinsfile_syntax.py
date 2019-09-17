from mock import patch

from tests.base import JenkinsTestBase
from tests.helper import build_response_mock


class JenkinsCheckJenkinsfileSyntax(JenkinsTestBase):

    @patch('jenkins.requests.Session.send', autospec=True)
    def test_check_syntax_of_a_valid_file(self, session_send_mock):

        valid_jenkinsfile_content = """
        pipeline {
            agent any ;
            stages {
                stage("blah")
                {
                    stexps {
                        sh("pwd")
                    }
                }
            }
        }
        """

        valid_response = {
            "status": "ok",
            "data": {
                "result": "success"
            }
        }
        session_send_mock.side_effect = iter([
            build_response_mock(200, self.crumb_data),  # crumb
            build_response_mock(200, valid_response)  # request
        ])
        response = self.j.check_jenkinsfile_syntax(valid_jenkinsfile_content)
        self.assertEqual(response, [])

    @patch('jenkins.requests.Session.send', autospec=True)
    def test_check_syntax_of_an_invalid_file(self, session_send_mock):

        invalid_jenkinsfile_content = """node {  "pwd" } """

        invalid_response = {
         "status": "ok",
         "data": {
          "result": "failure",
          "errors": [
           {
            "error": [
             "Unknown stage section \"stexps\". Starting with version 0.5, steps in a stage must be" +
             " in a \"steps\" block. @ line 5, column 9.",
             "Expected one of \"steps\", \"stages\", or \"parallel\" for stage \"blah\" @ line 5, column 9."
            ]
           }
          ]
         }
        }

        session_send_mock.side_effect = iter([
            build_response_mock(200, self.crumb_data),  # crumb
            build_response_mock(200, invalid_response)  # request
        ])
        response = self.j.check_jenkinsfile_syntax(invalid_jenkinsfile_content)
        self.assertEqual(response, invalid_response["data"]["errors"])
