# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

## [3.6.1] - 2023-09-19
### Fixed
- Detailed logging for user events. [#1113](https://github.com/rokwire/events-manager/issues/1113)
## [3.6.0] - 2023-09-08
### Changed
- Skip all day events in imported events. [#1086](https://github.com/rokwire/events-manager/issues/1086)
- Exclude events from WebTools with certain categories. [#1085](https://github.com/rokwire/events-manager/issues/1085)
- Update categories and subcategories mapping using the latest information. [#1084](https://github.com/rokwire/events-manager/issues/1084)
- Change category names. [#1107](https://github.com/rokwire/events-manager/issues/1107)

### Fixed
- Category name mappings. [#1092](https://github.com/rokwire/events-manager/issues/1092)
- Fix cannot import name 'open_binary' from 'importlib_resources'. [#1097](https://github.com/rokwire/events-manager/issues/1097)
- Added missing event category and changed ordering of categories. [#1101](https://github.com/rokwire/events-manager/issues/1101)

## [3.5.0] - 2023-04-02
### Added
- Add hyperlink to Privacy Policy in footer. [#997](https://github.com/rokwire/events-manager/issues/997)
- Update the style of the settings page in the campus event. [#994](https://github.com/rokwire/events-manager/issues/994)
- Update the style for buttons on add new event page. [#996](https://github.com/rokwire/events-manager/issues/996)
- Update the style for white background buttons on hover. [#1006](https://github.com/rokwire/events-manager/issues/1006)
- Add the version to footer. [#988](https://github.com/rokwire/events-manager/issues/988)
- Add the syle to the dropdown menu in user event create page. [#1039](https://github.com/rokwire/events-manager/issues/1039)
- Update the style of buttons on the event detail page. [#984](https://github.com/rokwire/events-manager/issues/984)
- Add elements to the footer. [#969](https://github.com/rokwire/events-manager/issues/969)
- Update the GUI of the campus calendar listing page. [#972](https://github.com/rokwire/events-manager/issues/972)

### Changed
- Change the GUI of text input field box. [#991](https://github.com/rokwire/events-manager/issues/991)
- Update the style of pagination in user event listing page. [#989](https://github.com/rokwire/events-manager/issues/989)
- Update the home page icon and events manager hyperlink redirection. [#1008](https://github.com/rokwire/events-manager/issues/1008)
- Update Login and Logout button. [#1009](https://github.com/rokwire/events-manager/issues/1009)
- Update the buttons in the user event edit page. [#1013](https://github.com/rokwire/events-manager/issues/1013)
- Update the publish button and pending button on the campus event detail page. [#1014](https://github.com/rokwire/events-manager/issues/1014)
- Update the style of the "Link a Sub-Event" button. [#1015](https://github.com/rokwire/events-manager/issues/1015)
- Update the style of all checkboxes. [#1022](https://github.com/rokwire/events-manager/issues/1022)
- Update the hover and focus style of all buttons. Refactored and cleaned unused styles. [#1048](https://github.com/rokwire/events-manager/issues/1048)
- Update the dropdown menu on user list page. [#1063](https://github.com/rokwire/events-manager/issues/1063)
- Update the style of modals/pop-up windows. [#1054](https://github.com/rokwire/events-manager/issues/1054)
- Update the style of reset button. [#1061](https://github.com/rokwire/events-manager/issues/1061)
- Update the placeholder for user events. [#1062](https://github.com/rokwire/events-manager/issues/1062)
- Change font size and color for text.[#975](https://github.com/rokwire/events-manager/issues/975)

### Fixed
- Fix the color of publish, pending and hide the past. [#995](https://github.com/rokwire/events-manager/issues/995)
- Fix the style of badge and checkbox of the filter. [#1011](https://github.com/rokwire/events-manager/issues/1011)
- Fix the height of Create Event button. [#1021](https://github.com/rokwire/events-manager/issues/1021)
- Fix the hover text decoration and color of Edit button in the event detail page. [#1023](https://github.com/rokwire/events-manager/issues/1023)
- Fix the scheduler to take the input from setting page. [#1030](https://github.com/rokwire/events-manager/issues/1023)
- Fix the display of the orange line under the dropdown menu. [#1042](https://github.com/rokwire/events-manager/issues/1042)
- Fix flash message and group building block failure. [#1075](https://github.com/rokwire/events-manager/pull/1075)
- Fix the mouse shape to be pointer when hovering on buttons. [#1059](https://github.com/rokwire/events-manager/issues/1042)
- Fix the round corners for the input text fields. [#1060](https://github.com/rokwire/events-manager/issues/1060)
- Fix the required fields validation when creating a new user event. [#1072](https://github.com/rokwire/events-manager/issues/1072)
- Fix the style of add icon. [#1041](https://github.com/rokwire/events-manager/issues/1041)
- Fix Detect secrets GitHub action build error and updated baseline. [#1070](https://github.com/rokwire/events-manager/issues/1070)



## [3.4.0] - 2022-10-27
### Added
- Add title attribute "Events per page" to page number drop down list. [#939](https://github.com/rokwire/events-manager/issues/939)
- Add language attribute to HTML tag. [#937](https://github.com/rokwire/events-manager/issues/937)
- Add space between attribute in base.html [#938](https://github.com/rokwire/events-manager/issues/938)
- Add start date and end date to calendar events page. [#946](https://github.com/rokwire/events-manager/issues/946)
- Add title attribute to delete event image button. [#944](https://github.com/rokwire/events-manager/issues/944)
- Add support for hybrid event. [#926](https://github.com/rokwire/events-manager/issues/926)
- Add support for hybrid event in user events space. [#922](https://github.com/rokwire/events-manager/issues/922)
- Send event id to group building block if event is published or group id has been updated. [#935](https://github.com/rokwire/events-manager/issues/935)
- Update the style of create event button. [#967](https://github.com/rokwire/events-manager/issues/967)
- Update the style of the footer. [#968](https://github.com/rokwire/events-manager/issues/968)


### Fixed
- Fix that the header is not in the correct hierarchy. [#940](https://github.com/rokwire/events-manager/issues/940)
- Fix config.py env. [#955](https://github.com/rokwire/events-manager/issues/955)
- Fix changelog history. [#954](https://github.com/rokwire/events-manager/issues/954)
- Fix that the screen reader is not able to read the dropdown list in campus event listing page. [#959](https://github.com/rokwire/events-manager/issues/959)
- Fix that the screen reader is not able to read options of the dropdown lists as user navigates. [#961](https://github.com/rokwire/events-manager/issues/961)
- Fix the issue that hours and seconds will be displayed for all day events in calendar events. [#958](https://github.com/rokwire/events-manager/issues/958)
- Set the empty location description if the user event is physical event and no location provided. [#981](https://github.com/rokwire/events-manager/issues/981)

### Changed
- Change the CSS class names to match the HTML controls. [#973](https://github.com/rokwire/events-manager/issues/973)

## [3.3.1] - 2022-07-25
### Added
- Add campus hybrid event support. [#915](https://github.com/rokwire/events-manager/issues/915)
### Fixed
- Fix the isInPerson field in campus events. [#928](https://github.com/rokwire/events-manager/issues/928)

## [3.3.0] - 2022-07-11
### Added
- Add tooltip for subcategory to indicate that only Athletics Category have subcategories. [#883](https://github.com/rokwire/events-manager/issues/883)
- Default option for timezone is set as central time. [#912](https://github.com/rokwire/events-manager/issues/912)
- Placeholder text for Cost Description. [#885](https://github.com/rokwire/events-manager/issues/885)
- Add isGroupPrivate field for user to select. [#913](https://github.com/rokwire/events-manager/issues/913)
- Make end date a required field. [#911](https://github.com/rokwire/events-manager/issues/911)

### Fixed
- Fix the tooltip color on create new user event page. [#886](https://github.com/rokwire/events-manager/issues/886)
- Fix that the required fields are not being checked when submitting form. [#893](https://github.com/rokwire/events-manager/issues/893)
- Fix that the pop up window to confirm saving the published super event is not working [#880](https://github.com/rokwire/events-manager/issues/880)
- Fix that the subcategory is not emptied after changing the category [#898](https://github.com/rokwire/events-manager/issues/898)
- Fix that the save button stay disabled after selecting the first option in subcategory. [#910](https://github.com/rokwire/events-manager/issues/910)

### Changed
- Change group api key. [#891](https://github.com/rokwire/events-manager/issues/891)
- Change the placeholder value when editing or creating events for clarity. [#897](https://github.com/rokwire/events-manager/issues/897)
- Change the description of Events Manager in the home page. [#890](https://github.com/rokwire/events-manager/issues/890)
- Update SECURITY.md. [#895](https://github.com/rokwire/events-manager/issues/895)
- Use eventId instead of eventid. [#831](https://github.com/rokwire/events-manager/issues/831)

## [3.2.0] - 2022-05-18
### Changed
- Change user events and campus events link on home page. [#866](https://github.com/rokwire/events-manager/issues/866)
- Switch Space” button to home and relocate the home button. [#868](https://github.com/rokwire/events-manager/issues/866)
- Remove old home link. [#870](https://github.com/rokwire/events-manager/issues/870)
- Remove auth select endpoint. [#869](https://github.com/rokwire/events-manager/issues/869)
- Hide "Display Only With Super Event" when the event is a super event. [#864](https://github.com/rokwire/events-manager/issues/864)

### Added
- Remove duplicates in the sub-event array in super events with back end check. [#834](https://github.com/rokwire/events-manager/issues/834)
- Add "Back To Super Event" button for sub events. [#853](https://github.com/rokwire/events-manager/issues/853)
- Add rich editor for user event description. [#721](https://github.com/rokwire/events-manager/issues/721)
- Add tooltip on super event and add sub event. [#865](https://github.com/rokwire/events-manager/issues/865)

### Fixed
- Fix jinja2 version. [#852](https://github.com/rokwire/events-manager/issues/852)
- Fix the bug that the sub-event cannot be added to the super event after being unlinked from it. [#859](https://github.com/rokwire/events-manager/issues/859)
- Fix timezone validation bug. [#857](https://github.com/rokwire/events-manager/issues/857)
- Remove unnecessary fields in sub-event array of super events. [#836](https://github.com/rokwire/events-manager/issues/836)
- Fix read of closed file on uploading campus events images. [#860](https://github.com/rokwire/events-manager/issues/860)
- Fix time filters between campus events and user events. [#846](https://github.com/rokwire/events-manager/issues/846)
- Fix the search on subevent. [#872](https://github.com/rokwire/events-manager/issues/872)

## [3.1.0] - 2022-03-01
### Added
- Add script to update group id in database[#739](https://github.com/rokwire/events-manager/issues/739).
- Display the publish status of sub-events in event detail page [#772](https://github.com/rokwire/events-manager/issues/772)
- Event filtering by date added for campus event. [#714](https://github.com/rokwire/events-manager/issues/714)
- Add script to update group id in database[#739](https://github.com/rokwire/events-manager/issues/739).
- Add displayOnlyWithSuperEvent. [#741](https://github.com/rokwire/events-manager/issues/741)
- Add events per page dropdown[#713](https://github.com/rokwire/events-manager/issues/713).
- Add simple logging in __init__.py. [#748](https://github.com/rokwire/events-manager/issues/748)
- Logging instead of printing for all python file. [#748](https://github.com/rokwire/events-manager/issues/748)
- Change the sub-event delete button text to say Unlink and Add buttons to Link [#769](https://github.com/rokwire/events-manager/issues/769)
- Update modal for publishing indicate that all sub-events will also be published [#782](https://github.com/rokwire/events-manager/issues/782)
- Allow to add pending subevent. [#756](https://github.com/rokwire/events-manager/issues/756)
- Security markdown file. [#794](https://github.com/rokwire/events-manager/issues/794)
- Updated popup message on delete confirmation of super event. [#790](https://github.com/rokwire/events-manager/issues/790)
- Deleting super events deletes its sub events as well. [#789](https://github.com/rokwire/events-manager/issues/789)
- When saving a published super-event, unpublished sub-events will be published. [#797](https://github.com/rokwire/events-manager/issues/797)
- All pending sub-events will be published when a super event is published. [#771](https://github.com/rokwire/events-manager/issues/771)
- Filter superevent or existing subevent to be added as a subevent.[#826](https://github.com/rokwire/events-manager/issues/826)
- Add create event button on event detail page. [#818](https://github.com/rokwire/events-manager/issues/818)
- Disable super event checkbox for sub events. [#833](https://github.com/rokwire/events-manager/issues/833)
- Add confirmation modal when saving the published super events. [#819](https://github.com/rokwire/events-manager/issues/819)

### Fixed
- Remove the wrong subevent added to a superevent. [#764](https://github.com/rokwire/events-manager/issues/764)
- Fix the placeholder of subevent id. [#766](https://github.com/rokwire/events-manager/issues/766)
- Fix indentation of removal sub events. [#785](https://github.com/rokwire/events-manager/issues/785)
- Fix the error message on required field. [#783](https://github.com/rokwire/events-manager/issues/783)
- Fix the subevent when the track or isfeature has been updated.[#823](https://github.com/rokwire/events-manager/issues/823)
- Fixed error message when deleting subevent. [#799](https://github.com/rokwire/events-manager/issues/799)
- Fix the issue that the sub event title is not updated in the super event. [#813](https://github.com/rokwire/events-manager/issues/813)
- Fix the issue that publish the super event without sub events. [#827](https://github.com/rokwire/events-manager/issues/827)
- Update superevent when its subevent has been removed. [#838](https://github.com/rokwire/events-manager/issues/838)
- Fix subevent publish status on its super event detail page. [#840](https://github.com/rokwire/events-manager/issues/840)

### Changed
- Only allow to select the same group subevents. [#754](https://github.com/rokwire/events-manager/issues/754)
- Allow to link pending sub events to super event. [#756](https://github.com/rokwire/events-manager/issues/756)
- Release script to use the latest AWS CLI login commands. [#816](https://github.com/rokwire/events-manager/issues/816)

## [3.0.5] - 2022-01-12
### Fixed
- Fix user image upload to Events Building Block. [#806](https://github.com/rokwire/events-manager/pull/809)

## [3.0.4] - 2022-01-05
### Fixed
- Issue with images in WebTool events not getting uploaded to Events BB. [#798](https://github.com/rokwire/events-manager/issues/798)

## [3.0.3] - 2021-10-19
### Fixed
- Hotfix to check the platformid of subevent to be added to a superevent [#776](https://github.com/rokwire/events-manager/issues/776)

## [3.0.2] - 2021-09-28
### Fixed
- Fix login to use Groups Building Block [#755](https://github.com/rokwire/events-manager/issues/755)

## [3.0.1] - 2021-09-13
### Added
- Add group environment variables in config.py.template.
### Changed
- Change APScheduler version.

## [3.0.0] - 2021-09-07
### Added
- Event filtering by group_ids functionality added [#673](https://github.com/rokwire/events-manager/issues/673)
- Groups for user to select in event create/edit page. [#674](https://github.com/rokwire/events-manager/issues/674)
- UIN in requested claims. [#672](https://github.com/rokwire/events-manager/issues/672)
- Get_admin_groups to retrieve admin_groups whenever required. [#671](https://github.com/rokwire/events-manager/issues/671)
- Add group admin privileges to access user events. [#678](https://github.com/rokwire/events-manager/issues/678)
- Not available tag removed. [#641](https://github.com/rokwire/events-manager/issues/641)
- Log status code when failed to download campus events. [#688](https://github.com/rokwire/events-manager/issues/688)
- Event filtering by groups on event listing page [#676](https://github.com/rokwire/events-manager/issues/676)
- Add "All Groups" on event listing page [#702](https://github.com/rokwire/events-manager/issues/702)
- Add "Created by" field in event detail page. [#718](https://github.com/rokwire/events-manager/issues/718)

### Fixed
- End dates can't be deleted. [#691](https://github.com/rokwire/events-manager/issues/690)
- All-day events not working. [#690](https://github.com/rokwire/events-manager/issues/691)
- User doesn't belong to any group will trigger a redirect loop upon login. [#695](https://github.com/rokwire/events-manager/issues/695)
- delete events from events manager in local if the events are not in events building blocks.[#684](https://github.com/rokwire/events-manager/issues/684)
- get_admin_group_ids() will only return first group ID.[#699](https://github.com/rokwire/events-manager/issues/699)
- Fix failure to publish a free user event. [#697](https://github.com/rokwire/events-manager/issues/697)
- Fix the same day date filter search. [#705](https://github.com/rokwire/events-manager/issues/705)
- Fix campus calendar id to download campus event image. [#715](https://github.com/rokwire/events-manager/issues/715)
- Fix campus event image url. [#716](https://github.com/rokwire/events-manager/issues/716)
- Fix date filters in user event. [#728](https://github.com/rokwire/events-manager/issues/728)
- Fix the wrong format of user input datetime.[#740](https://github.com/rokwire/events-manager/issues/740)

### Changed
- Hide Past event -> Hide Past Events. [#641](https://github.com/rokwire/events-manager/issues/641)
- Crop event title at a fixed number of characters. [#667](https://github.com/rokwire/events-manager/issues/667)
- Move dates under a second row below the title and move badges to the right of the title. [#666](https://github.com/rokwire/events-manager/issues/666)
- Split datetime-local control to date and time to fix compatibility issue with firefox and safari. [#479](https://github.com/rokwire/events-manager/issues/479)
- Move Free Event above Cost Description. [#661](https://github.com/rokwire/events-manager/issues/661)

### Removed
- User events that are not associated with groups from being viewable. [#678](https://github.com/rokwire/events-manager/issues/678)

## [2.4.2] - 2021-08-11
### Fixed
- Fix user event image operation using event id of events building block.[#707](https://github.com/rokwire/events-manager/issues/707)

## [2.4.1] - 2021-06-23
### Fixed
- Fix compatibility issue with the all-day event in the current UI. [#662](https://github.com/rokwire/events-manager/issues/662)

## [2.4.0] - 2021-06-22
### Added
- Various UI update [#654](https://github.com/rokwire/events-manager/issues/654) [#653](https://github.com/rokwire/events-manager/issues/653) [#652](https://github.com/rokwire/events-manager/issues/652) [#651](https://github.com/rokwire/events-manager/issues/651)
- Virtual event checkbox moved above location field. Location field renamed. Dynamic header implemented [#636](https://github.com/rokwire/events-manager/issues/636)
- Registration URL and Registration Label fields added with functionality [#640](https://github.com/rokwire/events-manager/issues/640)
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


[Unreleased]: https://github.com/rokwire/events-manager/compare/3.6.1...HEAD
[3.6.1]: https://github.com/rokwire/events-manager/compare/3.6.0...3.6.1
[3.6.0]: https://github.com/rokwire/events-manager/compare/3.5.0...3.6.0
[3.5.0]: https://github.com/rokwire/events-manager/compare/3.4.0...3.5.0
[3.4.0]: https://github.com/rokwire/events-manager/compare/3.3.1...3.4.0
[3.3.1]: https://github.com/rokwire/events-manager/compare/3.3.0...3.3.1
[3.3.0]: https://github.com/rokwire/events-manager/compare/3.2.0...3.3.0
[3.2.0]: https://github.com/rokwire/events-manager/compare/3.1.0...3.2.0
[3.1.0]: https://github.com/rokwire/events-manager/compare/3.0.5...3.1.0
[3.0.5]: https://github.com/rokwire/events-manager/compare/3.0.4...3.0.5
[3.0.4]: https://github.com/rokwire/events-manager/compare/3.0.3...3.0.4
[3.0.3]: https://github.com/rokwire/events-manager/compare/3.0.2...3.0.3
[3.0.2]: https://github.com/rokwire/events-manager/compare/3.0.1...3.0.2
[3.0.1]: https://github.com/rokwire/events-manager/compare/3.0.0...3.0.1
[3.0.0]: https://github.com/rokwire/events-manager/compare/2.4.2...3.0.0
[2.4.2]: https://github.com/rokwire/events-manager/compare/2.4.1...2.4.2
[2.4.1]: https://github.com/rokwire/events-manager/compare/2.4.0...2.4.1
[2.4.0]: https://github.com/rokwire/events-manager/compare/2.3.1...2.4.0
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
