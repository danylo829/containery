# Containery 1.3 is out!

This release introduces support for managing multiple Docker hosts and includes a visual refresh with glassmorphism-style UI elements, along with a number of bug fixes and smaller improvements.

- **Multiple Docker hosts** — Docker hosts can now be added, configured, and managed through the settings page. Each host supports a configurable address and port, connection status tracking, and a test connection feature. Container exec, logs, and other operations respect the selected host.
- **Glassmorphism UI** — The interface has been updated with a glassmorphism visual style across cards, panels, and dashboard elements.

### Features

- **hosts:** Add multiple Docker hosts management with status indicators and loading states
- **hosts:** Add test connection feature when adding a Docker host
- **hosts:** Add port customization for Docker hosts
- **hosts:** Initialize a default Docker host if the table is empty
- **exec:** Add Docker hosts support to container exec
- **container:** Add stream selection in container logs
- **container:** Add empty state message for container list when no containers are found
- **container:** Add filters to containers prune logic
- **dashboard:** Add message when no hosts are configured
- **dashboard:** Speed up dashboard load with threads
- **core:** Add dedicated JS for loading spinner
- **docs:** Add documentation for managing multiple Docker hosts

### Features

- **hosts:** Add multiple Docker hosts management with status indicators and loading states
- **hosts:** Add test connection feature when adding a Docker host
- **hosts:** Add port customization for Docker hosts
- **hosts:** Initialize a default Docker host if the table is empty
- **exec:** Add Docker hosts support to container exec
- **container:** Add containers list customization
- **container:** Add sorting by compose project in containers list
- **container:** Add stream selection in container logs
- **container:** Add empty state message for container list when no containers are found
- **container:** Add filters to containers prune logic
- **dashboard:** Add message when no hosts are configured
- **dashboard:** Speed up dashboard load with threads
- **core:** Add startup ASCII art
- **core:** Add seed script to populate database with synthetic test data
- **core:** Implement personal settings migration, improve container list customization
- **core:** Add last lines parameter to logs retrieval
- **core:** Add dedicated JS for loading spinner
- **style:** Improve visual appearance of select inputs
- **docs:** Add documentation for managing multiple Docker hosts

### Bug Fixes

- **terminal:** Fix terminal resize bug and exec on macOS
- **container:** Fix container resize bug
- **container:** Fix container list error when host is unreachable
- **container:** Fix bug with multiple container list settings panels being opened simultaneously
- **container:** Fix conditional rendering for compose and Docker host selects
- **container:** Preserve user defined order of container list settings
- **hosts:** Fix Docker hosts usage across main/container routes
- **hosts:** Fix fallback to default version
- **hosts:** Fix several Docker lib exec bugs
- **core:** Fix init after migration
- **core:** Fix Docker init
- **core:** Improve version validation in update check
- **core:** Update migration configuration
- **core:** Fix image, volume and network deletion
- **dashboard:** Disable "Clean All" button on load
- **logs:** Fix logs display on small screens
- **style:** Fix custom select display, number input styles, and select dropdown
- **style:** Fix sidebar icons width in closed state
- **style:** Fix mobile sidebar layout
- **style:** Fix inputs height for large screens
- **style:** Ensure responsive layout for permissions grid on mobile
- **styles:** Fix layout, card headers, and settings page headers

### Code Refactoring

- **style:** Rework colors, theme logic, and optimize styles
- **user:** Increase stability and maintainability, improve some UI elements
- **terminal:** Refactor terminal resize handling
- **exec:** Refactor exec routes
- **container:** Split routes in the container module

### Performance Improvements

- **core:** Add auto reload page on CSRF errors
- **core:** Switch to Alpine base image
- **ci:** Reduce production image size

### Other Changes

- **settings:** Adapt settings page for mobile

Feedback, issues, and contributions are welcome.