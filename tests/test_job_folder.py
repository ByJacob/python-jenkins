from mock import patch

import jenkins
from tests.base import JenkinsTestBase
from tests.helper import build_response_mock


class JenkinsGetJobFolderTest(JenkinsTestBase):

    @patch.object(jenkins.Jenkins, 'jenkins_open')
    def test_simple(self, jenkins_mock):
        folder, name = self.j._get_job_folder('my job')
        self.assertEqual(folder, '')
        self.assertEqual(name, 'my job')

    @patch.object(jenkins.Jenkins, 'jenkins_open')
    def test_single_level(self, jenkins_mock):
        folder, name = self.j._get_job_folder('my folder/my job')
        self.assertEqual(folder, 'job/my folder/')
        self.assertEqual(name, 'my job')

    @patch.object(jenkins.Jenkins, 'jenkins_open')
    def test_multi_level(self, jenkins_mock):
        folder, name = self.j._get_job_folder('folder1/folder2/my job')
        self.assertEqual(folder, 'job/folder1/job/folder2/')
        self.assertEqual(name, 'my job')


class JenkinsCreateFolderTest(JenkinsTestBase):

    @patch('jenkins.requests.Session.send', autospec=True)
    def test_create_new_folder(self, session_send_mock):
        session_send_mock.side_effect = iter([
            build_response_mock(200, self.crumb_data),  # crumb
            build_response_mock(200, None),  # request
        ])
        self.j.create_folder(u'New-Test-Folder')

    @patch('jenkins.requests.Session.send', autospec=True)
    def test_create_new_folder_that_already_exists(self, session_send_mock):
        session_send_mock.side_effect = iter([
            build_response_mock(200, self.crumb_data),  # crumb
            build_response_mock(400),  # request
        ])

        folder_name = u'Folder-that-already-exists'

        with self.assertRaises(jenkins.JenkinsException) as context_manager:
            self.j.create_folder(folder_name)
        self.assertEqual(
            str(context_manager.exception),
            u'Error creating folder [' + folder_name + ']. Probably it already exists.')

    @patch('jenkins.requests.Session.send', autospec=True)
    def test_create_new_folder_that_already_exists_ignoring_errors(self, session_send_mock):
        session_send_mock.side_effect = iter([
            build_response_mock(200, self.crumb_data),  # crumb
            build_response_mock(400),  # request
        ])

        self.j.create_folder(u'Folder-that-already-exists', ignore_failures=True)
