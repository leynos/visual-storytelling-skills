Feature: OpenShot packaging
  Scenario: Package accepted generated clips into an OpenShot project
    Given a completed generated media project
    When I run the OpenShot packaging command
    Then an OpenShot project and sidecar are written in timeline order
