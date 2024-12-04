# Survivor Soul RPG Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2024-11-13
### Added
- Initial release of Survivor Soul RPG.
- Flask microservices architecture with endpoints for Notion and Todoist integrations.
- Landing page with Lovecraftian theme displaying character cards in a grid.
- Basic structure for the following endpoints:
  - **Notion API**: `getAllCharacters`, `updateCharacter`, `filterByDeepLevel`
  - **Adventure Core**: `createAdventure`, `executeAdventure`, `createChallenge`, `getChallengesByDateRange`
  - **Todoist API**: `createTodoistTask`
- Integration with **Notion API** for character data.
- Integration with **Todoist SDK** for creating daily tasks and challenges.
- Error handling with custom 404 and 500 error pages.
- Global logging system with log levels (`debug`, `info`, `warn`, `error`).
- Docker-based deployment configuration.
- CI/CD setup with GitHub Actions for automated testing and deployment.
- Comprehensive README with project overview, setup instructions, and usage details.

### Changed
- N/A

### Removed
- N/A

---

## [1.0.1] - 2024-12-03
- Merge 489595feb3cfdde96c2b2246994c567f75649f45 into 2b862feb194aa5718c41237822e3d654869308de
- Update CHANGELOG for version
- Update python-app.yml

---## [1.0.2] - 2024-12-04
Merge 66550d740fea0fa5b93ea5a05e77a1bc41072a8f into 14b77d30366ba02295ab2014d8a7bfc7c1f39f90

feat: Execute Adventure

dummy execution

style: CreateChallenge Button

- [x]  style: Footer w/exit
- [x]  style: CreateChallenge Button

Update CHANGELOG for version

Merge 489595feb3cfdde96c2b2246994c567f75649f45 into 2b862feb194aa5718c41237822e3d654869308de
---
## [1.0.2] - 2024-12-04
Update python-app.yml
Update CHANGELOG for version 1.0.2

Merge 66550d740fea0fa5b93ea5a05e77a1bc41072a8f into 14b77d30366ba02295ab2014d8a7bfc7c1f39f90

feat: Execute Adventure

dummy execution

style: CreateChallenge Button

- [x]  style: Footer w/exit
- [x]  style: CreateChallenge Button
---

