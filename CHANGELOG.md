# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Virtual event checkbox moved above location field. Location field renamed. Dynamic header implemented [#636](https://github.com/rokwire/events-manager/issues/636)
- Placeholder text added to Event URL field. [#637](https://github.com/rokwire/events-manager/issues/637)
- Add Free Event checkbox and add database entry. [#635](https://github.com/rokwire/events-manager/issues/635)
- Add tag autocomplete and change the style to comma separate. [#637](https://github.com/rokwire/events-manager/issues/622)
- XML12 was changed to XML15 in the config.py template. [#634](https://github.com/rokwire/events-manager/issues/634)
- Add deletion button to delete campus events. [#618](https://github.com/rokwire/events-manager/issues/618)
- Refresh setting page after adding a new calendar. [#605](https://github.com/rokwire/events-manager/issues/605)
- Show the message box to tell the user the failure of deletion on campus event.[#623](https://github.com/rokwire/events-manager/issues/623)
- Add pending button on campus event page if this event is published.[#630](https://github.com/rokwire/events-manager/issues/630)
- Map event type Religious/Cultural to Community.[#615](https://github.com/rokwire/events-manager/issues/615)
- Add isEventFree field in the event if costFree field in WebTools event.[#645](https://github.com/rokwire/events-manager/issues/645)

### Changed
- Do pagination downloading on campus events from webtool endpoint.[#607](https://github.com/rokwire/events-manager/issues/607).
### Fixed
- Issue with download scheduler (when using manual calendar events download) blocking the web app and resulting in internal server error. [#620](https://github.com/rokwire/events-manager/issues/620).
- Fix updated scheduling download time data does not refresh on the setting page.[#625](https://github.com/rokwire/events-manager/issues/625)

## [2.3.1] - 2021-03-22
### Security
- Bump pillow from 8.0.0 to 8.1.1.(https://github.com/rokwire/events-manager/pull/610)
- Bump jinja2 from 2.10.1 to 2.11.3.(https://github.com/rokwire/events-manager/pull/611)

## [2.3.0] - 2021-03-02
### Added
- Allow user to view event within selected time range. [#588](https://github.com/rokwire/events-manager/issues/588)
- More information in event list. [#537](https://github.com/rokwire/events-manager/issues/537)
- Checkbox to hide past event [#587](https://github.com/rokwire/events-manager/issues/587)
- Custom error pages. [#356](https://github.com/rokwire/events-manager/issues/356)
- Contributor guidelines. [#574](https://github.com/rokwire/events-manager/issues/574)
- A pull request template. [#575](https://github.com/rokwire/events-manager/issues/575)
- Add detect-secrets.yaml. [#591](https://github.com/rokwire/events-manager/issues/591)
- Allow user to select events per pages. [#586](https://github.com/rokwire/events-manager/issues/586)

### Changed
- Read version from git tag [#376](https://github.com/rokwire/events-manager/issues/376)
- Change to allow to download and upload campus events without location.[#540](https://github.com/rokwire/events-manager/issues/540)
- Change .secrets-baseline.[#591](https://github.com/rokwire/events-manager/issues/591)

## [2.2.0] - 2020-10-27
- Accept all image extension in ALLWED_IMAGE_EXTENSIONS. [#555](https://github.com/rokwire/events-manager/issues/555)
- Read ALLOWED_IMAGE_EXTENSIONS as string. [#553](https://github.com/rokwire/events-manager/issues/553)
- Use latest base image when building Docker image. [#560](https://github.com/rokwire/events-manager/issues/560)
- Change the timezone name on GUI.[#568](https://github.com/rokwire/events-manager/issues/568)

### Added
- Yelp's detect secrets baseline file and pre-commit hook. [#563](https://github.com/rokwire/events-manager/issues/563)
- Add time zone selection feature. [#533](https://github.com/rokwire/events-manager/issues/533)

### Fixed
- Fix timezone conversion issue with end date [#578](https://github.com/rokwire/events-manager/issues/578)

## [2.1.6] - 2020-10-13
### Fixed
- Fix the exception of editing the subevent title. [#556](https://github.com/rokwire/events-manager/issues/556)

## [2.1.5] - 2020-10-13
### Fixed
- Fix image folder permission within Docker image to fix image upload/download error. [#547](https://github.com/rokwire/events-manager/issues/547)

## [2.1.4] - 2020-10-08
### Added
- Add a filter for blocking events that are not shared with Illinois Mobile and clean previous records [#520](https://github.com/rokwire/events-manager/issues/520)
- Provide an option to mark an event as virtual (Add `isVirtual` to document) [#517](https://github.com/rokwire/events-manager/issues/517)
- Update config.py.template [#518](https://github.com/rokwire/events-manager/issues/518)
- Add field `superEventID` to document to keep track of the super event locally [#480](https://github.com/rokwire/events-manager/issues/480)
- Add `virtualEvent` flag coming from WebTools[#526](https://github.com/rokwire/events-manager/issues/526)

### Fixed
- Fix the EXCLUDED_LOCATION to use ENV variables. [#510](https://github.com/rokwire/events-manager/issues/510)
- Fix calendar events display location on online events [#510](https://github.com/rokwire/events-manager/issues/510)
- Fix the existence of super event id [#531](https://github.com/rokwire/events-manager/issues/531)
- The sub event name in the super event will not change when the sub event name changes [#483](https://github.com/rokwire/events-manager/issues/483)

## [2.1.3] - 2020-09-03
### Fixed
- Fix calendar events publish [#513](https://github.com/rokwire/events-manager/issues/513)
- Fix calendar event view page [#515](https://github.com/rokwire/events-manager/issues/515)

## [2.1.2] - 2020-08-20
### Fixed
- Fix subevent name updates [#505](https://github.com/rokwire/events-manager/issues/505)

### Changed
- Reduces container image size to 498 MB from 1.27 GB using a multistage
  Dockerfile [#507](https://github.com/rokwire/events-manager/pull/507)

### Security
- The container runs gunicorn as user nobody instead of as root
  [#507](https://github.com/rokwire/events-manager/pull/507)
- Eliminates all unnecessary development tools used to build container
  [#507](https://github.com/rokwire/events-manager/pull/507)

## [2.1.1] - 2020-08-05
### Fixed
- Fix user event datetime conversion [#492](https://github.com/rokwire/events-manager/issues/492)
- Fixed the endDate display in the preview page and match its format with startDate. [#491](https://github.com/rokwire/events-manager/issues/491)

### Added
- CODEONWERS file. [#493](https://github.com/rokwire/events-manager/issues/493)

## [2.1.0] - 2020-07-29
### Added
- LICENSE file [#429](https://github.com/rokwire/events-manager/issues/429)
- Code of conduct file [#446](https://github.com/rokwire/events-manager/issues/446)
- Issue templates - bug report and fearture request. [#472](https://github.com/rokwire/events-manager/issues/472)
- Image upload for user event [#320](https://github.com/rokwire/events-manager/issues/320)
- Image preview(with a fixed resolution) when user uploads the image and edits the image [#380](https://github.com/rokwire/events-manager/pull/380) [#401](https://github.com/rokwire/events-manager/issues/401)
- Sub-events in a super-event preview page are now clickable, redirecting to the sub-event preview page [#454](https://github.com/rokwire/events-manager/issues/454)

### Fixed
- Not calculating geocoordinates for virtual events [#427](https://github.com/rokwire/events-manager/issues/427)
- Add the missing `imageUrl` in events [#482](https://github.com/rokwire/events-manager/issues/482)
- Redirection to home page. [#296](https://github.com/rokwire/events-manager/issues/296)
- Network exception handling when deleting user event from building block. [#308](https://github.com/rokwire/events-manager/issues/308)
- Year can have 6 digits [#351](https://github.com/rokwire/events-manager/issues/351)

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
- setting requires user's login.

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

[Unreleased]: https://github.com/rokwire/events-manager/compare/2.3.1...HEAD
[2.3.1]: https://github.com/rokwire/events-manager/compare/2.2.0...2.3.1
[2.3.0]: https://github.com/rokwire/events-manager/compare/2.2.0...2.3.0
[2.2.0]: https://github.com/rokwire/events-manager/compare/2.1.6...2.2.0
[2.1.6]: https://github.com/rokwire/events-manager/compare/2.1.5...2.1.6
[2.1.5]: https://github.com/rokwire/events-manager/compare/2.1.4...2.1.5
[2.1.4]: https://github.com/rokwire/events-manager/compare/2.1.3...2.1.4
[2.1.3]: https://github.com/rokwire/events-manager/compare/2.1.2...2.1.3
[2.1.2]: https://github.com/rokwire/events-manager/compare/2.1.1...2.1.2
[2.1.1]: https://github.com/rokwire/events-manager/compare/2.1.0...2.1.1
[2.1.0]: https://github.com/rokwire/events-manager/compare/2.0.1...2.1.0
[2.0.1]: https://github.com/rokwire/events-manager/compare/2.0.0...2.0.1
[2.0.0]: https://github.com/rokwire/events-manager/compare/1.0.6...2.0.0
[1.0.6]: https://github.com/rokwire/events-manager/compare/1.0.5...1.0.6
[1.0.5]: https://github.com/rokwire/events-manager/compare/1.0.4...1.0.5
[1.0.4]: https://github.com/rokwire/events-manager/compare/1.0.3...1.0.4
[1.0.3]: https://github.com/rokwire/events-manager/compare/1.0.2...1.0.3
[1.0.2]: https://github.com/rokwire/events-manager/compare/1.0.1...1.0.2
[1.0.1]: https://github.com/rokwire/events-manager/compare/1.0.0...1.0.1
[1.0.0]: https://github.com/rokwire/events-manager/releases/tag/1.0.0
