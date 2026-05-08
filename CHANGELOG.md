
<a name="v1.3"></a>
## [v1.3](https://github.com/danylo829/containery/compare/v1.2...v1.3)

### Bug Fixes

- **core:** Fix init after migration
- **core:** Fix Docker init
- **core:** Improve version validation in update check
- **core:** Update migration configuration
- **core:** Fix image, volume and network deletion
- **dashboard:** Disable "Clean All" button on load
- **style:** Fix custom select display
- **style:** Fix number input styles
- **style:** Update select dropdown
- **style:** Fix sidebar icons width in closed state
- **style:** Ensure responsive layout for permissions grid on mobile
- **style:** Update sidebar navigation styles for certain devices
- **style:** Fix mobile sidebar, change to bottom layout
- **style:** Fix inputs height for large screens
- **user:** Preserve user defined order of container list settings

### Code Refactoring

- **style:** Reworked colors and theme logic
- **style:** Rework and optimize styles
- **user:** Increase stability and maintainability, improve some UI elements

### Features

- **container:** Add containers list customization
- **container:** Add sorting by compose project in containers list
- **core:** Add multiple Docker hosts support
- **core:** Add startup ASCII art
- **core:** Add seed script to populate database with synthetic test data
- **core:** Implement personal settings migration, improve container list customization
- **core:** Add last lines parameter to logs retrieval
- **style:** Improve visual appearance of select inputs

### Performance Improvements

- **core:** Add auto reload page on CSRF errors
- **core:** Switch to Alpine base image


<a name="v1.2"></a>
## [v1.2](https://github.com/danylo829/containery/compare/v1.1...v1.2)

### Bug Fixes

- **auth:** Fix admin creation logic

### Features

- **core:** Add error message hint


<a name="v1.1"></a>
## [v1.1](https://github.com/danylo829/containery/compare/v1.0...v1.1)

### Bug Fixes

- **core:** Build confirmation modal dynamically
- **styles:** Update accent colors for dark theme
- **user:** Display user roles as separate badges
- **user:** Remove autocomplete username and password on user creation form

### Features

- **ci:** Provide image description
- **core:** Provide tooltips on various buttons
- **core:** Implement Docker prune support (containers, images, networks and volumes)
- **core:** Add clear button to search fields
- **core:** Add handler for Bad Request errors
- **style:** Improve modal styles and animations


<a name="v1.0"></a>
## [v1.0](https://github.com/danylo829/containery/compare/v0.1.2...v1.0)

### Bug Fixes

- **ci:** Escape HTML characters in changelog commit subjects

### Code Refactoring

- **ci:** Improve releases creation

### Features

- **auth:** Enhance login flow with safe redirect handling
- **ci:** Introduce git-chglog
- **core:** Add update notification
- **core:** Add About page
- **core:** Implement session timeout configuration


<a name="v0.1.2"></a>
## [v0.1.2](https://github.com/danylo829/containery/compare/v0.1.1...v0.1.2)

### Bug Fixes

- **auth:** Correctly add permission values to admin role during installation
- **container:** Fix container actions dont work


<a name="v0.1.1"></a>
## [v0.1.1](https://github.com/danylo829/containery/compare/v0.1...v0.1.1)

### Bug Fixes

- **container:** Fix container terminal does not open

### Code Refactoring

- **user:** Refactor user and role management with permissions

### Features

- **core:** Add tables prefixes
- **core:** Enhance error handling by parsing docker error messages


<a name="v0.1"></a>
## v0.1

### Bug Fixes

- **app:** Prevent full app initialization in CLI context
- **auth:** Fix role error
- **ci:** Improve CI process
- **ci:** Add tag message to releases
- **ci:** Add tag message to releases
- **ci:** Change dockerfile build release from
- **ci:** Add version label to production Dockefile
- **ci:** Fix script permissions
- **config:** Set default values for SECRET_KEY and CSRF_SECRET_KEY
- **container:** Fix terminal functionality
- **container:** Avoid adding &lt;hr&gt; after the last port binding
- **core:** Fix personal settings DB records deletion
- **core:** fixed sidebar flickering
- **core:** Remove unused close btn from js
- **core:** Remove unused socketio functionality
- **core:** Fix error page messages
- **docker:** Remove unused import and add type hint
- **docs:** Add badges
- **docs:** Update readme
- **network:** Remove debug
- **network:** Route path fix
- **style:** Fix dynamic scrollbar handling for table boxes
- **style:** Disable blue highlight on mobile button clicks
- **style:** Fix table shutters while loading last search value
- **style:** Adjust table box height
- **style:** Fix load average table
- **style:** Correct spinner position
- **style:** Fix submit button radius
- **style:** Fix mobile layout for breadcrumbs
- **style:** Fixed icons flickering on page reload
- **user:** Add 'Accept' header in fetch requests for proper JSON handling
- **user:** Fixed minimal passwrd length error
- **user:** Prevent editing of super admin role on backend side
- **user:** Fix user deletion
- **user:** Update remove_role endpoint to use DELETE method

### Code Refactoring

- **app:** Migrate to separate models file for each module
- **app:** Refactor application initialization into ApplicationFactory class
- **config:** Migrate to environment variables
- **container:** Update network info structure and template links
- **container:** Improve flash messages and redirect logic for container actions
- **core:** Remove unused imports and streamline code structure
- **core:** Restructure application modules. Introduce error page handlers
- **core:** Restructure module imports and registration for improved organization and clarity
- **core:** Update static files usage, add volumes, network delete
- **core:** Add Gunicorn config
- **core:** Update app data paths for consistency
- **core:** Remove unused import
- **docker:** Remove unnecessary Threading
- **docker:** Update Docker integration to use configurable socket path
- **docker:** Change entry point to entrypoint.sh, add Flask-Migrate
- **docs:** Update README
- **index:** Move index routes to new module structure
- **index:** Remove unused import of User model
- **main:** Remove unused static files logic
- **settings:** Update settings module structure and styles; consolidate static files
- **style:** Update text colors for dark_mixed mode to improve readability
- **style:** Simplify dashboard button structure and improve styling
- **style:** Update restart/revert icons
- **style:** Clean up unused CSS variables and styles for flash messages
- **styles:** Consolidate color styles into a single file
- **user:** Clean up forms and routes
- **user:** Improve user deletion
- **user:** Consolidate role management forms and templates
- **user:** Remove unused blueprint setup and context processor from user routes
- **user:** Remove unused import (Role) from user routes
- **user:** Remove unused role deletion js functionality
- **user:** Switch from path to query parameters in profile view

### Features

- **ci:** Add production Dockerfile
- **ci:** Introduce CI
- **container:** Add start, stop, and delete container functionality
- **container:** Add confirmation modal for container deletion
- **core:** Intoduced webassets
- **core:** Add .dockerignore
- **core:** Add search preserving between page reloads
- **core:** Implement assets logic
- **dashboard:** Add hostname info
- **image:** Add 'created' timestamp to images list
- **image:** Add image deletion
- **network:** Add network deletion
- **network:** Add network info page
- **settings:** Add global settings page
- **style:** Implement dynamic scrollbar handling for table boxes
- **style:** Add minimal pass notification
- **style:** Change default accent color
- **style:** Change sidebar icon
- **style:** Migrated to svg icons
- **style:** Set default loading spinner state to hidden
- **user:** Add ability to change user role
- **volume:** Add volume info page

### Performance Improvements

- **container:** Increase default terminal timeout
- **dashboard:** Increase polling interval
- **user:** Role deletion refactor

