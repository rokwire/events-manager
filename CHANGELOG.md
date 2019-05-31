# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.1] - 2019-05-24
### Added
- db.py that has needed functions to support DB usage in authentication function
- \_\_init\_\_.py that creates an app instance but its config loading is different than the one in tutorial

### Changed
- Modify some functions in auth.py written by Phoebe to accommodate mongDB's usage
- html files in template

### Removed

## [0.0.2] - 2019-05-31
### Added
- user events page and user event subpage and `user_events` blueprint
- user events templates
- Login and register pages and `auth` blueprint
- db.py that has needed functions to support DB usage in authentication function
- \_\_init\_\_.py that creates an app instance but its config loading is different than the one in tutorial

### Changed
- Modify some functions in auth.py written by Phoebe to accommodate mongDB's usage
- html files in template


## [0.0.3] - 
### Added
- sourceEvent.py for downloading, parsing, and storing calendar events
- user_events.py for providing accessing to db for user events management

### Changed
- html file under /template/events to adapt to base.html
- auth.py for updating the usage of db functions

