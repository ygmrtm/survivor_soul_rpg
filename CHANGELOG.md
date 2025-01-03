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
---
## [1.0.2] - 2024-12-04
- Update python-app.yml
- Update CHANGELOG for version 1.0.2
- Merge 66550d740fea0fa5b93ea5a05e77a1bc41072a8f into 14b77d30366ba02295ab2014d8a7bfc7c1f39f90
- feat: Execute Adventure 
- dummy execution
- style: CreateChallenge Button
- [x]  style: Footer w/exit
- [x]  style: CreateChallenge Button
---

## [1.0.3] - 2024-12-17
Merge cef44231c9cb5d6d86044341478260c60609bba2 into ea8e00526c7fa74aeaf98368d2077614624649bb

feat: Execute Adventure

- [x]  feat: Execute Adventure
    - [x]  system of fight
    - [x]  consider negotiate
    - [x]  reward system
    - [x]  Logging in paragraphs

Update CHANGELOG for version 1.0.2

Update python-app.yml
Update CHANGELOG for version 1.0.2
---

## [1.0.4] - 2024-12-17
Merge aa220b3811c1d1fa13082bea65d9126a7f29847c into 873f008d14a1466a14f07bfe214dc102f800689b

Merge pull request #8 from ygmrtm/feat_underworld

[CODE-41] Feat underworld
feat: Tribute System for Challenges

Merge pull request #7 from ygmrtm/fix_ui-do-not-refresh-the-next-adventure

[CODE-41] Fix UI do not refresh the next adventure
fix: After executing an Adventure, the UI do not refresh the next Adventure

- [x]  fix: [Issue](https://github.com/ygmrtm/survivor_soul_rpg/issues/3)
---

## [1.0.5] - 2024-12-26
Merge 8d57e1c19bb4b016525347b686d1e79bf1a2a022 into 34f6001bf25e15dc4a87364a1cef11fbd678d528

feat: afterlife’s Adventure

fix: respawn

fix: adventure log

Merge pull request #13 from ygmrtm/feat_executeChagenge

[CODE-41] Feat execute challenge to underworld
---

## [1.0.6] - 2024-12-26
Merge d029ed4e561023195e73d6b8e0d226ef659a9368 into cca74683e33f612eeb9ccaa2d78d20d6ecbae955

Update CHANGELOG for version 1.0.5

Merge 8d57e1c19bb4b016525347b686d1e79bf1a2a022 into 34f6001bf25e15dc4a87364a1cef11fbd678d528

feat: afterlife’s Adventure (punishment)

- [x]  feat: afterlife’s Adventure
    - [x]  Create **Underworld Training 101** for *deadpeople*
    - [x]  Execute **101**
    - [x]  Resting/Dying Characters
    - [x]  Enable Punishment

feat: afterlife’s Adventure
---

## [1.0.7] - 2025-01-03
Merge branch 'feat_abilities' into main
Merge pull request #18 from ygmrtm/feat_stencilintegration

[CODE-41] Feat stencilintegration to abilities branch
Merge pull request #17 from ygmrtm/feat_bikeIntegration

[CODE-41] Feat bike integration to abilities branch
Merge pull request #16 from ygmrtm/feat_codingIntegration

[CODE-41] Feat coding integration merge to abilities branch
feat: Integration with **Stencil**

- [ ]  feat:Update abilities (like habits)
    - [x]  Integration with **Code**
    - [x]  Integration with **Stencil**
    - [x]  Integration with **Bike**
    - [ ]  Integration with **Epics**
    - [x]  Consider not punishment if status Stand-by
---

