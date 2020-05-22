# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
## Fixed
- Redirection to home page. [#296](https://github.com/rokwire/events-manager/issues/296)

## [2.0.1] - 2020-05-18
### Changed
- update pymongo to 3.10.0
### Fixed
- fix pymongo distinct find.
- fixed delete button cursor hovering issue.

## [2.0.0] - 2020-05-11
### Changed
- Change approved user event to published, hide disapprove button and change approve button to be publish on GUI.
- hide search bar, part of status selection and history requests on user events GUI.
- change the style of deletion modal the same as the approval modal on user events.
- moved event date-time conversion code to python
- made end date optional
- updated backend code for editing an event.

### Added
- add user events deletion endpoint and GUI to click delete button to delete user event.
- added 'Counseling Center' Calendar
- add event notification
- send data message with event notification.
- support for creating all day events.
- geocoding of location description/address when creating a new event.
- support for authenticating using Shibboleth + OIDC.
- basic home page.
- email of user in `createdBy` field when creating a new event.
- session timeout

### Fixed
- fix editing event location
- fix the event id in data message on notification.
- fix the event id on sending notification.
- fix the browser redirection url after editing the user event.
- fix userevent approval failure status change.
- fix userevent approval.
- fix the redirection when user clicks the add button to create a new event.
- check the existence of startdate and enddate for user event html.
- fix config for event notification.
- load calendar from db.
- skip events if there is no location or empty location.
- optimize the google geolocation service usage
- fix UTC time conversion outside of central timezone.
- required fields bug in the add event page.
- validation for optional end date field. 
- fixed a few issues related to editing an event.
- check before deleting field.

## [1.0.6] - 2020-03-17
### Added
- Add tls,srv python module to pymongo.

## [1.0.5] - 2019-12-10
### Fixed
- specify the python version 3.7.4 to build docker image.

### Added
- add new webtool calendar url.

## [1.0.4] - 2019-11-27
### Fixed
- update webtool calendar url.

## [1.0.3] - 2019-11-02
### Fixed
- css bug incompatible with url perfix
- fix event time to UTC conversion.

## [1.0.2] - 2019-10-15
### Fixed
- get collection name from config.py


## [1.0.1] - 2019-10-14
### Added
- add SLC predefined geolocation.

### Fixed
- Incorrect geolocations outside Champaign-Urbana area.

## [1.0.0] - 2019-10-11
### Fixed
-- setting requires user's login.

### Added
- dockerize events manager
- source and calendar pages, `event` blueprint
- user events page and user event subpage and `user_events` blueprint
- user events templates
- Login and register pages and `auth` blueprint
- db.py that has needed functions to support DB usage in authentication function
- \_\_init\_\_.py that creates an app instance but its config loading is different than the one in tutorial
- python scripts in *utilities* subfolder for providing wrapper db functions and source events crawling
- Added registrationLabel field to be parsed.
- Release scripts.

### Changed
- `base.html` to add spacing between items in navigation bar
- Modify some functions in auth.py written by Phoebe to accommodate mongDB's usage
- html files in template
- Insert subcatogories map into constants
- event parsing now includes recurring event fields.
- PUT and PATCH URLs now use Events Building Block Event ID.
- Authorization header for communicating with Events Building Block.
- Set secrets in environment variables  
- Update S3 image upload ACL to bucket-owner-full-control
- Set more config.py variables as environment variables.  

### Removed
- References to AWS keys and variables.
